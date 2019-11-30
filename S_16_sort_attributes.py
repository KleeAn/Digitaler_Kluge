#!/usr/bin/env python3
'''
SCRIPT 16:
Script for correcting the order of attributes which are orderd alphabetically by ElementTree.

Used package:
    re (see: https://docs.python.org/3/library/re.html)
'''

# === Imports ===

import re
import S_01_helpers as helpers



# === Functions ===
    
def sort_attributes(tei):
    ''' Corrects the order of attributes which are orderd alphabetically by ElementTree.'''
    
    # entry
    tei = re.sub(r'(<entry)(\stype="[^"]+")(\sxml:id="[^"]+")(\sxml:lang="de">)', r'\1\3\2\4', tei)
    # div 
    tei = re.sub(r'(<div)(\stype="section")(\sxml:id="\w")', r'\1\3\2', tei)
    # gram
    tei = re.sub(r'(<gram)(\sexpand="[^"]+")(\stype="[^"]+")', r'\1\3\2', tei)
    # date 
    tei = re.sub(r'(<date)(\sfrom="\d+")(\sto="\d+")(\stype="[^"]+")', r'\1\4\2\3', tei)
    # usg
    tei = re.sub(r'(<usg)(\sexpand="[^"]+")(\stype="[^"]+")', r'\1\3\2', tei)
    tei = re.sub(r'(<usg)(\sana="[^"]+")(\stype="time")', r'\1\3\2', tei)
    # ref
    tei = re.sub(r'(<ref)(\starget="[^"]+")(\stype="entry")', r'\1\3\2', tei)
    
    return tei
           

# === Coordinating function ===

def main(tei):
    print("--- 16_sort_attributes.py running")
    tei = sort_attributes(tei)
    print("... done!")
    return tei