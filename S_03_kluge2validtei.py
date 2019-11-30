#!/usr/bin/env python3
'''
SCRIPT 03:
Script for turning the postprocessed Finereader-output in HTML into valid XML-TEI.
Input: postprocessed Finereader-output in HTML
Output: XML-TEI

Used package:
    re (see: https://docs.python.org/3/library/re.html)
'''

# === Imports ===

import re
import S_01_helpers as helpers

# === Functions ===

def get_body(html):
    ''' Deletes the <html>-tag and <head>-element and returns the <body> as string.'''

    string = str(html)
    body = re.sub(r'<!DOCTYPE(.*?)</head>', r'', string, 0, re.DOTALL)
    body = re.sub(r'</html>', r'', body)
    
    return body

def add_text_element(body):
    '''Adds <text>-tags.'''
    
    text = "<text>" + body + "</text>\n</TEI>"
    return text

def rename_elements(text):
    '''Renames the HTML-tags into corresponding XML-TEI-tags:
       - <span> to <hi>
       - <sup> to <hi rend="superscript">
       - attribute 'class' to 'rendition'
    '''
    text = text.replace(r'<span class', r'<hi rendition')
    text = text.replace(r'</span>', r'</hi>')
    text = text.replace(r'<p class', r'<p rendition')
    text = text.replace(r'<sup>', r'<hi rend="superscript">')
    text = text.replace(r'</sup>', r'</hi>')
    
    return text

    
def merge(text, headerfile):
    '''Merges TEI-Header (passed by headerfile) and text.'''
    
    header = helpers.read_file(headerfile)
    xmltei = header + text
    
    return xmltei


def undo_pretty_printing(xmltei):
    '''Deletes whitespace between elements.'''
    xmltei = xmltei.replace(r'﻿', r'')  
    xmltei = re.sub(r'(?<=>)\s+(?=<)', r'', xmltei)   
    return xmltei


# === Coordinating function ===
    
def main(htmlfile, headerfile):
    print("--- 03_kluge2validtei.py running")
    html = helpers.read_file(htmlfile)
    body = get_body(html)
    text = add_text_element(body)
    text = rename_elements(text)
    xmltei = merge(text, headerfile)
    xmltei = undo_pretty_printing(xmltei)
    #helpers.save_file(xmltei, "kluge_L.xml")
    print("... done!")
    return xmltei
