#!/usr/bin/env python3
'''
SCRIPT 08:
Script for tagging information in the etymological section (grammatical information and word forms).

Used package:
    re (see: https://docs.python.org/3/library/re.html)
'''

# === Imports ===

import re
import S_01_helpers as helpers

# === Functions ===

def seperate_hi_italics(tei):
    '''Splits the contant of <hi rend="italics"> when separated by commas.'''
    
    n = 0
    for n in range (0,5):
        tei = re.sub(r'(<hi rend="italics">[^<^,]+)(,)([^<]+</hi>)', r'\1</hi>\2<hi rend="italics">\3', tei)
        n =+ 1
    return tei


def mark_pos_etym(tei, pos_csv):
    ''' Annotates grammatical information in the etymological section.'''

    data_wortarten = helpers.read_csv(pos_csv, 'abbr')
    
    pattern = '(<hi rend="italics">)([^<]+)(</hi>)'
    tei = helpers.mark_pattern_df(pattern, data_wortarten, " ", tei)  
    
    # moving <hi> in front of <gramGrp>
    tei = re.sub(r'(?P<begin><hi rend="italics">)(?P<keep>[^<]*)(?P<gram><gramGrp>(<gram[^<]+</gram>\/?)+</gramGrp>[^<]*)(?P<end></hi>)', r'\g<begin>\g<keep>\g<end>\g<gram>', tei)
    
    # deleting empty <hi>-elements
    tei = re.sub(r'<hi rend="italics">\s*</hi>', r'', tei)
    
    # annotating grammatical person and number and moving into <gramGrp>
    tei = re.sub(r'(\d\.\s)(<hi rend="italics">)(<gramGrp>)(<gram [^>]+>(Sg.|Pl.)</gram>)', r'\2\3<gram type="person">\1</gram>\4', tei)
    
    # merging two following <gramGrp>s 
    tei = re.sub(r'</gramGrp>\s{1,2}<gramGrp>', r'', tei)
    
    return tei

def move_hi_from_gram(tei):
    '''Moves <gramGrp> out of <hi rend=italics>.'''
    
    ### different cases according to content of <hi>:
    
    # case 1: word form + gramGrp
    tei = re.sub(r'(<hi rend="italics">[^<]+)(<gramGrp>(<gram[^<]+</gram>\/?){1,3}</gramGrp>\s{0,2})(</hi>)', r'\1\4\2', tei)
    # case 2: word form + gramGrp + 'u.ä.' or 'Pl.'
    tei = re.sub(r'(<hi rend="italics">[^<]+)(<gramGrp>(<gram[^<]+</gram>\/?){1,3}</gramGrp>\s{1,2}(u\.ä|Pl\.))(</hi>)', r'\1\5\2', tei)
    # case 3: gramGrp + word form
    tei = re.sub(r'(<hi rend="italics">)\s?(<gramGrp>(<gram[^<]+</gram>){1,3}</gramGrp>)([^<]+</hi>)', r'\2\1\4', tei)
    # case 4: only gramGroup in <hi>
    tei = re.sub(r'(<hi rend="italics">)(<gramGrp>(<gram[^<]+</gram>){1,3}</gramGrp>)(</hi>)', r'\2', tei)
    
    return tei


def mark_orth(tei):
    '''Marks word forms (remaining content of <hi rend="italics">) with <orth>.'''
   
    tei = re.sub(r'((?<!<orth>)<hi rend="italics">[^<]+</hi>)', r'<orth>\1</orth>', tei)
    
    # exception: no <orth> in case of references
    tei = re.sub(r'(<ref type="entry">)<orth>(<hi rend="italics">[^>]+</hi>)</orth>(</ref>)', r'\1\2\3', tei)
    
    return tei


def mark_form(tei):
    ''' Inserting '<form xml:lang="xxx">' around <orth> or <orth> + following <gramGrp>.'''
    
    # <orth> + <gramGrp>
    tei = re.sub(r'(<orth><hi rend="italics">[^<]+</hi></orth><gramGrp>(<gram[^<]+</gram>\/?)*</gramGrp>)', r'<form xml:lang="xxx">\1</form>', tei)
    # <lang> in front of <orth>
    tei = re.sub(r'(<lang[^<]+</lang>[^<]*)(<orth><hi rend="italics">[^<]+</hi></orth>)', r'\1<form xml:lang="xxx">\2</form>', tei)
    # text in front of <orth>
    tei = re.sub(r'([^<^>]+)(<orth><hi rend="italics">[^<]+</hi></orth>)', r'\1<form xml:lang="xxx">\2</form>', tei)
    # </hi> oder </sense> in front of <orth>
    tei = re.sub(r'(</hi>|</sense>)(<orth><hi rend="italics">[^<]+</hi></orth>)', r'\1<form xml:lang="xxx">\2</form>', tei)
    # <lang> or ',' + <gramGrp> + <orth>
    tei = re.sub(r'(</lang>|,)(<gramGrp>(<gram [^<]+</gram>)*</gramGrp><orth><hi rend="italics">[^<]+</hi></orth>)', r'\1<form xml:lang="xxx">\2</form>', tei)
    
    # deleting empty <orth>-elements
    tei = re.sub(r'<orth><hi rend="italics">\s?</hi></orth>', r'', tei)
    
    return tei


def mark_cit(tei):
    '''Inserts '<cit type="etymologicalForm">' around <form> + possibly preceding <lang>.'''
    
    ### deleting whitespace between elements
    tei = re.sub(r'</lang>\s{1,2}<form', r'</lang><form', tei)
    tei = re.sub(r'</form>\s{1,2}<def>', r'</form><def>', tei)
    
    ### inserting <cit> + <mark/> (in order to prevent the future finding of already tagged cases) 
    
    # case 1a: lang + form (1. orth, 2. gramGrp) + def
    tei = re.sub(r'(<lang[^<]+</lang>([^<]+)?)(<form[^>]+><orth><hi[^<]+</hi></orth>(<gramGrp>(<gram [^<]+</gram>)*</gramGrp>)?</form>\s?<def>[^<]+</def>(,\s<gramGrp>(<gram [^<]+</gram>)*</gramGrp>\s<def>[^<]+</def>)?)', r'<cit type="etymologicalForm">\1<mark/>\3</cit>', tei)
    # case 1b: lang + form (1. gramGrp, 2. orth) + def
    tei = re.sub(r'(<lang[^<]+</lang>([^<]+)?)(<form[^>]+><gramGrp>(<gram [^<]+</gram>)*</gramGrp><orth><hi[^<]+</hi></orth></form>\s?<def>[^<]+</def>)', r'<cit type="etymologicalForm">\1<mark/>\3</cit>', tei)
    # case 2a: lang + form (1. orth, 2. gramGrp)
    tei = re.sub(r'((?<!>)(<lang[^<]+</lang>)+)(<form[^>]+><orth><hi[^<]+</hi></orth>(<gramGrp>(<gram [^<]+</gram>)*</gramGrp>)?</form>)', r'<cit type="etymologicalForm">\1<mark/>\3</cit>', tei)
    # case 2b: </hi> between lang and <form> 
    tei = re.sub(r'(?<!>)(<lang[^<]+</lang>([^<]+)?)(</hi>)(<form[^>]+><orth><hi[^<]+</hi></orth>(<gramGrp>(<gram [^<]+</gram>)*</gramGrp>)?</form>)', r'\3<cit type="etymologicalForm">\1<mark/>\4</cit>', tei)
    # case 2c: lang + form (1. gramGrp, 2. orth)
    tei = re.sub(r'((?<!>)<lang[^<]+</lang>([^<]+)?)(<form[^>]+><gramGrp>(<gram [^<]+</gram>)*</gramGrp><orth><hi[^<]+</hi></orth></form>)', r'<cit type="etymologicalForm">\1<mark/>\3</cit>', tei)
    # case 3: lang + form (gram seperated by "/")
    tei = re.sub(r'(<lang[^<]+</lang>[^<]*<form[^>]+><orth([^<]|<hi[^<]+</hi>)+</orth><gramGrp><gram [^<]+</gram>(/<gram[^<]+</gram>)+</gramGrp></form>)', r'<cit type="etymologicalForm">\1<mark/></cit>', tei)
    
    ### move variants (several belonging forms) in one single <cit>
    
    # cit is followed by <form> (and possibly) <def> 
    tei = re.sub(r'(</cit>)((\s?,<form[^>]+><orth><hi[^<]+</hi></orth>(<gramGrp>(<gram [^<]+</gram>\/?)*</gramGrp>)?</form>)+(\s?<def>[^<]+</def>)?)', r'\2\1',tei)
    # case: order: 1. gramGrp, 2. orth
    tei = re.sub(r'(</cit>)((\s?,<form[^>]+><gramGrp>(<gram [^<]+</gram>)*</gramGrp><orth><hi[^<]+</hi></orth></form>)+(\s?<def>[^<]+</def>)?)', r'\2\1',tei)
    # special case: variant in '()' + gramGrp (optional) + def (optional)
    tei = re.sub(r'(</cit>\s?)(\(oder\s)(<form[^>]+><orth><hi[^<]+</hi></orth></form>\)(\s?<gramGrp>(<gram [^<]+</gram>)+</gramGrp>)?(\s?<def>[^<]+</def>)?)', r'\2<mark/>\3\1', tei)
    
    
    ### inserting <cit> - remaining cases
   
    # case 4a:  text + form + def (optional)
    tei = re.sub(r'((?<![,>])<form xml:lang[^>]+><orth><hi[^<]+</hi></orth>(\s?<gramGrp>(<gram [^<]+</gram>)+</gramGrp>)?</form>(<def>[^<]+</def>)?)', r'<cit type="etymologicalForm">\1</cit>', tei)
    # case 4b: </hi> in front of form
    tei = re.sub(r'(</hi>)(<form xml:lang[^>]+><orth><hi[^<]+</hi></orth>(\s?<gramGrp>(<gram [^<]+</gram>)+</gramGrp>)?</form>(<def>[^<]+</def>)?)', r'\1<cit type="etymologicalForm">\2</cit>', tei)
    
    # case 5: enumeration of <form>s (which aren't variants)
    n = 0
    for n in range(0,5):
        tei = re.sub(r'(</cit>\s?,)((<form[^>]+><orth><hi[^<]+</hi></orth>(<gramGrp>(<gram [^<]+</gram>)*</gramGrp>)?</form>)+(\s?<def>[^<]+</def>)?)', r'\1<cit type="etymologicalForm">\2</cit>', tei)
        n =+1
        
    # delete <mark/>
    tei = tei.replace('<mark/>', '')
    
    return tei


def mark_variants(tei):
    '''Adds attribute type="variant" to <form>-elements that are variants (several <form>-elements in one <cit>).'''

    matches = re.finditer('(?P<begin><cit type="etymologicalForm"><lang[^<]+</lang>)(?P<form>(<form[^<]+\s?(<orth><hi[^<]+</hi></orth>)?(<gramGrp>(<gram [^<]+</gram>)+</gramGrp>)?(<orth><hi[^<]+</hi></orth>)?</form>\,?)+)(?P<end>(<def>[^<]+</def>)?</cit>)', tei)
    for match in matches:
        if match[0].count('<form') > 1:
            repl = re.sub(r'(<form)', r'\1 type="variant"', match.group('form'))  
            replaceStr = match.group('begin') + repl + match.group('end')
            tei = tei.replace(match[0], replaceStr)
    
    return tei


def mark_cit_relatedForm(tei):
    '''Inserts '<cit type="related"> around sublemmata in the etymological section.'''

    ### step 1: mask sublemmta in entry head by replacing the attribute value

    matches = re.finditer('<form type="lemmaGroup"><form type="lemma"><orth>[^<]+(<hi[^<]+</hi>)?</orth></form>(\([^\)]+\)\s?)?\s?<gramGrp>(<gram [^<]+</gram>)*</gramGrp></form>(\s\([^\)]+\))?(,\s<form type="sublemma">)?', tei)
    for match in matches:
        repl = re.sub('sublemma', 'placeholder', match[0])
        tei = tei.replace(match[0], repl)
    
    ### step 2: insert <cit>
    tei = re.sub(r'(<form type="sublemma"><orth>[^<]+(<hi[^<]+</hi>)?</orth></form>(\s?<gramGrp>(<gram[^<]+</gram>)+</gramGrp>)?(\s?<def[^<]+</def>)?)', r'<cit type="relatedForm">\1</cit>', tei)
    # sublemma is reference:
    tei = re.sub(r'(<form type="sublemma"><orth><xr><lbl>↗</lbl><ref type="entry">[^<]+(<hi[^<]+</hi>)?</ref></xr></orth></form>)', r'<cit type="relatedForm">\1</cit>', tei)
    tei = re.sub(r'(<form type="sublemma"><orth><xr><lbl>↗</lbl><ref type="entry"><hi[^<]+(<hi[^<]+</hi>)?</hi></ref></xr></orth></form>)', r'<cit type="relatedForm">\1</cit>', tei)
    
    ### step 3: undo masking
    tei = tei.replace('placeholder', 'sublemma')
    
    return tei
    

# === Coordinating function ===

def main(tei, pos_csv):
    print("--- 08_mark_etym.py running")
    tei = seperate_hi_italics(tei)
    tei = mark_pos_etym(tei, pos_csv)
    tei = move_hi_from_gram(tei)
    tei = mark_orth(tei)
    tei = mark_form(tei)
    tei = mark_cit(tei)
    tei = mark_variants(tei)
    tei = mark_cit_relatedForm(tei)
    print("... done!")
    return tei
    
