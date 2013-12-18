#!/usr/bin/env python
'''
mobile devices parser

Version 0.1

by Roy Firestein (roy@firestein.net)


Parse mobile devices audit plugin and export to CSV

'''


import os
import xml.dom.minidom
from optparse import OptionParser


parser = OptionParser()
parser.add_option("-f", "--file",  action="store", type="string", dest="file", help="Nessus file to parse")
parser.add_option("-o", "--output",  action="store", type="string", dest="output", help="output file name")
(menu, args) = parser.parse_args()

devices = {"Android": [], "iPhone": [], "iPad": []}

def main():
    nes_file = menu.file
    report = xml.dom.minidom.parse(nes_file)
    
    for el in report.getElementsByTagName('ReportItem'):
        if el.getAttribute("pluginID") == "60035":
            # find plugin_output element
            output = get_plugin_output(el)
            
            model = get_model(output)
            version = get_version(output)
            user = get_user(output)
            serial = get_serial(output)
            
            item = {"serial": serial, "version": version, "user": user}
            
            if not item in devices[model]:
                devices[model].append(item)
                print "%s\t%s\t%s\t%s" %(model, version, user, serial)
    
    if len(devices['iPhone']) > 0 or len(devices['iPad']) > 0 or len(devices['Android']) > 0:
        save_csv(devices)


def save_csv(devices):
    fh = open(menu.output, "w")
    fh.write("Platform,User,Version,Serial\n")
    
    for d in devices['iPhone']:
        fh.write('"%s","%s","%s","%s"\n' %("iPhone", d['user'], d['version'], d['serial']))
        
    for d in devices['iPad']:
        fh.write('"%s","%s","%s","%s"\n' %("iPad", d['user'], d['version'], d['serial']))
        
    for d in devices['Android']:
        fh.write('"%s","%s","%s","%s"\n' %("Android", d['user'], d['version'], d['serial']))
    
    fh.close()
            

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
    
def get_plugin_output(el):
    a = el.getElementsByTagName("plugin_output")[0]
    return getText(a.childNodes)
    
def get_model(data):
    for line in data.split("\n"):
        if line.startswith("Model"):
            return line.split(" ")[2]
    return None

def get_version(data):
    for line in data.split("\n"):
        if line.startswith("Version"):
            return line.split(" ")[2]
    return None

def get_user(data):
    for line in data.split("\n"):
        if line.startswith("User"):
            return line.split(" ")[2]
    return None

def get_serial(data):
    for line in data.split("\n"):
        if line.startswith("Serial"):
            return line.split(" ")[3]
    return None
    

if __name__ == "__main__":
    main()
