#!/usr/bin/env python3
'''
SCRIPT 02:
Script for postprocessing the recognized dictionary text.
Systematic OCR-errors are corrected automatically.

Input: Finereader-Output in HTML
Output: postprocessed text in HTML

Used package:
    re (see: https://docs.python.org/3/library/re.html)
'''

# === Imports ===

import re
import S_01_helpers as helpers

# === Parameters ===

html_file = "kluge_L_FR_output.html"

# === Functions ===

def correct_arrows(html):
    '''Corrects incorrectly recognized arrows.'''
    
    # Replacing &nbsp; (no-break space) with regulare whitespace
    html = re.sub(r'&nbsp;', r' ', html) 
    
    # Variants of misrecognized arrow as " / " 
    html = re.sub(r'\/\'', r'↗', html) 
    html = re.sub(r'\s\/', r' ↗', html)  
    html = re.sub(r'(<span[^>]+>)/', r'\1↗', html)      
   
    # Misrecognized arrow as bracket
    html = re.sub(r'(\(|{)/', r'(↗', html) 
    
    # Variants of misrecognized arrow as s or S; 
    html = re.sub(r'(\s|\()(s|S)\s(?!(mobile|</span><span class="font\d" style="font-style:italic;">mobile))', r' ↗', html) 
    html = re.sub(r'(<span[^>]+>)(s|S)\s(?!mobile)', r'\1↗', html) 
    html = re.sub(r'(<span class="font\d" style="font-style:italic;">)S(?![fmng])', r'\1↗', html) 
    html = re.sub(r'(<span class="font\d" style="font-style:italic;">[^<]+)s([A-Z][^<]+</span>)', r'\1↗\2', html) 
    html = re.sub(r'(<span class="font\d" style="font-style:italic;">[^<]*)S([A-Z]([^<]|<sup>[^<]</sup>)+</span>)', r'\1↗\2', html)  
    
    # Misrecognized arrow as Z
    html = re.sub(r'(<span class="font\d" style="font-style:italic;">)Z', r'\1↗', html)     
    
    # Deletes whitespace behind the arrow
    html = re.sub(r'↗\s', r'↗', html)   # entfernt Leerzeichen hinter ↗
    
    return html


def correct_punctuation(html):
    '''Corrects quotation marks which surround meaning information.'''
    
    html = re.sub("\'", r'‘', html)  
    return html


def correct_latin(html):
    '''Replaces "1." with the correct language abbreviation "l." in front of Latin word forms.'''
    
    html = re.sub(r'1(. </span><span class="font\d" style="font-style:italic;">)', r'l\1', html)
    return html


def correct_bib(html):
    '''Corrects frequent errors in the bibliography section of the entries.'''
    
    html = re.sub("EWN1", "EWNl", html)
    html = re.sub("EWNl3", "EWNl 3", html)
    html = re.sub("b;", "f.;", html)
    html = re.sub("E;", "f.;", html)
    html = re.sub("Í;", "f.;", html)
    return html


def correct_missingWS(html):
    '''Adds missing whitespace behind the gender specification "f." if it's printed in italics and it's followed by meaning information in a new font style.''' 
    
    html = re.sub(r'(f.\s?</span><span class="font5">\s?‘)', r' \1', html)
    return html

# === Coordinating function ===

def main():
    print("--- 02_correct_html.py running")
    html = helpers.read_file(html_file)
    html = correct_arrows(html)
    html = correct_punctuation(html)
    html = correct_latin(html)
    html = correct_bib(html)
    html = correct_missingWS(html)
    helpers.save_file(html, "Kluge_L_FR_postprocessed.html")
    print("... done!")
    

main()