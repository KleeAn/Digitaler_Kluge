#!/usr/bin/env python3
'''
SCRIPT 14:
Script for turning the Finereader-output of chapter "Abkürzungen der Zeitschriften und Reihen" (TXT file) into XML-TEI and assigning xml:ids to each bibliographical entry. 

Input: chapter "Abkürzungen der Zeitschriften und Reihen" as TXT file
Output: chapter as XML-TEI file

Used package:
    re (see: https://docs.python.org/3/library/re.html)
'''

# === Imports ===

import re
import S_01_helpers as helpers


# === Functions ===

def mark_head(txt):
    '''Marks first line with <head>.'''
    
    lines = txt.split("\n")
    head = '<head>' + lines[0] + '</head>'
    txt = re.sub(lines[0], head, txt)
    
    return txt


def mark_title(txt):
    ''' Annotates the title.'''
    txt = re.sub(r'<bibl>([^\u0009]+)\u0009([^<]+)</bibl>', r'<bibl><title type="short">\1</title><title type="main"> \2</title></bibl>', txt)
    return txt


# === Coordinating function ===

def main(periodicals_file, periodicals_header):
    print("--- 14_mark_periodicals_list.py running")
    txt = helpers.read_file(periodicals_file)
    txt = helpers.change_brackets(txt)
    txt = mark_head(txt)
    txt = helpers.mark_listBibl(txt)
    txt = helpers.mark_bibl(txt)
    txt = mark_title(txt)
    txt = helpers.add_bibl_id(txt, 530)
    xml = helpers.transform2xml(txt, periodicals_header)
    helpers.save_file(xml, "periodicals.xml")
    print("... done!")

#main(periodicals_file)