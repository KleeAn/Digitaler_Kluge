#!/usr/bin/env python3
'''
SCRIPT 07:
Script for tagging the language abbreviations.
Saves language abbreviations and corresponding expansions into CSV ('languages.csv').
CSV has to be updated with normed language tags manually. Updated version is used as 'languages_norm.csv' in script 15.

Used packages:
    re (see: https://docs.python.org/3/library/re.html)
    pandas (see: https://pandas.pydata.org/pandas-docs/stable/)
'''

# === Imports ===

import re
import pandas as pd
import S_01_helpers as helpers


# === Functions ===

def create_lang_dict(langfile):
    ''' Takes list of language abbreviations as TXT file ('langfile') and writes the information into two dictionaries:
        - lang_dict: contains abbreviations and expansions as in langfile
        - lang_dict_cap: abbreviations with beginning capital letter
    '''
    
    txt = helpers.read_file(langfile)

    lang_dict = {}
    lines = txt.split("\n")
    
    for line in lines:
        values = line.split(" = ")
        lang_dict[values[0]] = values[1]
    
    # creating lang_dict_cap
    lang_dict_cap= {}
    for lang in lang_dict.keys():
        lang_dict_cap[lang.capitalize()] = lang_dict[lang]
    
    return lang_dict, lang_dict_cap

    
def save_lang_dict(langfile):
    '''Saves dictionary with language abbreviations and expansions as CSV file.'''

    lang_dict, lang_dict_cap = create_lang_dict(langfile)
    lang_df = pd.DataFrame.from_dict(lang_dict, orient = 'index', columns = ['expand'])
    lang_df_cap = pd.DataFrame.from_dict(lang_dict_cap, orient = 'index', columns = ['expand'])

    lang_df.to_csv('languages.csv', sep='\t', encoding="utf-8")
    lang_df_cap.to_csv('languages_cap.csv', sep='\t', encoding="utf-8")


    
def helper_mark_lang(dict, tei):
    ''' Marks language abbreviations using the passed dictionary with abbreviations and corresponding expansions.'''
   
    for lang in dict:
        # language acronym with following whitespace
        tei = tei.replace(' ' + lang + ' ', ' <lang expand="'+ dict[lang] + '">' + lang + ' </lang>') 
        tei = tei.replace('<hi rendition="font5">' + lang + ' ', '<hi rendition="font5"><lang expand="'+ dict[lang] + '">' + lang + ' </lang>')
        # following </hi>
        tei = tei.replace(' ' + lang + '</hi>', ' <lang expand="'+ dict[lang] + '">' + lang + '</lang></hi>') 
        tei = tei.replace('<hi rendition="font5">' + lang + '</hi>', '<hi rendition="font5"><lang expand="'+ dict[lang] + '">' + lang + '</lang></hi>')
        # language acronym in '()'
        tei = tei.replace('(' + lang + ')', '(<lang expand="'+ dict[lang] + '">' + lang + '</lang>)')
        tei = tei.replace('(' + lang , '(<lang expand="'+ dict[lang] + '">' + lang + '</lang>')
        # with hyphen
        tei = tei.replace('(' + lang + '-)', '(<lang expand="'+ dict[lang] + '">' + lang + '-</lang>)')
    
    return tei


def mark_lang(tei, langfile):
    '''Annotates language abbreviations.'''

    # special cases: bipartide acronyms
    tei = tei.replace('ig. (w./oeur.)', '<lang expand="ig., westeuropäisch und osteuropäisch">ig. (w./oeur.)</lang>')
    tei = tei.replace('nnorw. (bokmäl)', '<lang expand="neunorwegisch (bokmäl)">nnorw. (bokmäl)</lang>')
    tei = tei.replace('nnorw. (nynorsk)', '<lang expand="neunorwegisch (nynorsk)">nnorw. (nynorsk)</lang>')
    tei = tei.replace('toch. A', '<lang expand="tocharisch A">toch. A</lang>')
    tei = tei.replace('toch. B', '<lang expand="tocharisch B">toch. B</lang>')
    
    lang_dict, lang_dict_cap = create_lang_dict(langfile)
    
    tei = helper_mark_lang(lang_dict, tei)
    tei = helper_mark_lang(lang_dict_cap, tei)   
    
    return tei


def delete_lang_bibl(tei):
    '''Deletes <lang> in bibliography section.'''
    
    tei = re.sub(r'(?P<before><bibl>[^<]+(<hi[^<]+</hi>[^<]+)?)<lang expand="[^"]+">(?P<between>[^<]+)</lang>(?P<after>(<hi[^<]+</hi>[^<]+)?.*?</bibl>)', r'\g<before>\g<between>\g<after>', tei)
    return tei


def delete_hi_lang(tei):
    ''' Deletes <hi>-tags around <lang>. '''
    
    tei = re.sub(r'<hi rendition="font(4|5)">(?P<keep>([^<]*?<def>[^<]+</def>)*(|[^<]+)(<lang[^<]+</lang>[^>]*?)*)</hi>', r'\g<keep>', tei)
    # case: <lang> behind <usg> in entry head
    tei = re.sub(r'<hi rend="italics">(?P<keep>(<usg[^<]+</usg>\s){,2}<lang[^<]+</lang>\s?)</hi>', r'\g<keep>', tei)
    # case: <lang> behind date information in entry head
    tei = re.sub(r'<hi rendition="font5">(?P<keep>\s?\(<usg.+?</usg>\)[^<]+<lang[^<]+</lang>\s?)</hi>', r'\g<keep>', tei)

    return tei

def move_lang_usg(tei):
    '''Moves <lang> into <usg> when language is mentioned as addition to lexical information'''
    tei = re.sub(r'(</usg>)(\s*<lang expand[^<]+</lang>)', r'\2\1', tei)
    return tei

# === Coordinating function ===

def main(tei, langfile):
    print("--- 07_mark_lang.py running")
    tei = mark_lang(tei, langfile)
    save_lang_dict(langfile)
    tei = delete_lang_bibl(tei)
    tei = delete_hi_lang(tei)
    tei = move_lang_usg(tei)
    print("... done!")
    return tei
    
