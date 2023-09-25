import zipfile
import xml.etree.ElementTree as ET
import json
import sys
import os

# Global dictionary to store the parsed content
datago = {}
# Global counter used as an identifier
i = 0

def loadfile():
    """Load the XMind file and extract its XML content."""
    filename = ''
    zip_ref = False
    # Check if a command line argument is provided (name of the XMind file)
    if (len(sys.argv) > 1):
        file = sys.argv[1]
    else:
        # Otherwise, search for the first .xmind file in the current directory
        for root, dirs, files in os.walk("."):
            for filename in files:
                if filename[-6:] == '.xmind':
                    file = filename
                    break

    # If the file is not found
    if not file:
        print('no xmind file found!')
    else:
        # Attempt to open the file as a ZIP archive
        try:
            zip_ref = zipfile.ZipFile(file, 'r')
        except:
            print('file not found!')

    # If the file is a valid ZIP archive, extract 'content.xml'
    if zip_ref:
        try:
            zip_ref.extract('content.xml')
            print('xml extracted')
            return True
        except:
            print('no valid xmind file!')
            return False
    else:
        return False

# Define namespaces for XML parsing
NS = {'xmind': 'urn:xmind:xmap:xmlns:content:2.0', 'svg': 'http://www.w3.org/2000/svg'}

def xmindParse(topic, parent):
    """Parse the XMind XML content and populate the 'datago' dictionary."""
    global i
    id = i
    # Find the title of the topic
    title = topic.find('xmind:title', NS)
    if title is not None:
        obj = {'label' : title.text, 'options' : [], 'parent' : ''}
        children_topics = topic.find('xmind:children/xmind:topics', NS)
        if children_topics is not None:
            for child_topic in children_topics.findall('xmind:topic', NS):
                option = {'option' : child_topic.find('xmind:title', NS).text}
                grand_children = child_topic.find('xmind:children/xmind:topics', NS)
                if grand_children is not None:
                    for grandChild in grand_children.findall('xmind:topic', NS):
                        if grandChild.find('xmind:title', NS).text[:5] == 'FICHE':
                            option['value'] = grandChild.find('xmind:title', NS).text
                        else:
                            i += 1
                            option['value'] = str(i)
                            xmindParse(grandChild, id)
                
                obj['options'].append(option)
        if parent > -1:
            obj['parent'] = str(parent)
        datago[id] = obj

# Main execution
if loadfile():
    try: 
        tree = ET.parse('content.xml')
        root = tree.getroot()
        try:
            xmindParse(root[0][0], -1)
            try:
                # Write the 'datago' dictionary to a JSON file
                with open('datago.json', 'w') as json_file:
                    json.dump(datago, json_file, indent=4, sort_keys=True)
                    print('json file written: datago.json')
            except:
                print('json file could not be written!')
        except:
            print('parsing error')
    except:
        print('xml error!')

    # Remove the extracted XML file
    os.remove('content.xml')
