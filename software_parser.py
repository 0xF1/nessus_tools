#!/usr/bin/env python
'''
Nessus Software Parser

Version 0.1

by Roy Firestein (roy@firestein.net)


Extract Enumerated Installed Software from Nessus reports

'''

import xml.dom.minidom
from optparse import OptionParser


parser = OptionParser()
parser.add_option("-f", "--file",  action="store", type="string", dest="file", help="Nessus file to parse")
parser.add_option("-o", "--output",  action="store", type="string", dest="output", help="output file name")
(menu, args) = parser.parse_args()

report_output = []

def main():
    nes_file = menu.file
    report = xml.dom.minidom.parse(nes_file)
    
    for host in report.getElementsByTagName('ReportHost'):
        
        client = host.getAttribute("name")
        reports = host.childNodes
        
        for el in reports:
            if el.nodeType == el.ELEMENT_NODE and el.getAttribute("pluginID") == "20811":
                
                output = get_plugin_output(el)
                software = get_software(output)
                updates = []
                
                item = {"software": software, "updates": updates, "client": client}
                report_output.append(item)
    
    if len(report_output) > 0:
        save_csv(report_output)


def save_csv(data):
    fh = open(menu.output, "w")
    fh.write("Client,Software,Version,Date Installed\n")
    
    for d in data:
        for i in d['software']:
            if not i is None:
                fh.write('"%s","%s","%s","%s"\n' %(d['client'], i[0], i[1], i[2]))
    
    fh.close()
    print "Done."
            

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
    
def get_plugin_output(el):
    a = el.getElementsByTagName("plugin_output")[0]
    return getText(a.childNodes)

def get_software(data):
    software = []
    lines = data.split("\n")
    lines.pop(0)
    lines.pop(0)
    lines.pop(0)
    for line in lines:
        if line == "":
            break
        software.append(extract_meta(line))
    return software

def extract_meta(data):
    fragments = data.split("[")
    name = fragments[0].strip()
    version = None
    date = None
    for frag in fragments:
        if frag.startswith("version"):
            words = frag.split()
            ver = words[1].split("]")
            version = ver[0]
        if frag.startswith("installed"):
            words = frag.split()
            ver = words[2].split("]")
            date = ver[0]
    if version and date:
        return (name, version, date)

def get_updates(data):
    """ Incomplete"""
    updates = []
    sections = data.split("The following updates")
    lines = sections[1].split("\n")
    lines.pop(0)
    lines.pop(0)
    lines.pop(0)
    for line in lines:
        updates.append(line)
    return updates


if __name__ == "__main__":
    main()
