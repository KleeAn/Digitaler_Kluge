#!/usr/bin/env python3
'''
SCRIPT 01:
This script contains functions that are called multiple times during the markup process in various scripts.

Used packages:
    re (see: https://docs.python.org/3/library/re.html)
    pandas (see: https://pandas.pydata.org/pandas-docs/stable/)
    ElementTree XML (see: https://docs.python.org/2/library/xml.etree.elementtree.html)
'''

# === Imports ===

import re
import pandas as pd
import xml.etree.ElementTree as ET

# === Functions ===

# --- Reading and Parsing ---

def read_file(file):
    '''Reads file (TXT, HTML, XML) and returns string.'''
    
    with open(file, "r", encoding="utf8") as infile: 
        str = infile.read()
        return str
    
    
def read_csv(csvfile, index):
    '''
    Reads CSV file and returns dataframe with \t as delimiter.
    'index' specifies which column is set as index.
    '''
    data = pd.read_csv(csvfile, delimiter="\t")
    data = data.set_index(index)
    return data


def parse_xml(xml):
    '''Parses string (in XML-structure) into ElementTree object. Returns the root of the XML tree.
       The namespace declaration in the root element is deleted temporarily for reasons of easier handling.
    '''
    
    xml = xml.replace('<TEI xmlns="http://www.tei-c.org/ns/1.0">', '<TEI>')  
    root = ET.fromstring(xml)
    return root


def get_root(file):
    '''Takes XML file and returns ElementTree object.'''

    xml = read_file(file)
    root = parse_xml(xml)
    return root
    
    
# --- Saving ---

def save_file(string, name):
    '''Takes string and writes it into a file with the passed name.'''
    with open(name, "w", encoding="utf8") as outfile: 
        outfile.write(string)


# --- Working with XML ---

def change_brackets(txt):
    '''Replaces angle brackets with guillemets.'''

    txt = re.sub(r'(\s)>(\w+)<(\s|[.,])', r'\1»\2«\3', txt)
    return txt


def transform2xml(txt, headerfile):
    ''' Transforms a string into XML by adding required element tags and a header (contained by headerfile).'''
    
    txt = "<text><body><p>" + txt + "</p></body></text></TEI>"
    header = read_file(headerfile)
    xml = header + txt
    # deletes no-break space
    xml = xml.replace('﻿', '')
    return xml


# --- Searching and replacing ---

def replace_abbr(str, str_tagged, text, match, tei):
    ''' This function is called in mark_abbr_usg_pos(), mark_pattern_df() and split_bibl().
        It replaces a string with its tagging.
        Input:
            - str: string that has to be replaced
            - str_tagged: tagged string
            - match: found text passage 
            - text: part of match containing str (and probably already replaced sections)
            - tei: complete text string
        Output:
            - tei with replacement
            - text with replacement
    '''
    
    text_replaced = text.replace(str, str_tagged)     
    replaceStr = match[1] + text_replaced + match[3]  
    searchStr = match[1] + text + match[3]
    text = text_replaced  
    tei = tei.replace(searchStr, replaceStr)
    return tei, text


def mark_abbr_usg_pos(pattern, csv_wortschatz, csv_wortarten, tei):
    '''
    Searches for pattern in the passed string ('tei') and taggs grammatical and lexical/stylistical information using the passed CSV files.
    Returns the string ('tei') with inserted tagging.
    '''
    
    # read CSV into dataframe
    data_wortschatz = read_csv(csv_wortschatz, 'abbr')
    data_wortarten = read_csv(csv_wortarten, 'abbr')
    
    # getting lists of abbreviations
    abbr_list_wortschatz = data_wortschatz.index.tolist() 
    abbr_list_wortarten = data_wortarten.index.tolist()
    
    regex = re.compile(pattern)
    for match in regex.finditer(tei):
        # text contains abbreviated grammatical and lexical/stylistical information
        text = match[2]      
        
        # splitting the string to separated several information
        strlist = text.split()

        # in case grammatical information is separated by "/"
        for str in strlist:
            if "/" in str:
                sep = str.split("/")
                for item in sep:
                    strlist.append(item)
                
        # searching for and tagging of abbreviations
        for str in strlist:
            for abbr in abbr_list_wortarten:
                if abbr == str or abbr + "," == str:  
                    str_tagged = str.replace(abbr, data_wortarten.loc[abbr, 'tagging'])  
                    tei, text = replace_abbr(str, str_tagged, text, match, tei)
                    # case POS is separated by "/": the generated two <gramGrp>s are merged
                    tei = re.sub(r'</gramGrp>(\s+/)<gramGrp>', r'\1', tei) 
            for abbr in abbr_list_wortschatz:
                if abbr == str or abbr + "," == str:
                    str_tagged = str.replace(abbr, data_wortschatz.loc[abbr, 'tagging'])  
                    tei, text = replace_abbr(str, str_tagged, text, match, tei)
    return tei


def mark_pattern_df(pattern, df, delim, tei):
    '''
    Searches for pattern in the passed string ('tei'), splits the found string using 'delim' as separator and taggs abbreviations using the passed dataframe.
    Returns the string ('tei') with inserted tagging.
    '''
 
    regex = re.compile(pattern)
    # getting list of abbreviations  
    abbr_list = df.index.tolist()
          
    for match in regex.finditer(tei):
        text = match[2]
        strlist = text.split(delim)
        
        for str in strlist:
            for abbr in abbr_list:
                if abbr == str:  
                    str_tagged = str.replace(abbr, df.loc[abbr, 'tagging'])
                    tei, text = replace_abbr(str, str_tagged, text, match, tei)
        
    return tei



def split_bibl(pattern, tei):
    '''
    Searches for pattern in the passed string ('tei'), separates found string using ';' as separator. Adds <bibl>-tag around splitted strings.
    Returns the string ('tei') with inserted tagging.
    '''

    regex = re.compile(pattern)
    for match in regex.finditer(tei):
        text = match[2]
        strlist = text.split(";")
        for str in strlist:
            str_tagged = "<bibl>" + str + "</bibl>"
            tei, text = replace_abbr(str, str_tagged, text, match, tei)
            
    return tei


# --- Tagging of literature and periodicals ---

def mark_listBibl(txt):
    txt = '<listBibl>' + txt + '</listBibl>'
    return txt


def mark_bibl(txt):
    txt = re.sub(r'\n([^\n^<]+)\n', r'\n<bibl>\1</bibl>\n', txt)
    txt = re.sub(r'\n([^\n^<]+)\n', r'\n<bibl>\1</bibl>\n', txt)
    return txt


def add_bibl_id(txt, id):
    '''Assigning xml:ids to <bibl>-elements.
       Beginning with the value specified in parameter 'id' the assigned value is incremented with each found <bibl>-element.
    '''
    root = ET.fromstring(txt)
    
    for bibl in ET.ElementTree(root).iterfind(".//bibl"):
        bibl.set('xml:id', 'B' + str(id))
        id += 1

    txt = ET.tostring(root, encoding='utf-8').decode('utf-8')
    return txt
