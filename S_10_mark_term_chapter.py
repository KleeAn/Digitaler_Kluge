#!/usr/bin/env python3
'''
SCRIPT 10:
Script for turning the Finereader-output of the chapter "Einführung in die Terminologie" (TXT file) into XML-TEI.
Each section is written into one <div>-element with attribute 'n' containing the section number.
Furthermore terms are annotated.

Input: chapter "Einführung in die Terminologie" as TXT file
Output: chapter as XML-TEI file

Used packages:
    re (see: https://docs.python.org/3/library/re.html)
'''

# === Imports ===

import re
import S_11_mark_term as mark11
import S_01_helpers as helpers

# === Functions ===

def mark_head(txt):
    '''Marks headings.'''
    
    txt = re.sub(r'\n([\w\s\,]+)((?<!\.)\n\d{1,2}\.\d{0,2})', r'\n<head>\1</head>\2', txt)
    txt = re.sub(r'(.*)(\n0.0)', r'<head>\1</head>\2', txt)
    
    return txt


def mark_div(txt):
    '''Inserts <div>-tags with attribute n which contains the section number. Text within each <div> is inclosed by <p>.'''
    
    ### sections
    # opening <div>
    txt = re.sub(r'(<head>[^<]+</head>\n(?P<section>\d{1,2})\.\d{0,2})', r'<div n="\g<section>">\1', txt)
    # closing </div>
    txt = re.sub(r'((?<=\.\n)<div)', r'</div>\1', txt)
    # last closing </div>
    txt = txt + '</div>'
    
    ### subsections 
    txt = re.sub(r'(\n)((?P<section>\d{1,2}\.\d{0,2})(.*))\n', r'\1<div n="\g<section>"><p>\2</p></div>\n', txt)
    txt = re.sub(r'(</div>\n)((?P<section>\d{1,2}\.\d{0,2})(.*))\n', r'\1<div n="\g<section>"><p>\2</p></div>\n', txt)
    # last section
    txt = re.sub(r'(</div>\n)((?P<section>\d{1,2}\.\d{0,2})(.*))</div>', r'\1<div n="\g<section>"><p>\2</p></div></div>', txt)

    return txt

def delete_p(xml):
    '''Deletes <p>-Element in <body>.'''
    
    xml = re.sub(r'(<text><body>)<p>', r'\1', xml)
    xml = re.sub(r'</p>(</body></text>)', r'\1', xml)
    
    return xml


# === Coordinating function ===

def main(termfile, term_header, regfile):
    print("--- 10_mark_term_chapter.py running")
    txt = helpers.read_file(termfile)
    txt = mark_head(txt)
    txt = mark_div(txt)
    xml = helpers.transform2xml(txt, term_header)
    xml = delete_p(xml)
    xml = mark11.mark_term(xml, regfile)
    helpers.save_file(xml, "terminology.xml")
    print("... done!")
    
