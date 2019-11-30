#!/usr/bin/env python3
'''
SCRIPT 11:
Script for tagging terms.

Used packages:
    re (see: https://docs.python.org/3/library/re.html)
    pandas (see: https://pandas.pydata.org/pandas-docs/stable/)
'''

# === Imports ===

import re
import pandas as pd
import S_01_helpers as helpers


# === Functions ===

def create_term_df(regfile):
    '''Takes list of terms and corresponding sections (in chapter "Terminologie") as TXT file and writes information into a dataframe. Saves dataframe to CSV 'term.csv'.
       Columns:
       - 'term': term as string
       - 'key': every term receives a key (number)
       - 'section': corresponding section in chapter "Terminologie".
       - 'tagging': tagging string
    '''   
    txt = helpers.read_file(regfile)
    
    
    # create dataframe
    df = pd.DataFrame(columns=['term', 'key','section', 'tagging'])
    df.set_index(list(df)[0])  
   
   
    lines = txt.split("\n")
  
    key = 0
        
    for line in lines:
        # lines without digits are deleted
        if not re.search('\d', line):
            lines.remove(line)
        else:
            section = re.search(r'(\d{1,2}\.\d{0,2}(\,\s)?)+', line).group()
            sections = section.split(',')
            term = re.search(r'[^\d^.]+', line).group()
            terms = term.split(',')
            
            for term in terms:
                term = term.strip()  
                key = key + 1
                tagging = '<term key="' + str(key) + '">' + term + '</term>'
                df = df.append({'term': term,'key': key, 'section': sections, 'tagging': tagging}, ignore_index=True)
                
    # save to CSV
    df.to_csv('term.csv', sep='\t', encoding="utf-8")            

    return df
    

def mark_term(tei, regfile):
    '''Annotates terms with <term key=""> by using the function create_term_df() which uses a list of terms ('regfile').'''
    
    term_df = create_term_df(regfile)
    term_list = term_df['term'].tolist()
    
    for term in term_list:
        index = term_df.loc[term_df['term'] == term].index[0]
       
        tei = tei.replace(' ' + term + ' ', ' ' + term_df.loc[index, 'tagging'] + ' ')
        tei = tei.replace(' ' + term + ',', ' ' + term_df.loc[index, 'tagging'] + ',')
        tei = tei.replace(' ' + term + '.', ' ' + term_df.loc[index, 'tagging'] + '.')
        tei = tei.replace('\n' + term + ' ', '\n' + term_df.loc[index, 'tagging'] + ' ')
        tei = tei.replace('\n' + term + ',', '\n' + term_df.loc[index, 'tagging'] + ',')
        
    
    # deleting <term> within <bibl>
    tei = re.sub(r'(<bibl>[^<]*)<term key="\d+">([^<]+)</term>(([^<]|<cit[^>]+><form[^>]+><orth><hi[^<]+</hi></orth></form></cit>)+</bibl>)', r'\1\2\3', tei)

    # deleting <term> within tags 
    tei = re.sub(r'(<[^=]+="[^"^<]*)<term\skey="\d+">([^<]+)</term>([^"^<]*">)', r'\1\2\3', tei)
    
    # deleting <term> within date information
    tei = re.sub(r'(<seg type="dateLabel">[^<]*)<term[^>]+>([^<]+)</term>(([^<]|<def>[^<]+</def>)*</seg>)', r'\1\2\3', tei)
    tei = re.sub(r'(</date>,[^<]+)<term[^>]+>([^<]+)</term>([^<]*</usg>)', r'\1\2\3', tei)
    
    return tei


# === Coordinating function ===    
    
def main(tei, regfile):
    print("--- 11_mark_term.py running")
    tei = mark_term(tei, regfile)
    print("... done!")
    return tei