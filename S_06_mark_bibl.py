#!/usr/bin/env python3
'''
SCRIPT 06:
Script for tagging the referencing section, bibliographical section and separate cited works.

Used package:
    re (see: https://docs.python.org/3/library/re.html)
'''

# === Imports ===

import re
import S_01_helpers as helpers


# === Functions ===

def mark_refSection(tei):
    '''Inserts <note type='referencingSection'.'''
    
    tei = re.sub(r'(<p(><hi|) rendition="font4")', r'<note type="referencingSection">\1', tei)
    tei = re.sub(r'(<note type="referencingSection">(.*?)</p>)', r'\1</note>', tei)  
    
    return tei

    
def move_hyphen(tei):
    ''' Moves hyphen (beginning of bibliography section) out of <hi>.'''
    
    tei = re.sub(r'(.\s)(-)(\s?)(</hi>)(<hi rendition="font4")', r'\1\4\2\3\5', tei)
    tei = re.sub(r'(?P<hi><hi rendition="font4"([^>]+)?>)(?P<hyphen>\s?-\s)', r'\g<hyphen>\g<hi>', tei)
    
    return tei


def mark_bibl_list(tei):
    ''' Annotates bibliography section with <bibl type='list'> and the including hyphen with <pc unit="bibl">.'''

    ### inserting <bibl type='list'>
    
    # case 1: - introduces bibliography section
    tei = re.sub(r'(?P<hyphen>-)(?P<white>\s?)<hi rendition="font4"([^>]+)?>(?P<bibl>[^<]+)</hi></p>', r'<bibl type="list"><pc unit="bibl">\g<hyphen></pc>\g<white>\g<bibl></bibl></p>', tei)
    
    # case 2a: referencing section contains only bibliography section
    tei = re.sub(r'(?P<before><note type="referencingSection"><p>)<hi rendition="font4" style="font-variant:small-caps;">(?P<bibl>[^<]+)</hi></p>', r'\g<before><bibl type="list">\g<bibl></bibl></p>', tei)
    
    # case 2b: missing typography attribute small:caps 
    tei = re.sub(r'(?P<before><note type="referencingSection">)<p rendition="font4">(?P<bibl>(EWNl|RGA|HWPh|LM|Wortbildung)[^<]+)</p>', r'\g<before><bibl type="list">\g<bibl></bibl>', tei)
        
    # case 3a: additional text in <hi>; with change of typography
    tei = re.sub(r'(?P<before>\.\s)(?P<hyphen>-)(?P<bibl>\s?<hi.*?</hi>)(?P<after></p>)', r'\g<before><bibl type="list"><pc unit="bibl">\g<hyphen></pc>\g<bibl></bibl>\g<after>', tei)
    
    # case 3b: additional text in <hi>; without change of typography
    tei = re.sub(r'(?P<before>\.\s)(?P<hyphen>-)(?P<bibl>.*?)(?P<after></hi></p>)', r'\g<before><bibl type="list"><pc unit="bibl">\g<hyphen></pc>\g<bibl></bibl>\g<after>', tei)

    # case 4: addition in '()' + change of typography
    tei = re.sub(r'(?P<before>(<p>|-\s))(?P<bib><hi rendition="font4"[^>]*>.*?)</p>', r'\g<before><bibl type="list">\g<bib></bibl></p>', tei)
    
    ### inserting <pc unit="bibl">
    tei = re.sub(r'(-)(\s?)(<bibl type="list">)', r'\3<pc unit="bibl">\1</pc>\2', tei)
    
    return tei


def adapt_hi_italics(tei):
    '''Changes <hi rendition="font4"/"font5" style="font-style:italic;"> to <hi rend="italics">.'''
    
    tei = tei.replace(r'<hi rendition="font4" style="font-style:italic;">', r'<hi rend="italics">')
    tei = tei.replace(r'<hi rendition="font5" style="font-style:italic;">', r'<hi rend="italics">')
    
    # move punctuation characters form <hi>
    # ')' + punctuation mark
    tei = re.sub(r'(<hi rend="italics">[^<^\(]+)(\)[.,;]+\s?)(</hi>)', r'\1\3\2', tei)
    # two punctuation characters 
    tei = re.sub(r'(<hi rend="italics">[^<]+)((?<!(\s|\/)[fmn])[.,;]\s?)(</hi>)', r'\1\4\2', tei)
    # one punctuation character unless it's part of gender abbreviation
    tei = re.sub(r'(<hi rend="italics">[^<]+)((?<!(\s|\/)[fmn])[.,;]\s?)(</hi>)', r'\1\4\2', tei)
    # ')'
    tei = re.sub(r'(<hi rend="italics">[^<^\(]+)([\)]+\s?)(</hi>)', r'\1\3\2', tei)
    # '('
    tei = re.sub(r'(<hi rend="italics">)(\()([^<^\)]+\s?</hi>)', r'\2\1\3', tei)
    
    # exceptions: keeping the point in <hi> in case of
    # gender abbreviation
    tei = re.sub(r'(<hi rend="italics">[mfn])(</hi>)(\.)', r'\1\3\2', tei)
    # POS abbreviation
    tei = re.sub(r'(<hi rend="italics">(Vst|Vsw))(</hi>)(\.)', r'\1\4\3', tei)
    # number abbreviation
    tei = re.sub(r'(<hi rend="italics">([^<]+)?(Sg|Pl))(</hi>)(\.)', r'\1\5\4', tei)
    
    return tei


def delete_hi_bibl_list(tei):
    ''' Deletes or moves <hi>-tags in <bibl type="list">.'''
    
    # deleting <hi>
    tei = re.sub(r'(?P<before>(<bibl type="list">)(<pc unit="bibl">.*?</pc>\s)?)<hi rendition[^>]+>(?P<bibl>.*?)</hi>', r'\g<before>\g<bibl>', tei)
   
    n = 0
    for n in range(0,3):
        tei = re.sub(r'(?P<before>(<bibl type="list">)(<pc unit="bibl">.*?</pc>)?(.*?))<hi rendition="font4"([^>]+)?>(?P<bibl>.*?(<hi rend="superscript">\d</hi>)?.*?)</hi>', r'\g<before>\g<bibl>', tei)
        n += 1
    
    # moving </hi> behind </bibl> in front of <bibl>
    tei= re.sub(r'(<bibl type="list">(<pc unit="bibl">-</pc>)?[^<]+</bibl>)(</hi>)', r'\3\1', tei)
    
    return tei


def mark_bibl(tei):
    '''Marking single bibliographical data with <bibl>'''
    
    # with <pc unit="bibl">
    pattern = r'(<bibl type="list"><pc unit="bibl">-</pc>)(.*?)(</bibl>)'
    tei = helpers.split_bibl(pattern, tei)
    
    # without <pc unit="bibl">
    pattern = r'(<bibl type="list">(?!<pc))(.*?)(</bibl>)'
    tei = helpers.split_bibl(pattern, tei)
    
    return tei


def delete_def_bibl(tei):
    ''' Deletes <def>s in <bibl>.'''

    n = 0
    for n in range (0,3):
        tei = re.sub(r'(?P<before><bibl>[^<]+(<hi[^<]+</hi>[^<]+)?)<def>(?P<between>.*?)</def>(?P<after>(<hi[^<]+</hi>[^<]+)?.*?</bibl>)', r'\g<before>\g<between>\g<after>', tei)
        n =+ 1
        
    return tei
           

# === Coordinating function ===

def main(tei):
    print("--- 06_mark_bibl.py running")
    tei = mark_refSection(tei)
    tei = move_hyphen(tei)
    tei = mark_bibl_list(tei)
    tei = adapt_hi_italics(tei)
    tei = delete_hi_bibl_list(tei)
    tei = mark_bibl(tei)
    tei = delete_def_bibl(tei)
    print("... done!")
    return tei
    