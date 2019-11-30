#!/usr/bin/env python3
'''
SCRIPT 09:
Script for tagging the translation section and the addition section.

Used package:
    re (see: https://docs.python.org/3/library/re.html)
'''

# === Imports ===

import re
import pandas as pd
import S_01_helpers as helpers



def mark_note_translation(tei):
    '''Marks translation section by inserting '<note type="translation">'.
       Note: This annotation will be changed into <seg> in S_12.
       Empty <trans/> is inserted as aid to find the element's closing tag in S_12.
    '''
    
    tei = re.sub(r'(Ebenso (<cit type="etymologicalForm"><lang[^<]+</lang>(<form[^<]+<orth><hi[^<]+</hi></orth></form>\,?)+(<def>[^<]+</def>)?</cit>(\,\s)?)+(\.|;))', r'<note type="translation">\1<trans/></note>', tei)
    return tei


def note_translation_variants(tei):
    '''Inserts <cit> around mistaken variants in translation section.'''
    
    matches = re.finditer('<note type="translation">.*?</note>', tei)
    for match in matches:
        if 'form type="variant"' in match[0]:
            repl = match[0].replace('type="variant"', '')  
            repl = re.sub(r'(</form>)(,)(<form)', r'\1</cit>\2<cit type="etymologicalForm">\3', repl)  
            tei = tei.replace(match[0], repl)
        
    return tei

def type_translationEquivalent(tei):
    '''Changes type-attribute of <cit> to "translationEquivalent" within the translation section. '''
    
    matches = re.finditer('<note type="translation">.*?</note>', tei)
    for match in matches:
        repl = match[0].replace('etymologicalForm', 'translationEquivalent')
        tei = tei.replace(match[0], repl)
    return tei


def mark_note_addition(tei):
    '''Annotate section "Weitere Informationen" with <note type="addition">.
       Note: This annotation will be changed into <seg> in S_12.
       Empty <add/> is inserted as aid to find the element's closing tag in S_12.
    '''

    # search for entries
    matches = re.finditer('<entry>.*?</entry>', tei)
    n = 0 
    for match in matches:
        if 'referencingSection' in match[0]:   # a referencing section exists
        
            #case 1: translation section + addition section + bibliographical section
            if '<note type="translation">' in match[0] and '<bibl type="list">' in match[0]:
                if '</note> <bibl' in match[0]:  # dann gibt es kein addition:
                    pass
                else:
                    repl = re.sub(r'(</note>(?!</entry>))', r'\1<note type="addition">', match[0])
                    repl = re.sub(r'(<bibl type="list">)', r'<add/></note>\1', repl)
                    tei = tei.replace(match[0], repl)
                
            # case 2: addition section + bibliographical section
            if '<bibl type="list">' in match[0] and '<note type="translation">' not in match[0]:
                if '<p><bibl type="list">' in match[0] or '<note type="referencingSection"><bibl' in match[0]: # no addition exists
                    pass
                else:
                    repl = re.sub(r'(<note type="referencingSection"><p[^>]*?>)(?!<bibl)', r'\1<note type="addition">', match[0])
                    repl = re.sub(r'(<bibl type="list">)', r'<add/></note>\1', repl)
                    tei = tei.replace(match[0], repl)
                  
            # case 3: translation section + addition section
            if '<note type="translation">' in match[0] and '<bibl type="list">' not in match[0]:
                if '</note></p></note>' in match[0] : # dann keine addition
                    pass
                else:
                    repl = re.sub(r'(</note>(?!</entry>))', r'\1<note type="addition">', match[0])
                    repl = re.sub(r'((?<!</bibl>)(</p>)?</note></entry>)', r'<add/></note>\1', repl)
                    tei = tei.replace(match[0], repl)
            
            # case 4: only addition section
            if '<note type="translation">' not in match[0] and '<bibl type="list">' not in match[0]:
                    repl = re.sub(r'(<note type="referencingSection"><p[^>]*?>)', r'\1<note type="addition">', match[0])
                    repl = re.sub(r'((</p>)?</note></entry>)', r'<add/></note>\1', repl)
                    tei = tei.replace(match[0], repl)
          
    return tei


# === Coordinating function ===

def main(tei):
    print("--- 09_mark_translation_addition.py running")
    tei = mark_note_translation(tei)
    tei = note_translation_variants(tei)
    tei = type_translationEquivalent(tei)
    tei = mark_note_addition(tei)
    print("... done!")
    return tei
