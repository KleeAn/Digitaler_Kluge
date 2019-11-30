#!/usr/bin/env python3
'''
SCRIPT 04:
Script for creating a CSV file as preparation for the tagging of grammatical (key ='pos') and lexical/stylistical information (key = 'lexic'). 
The resulting CSV has to be completed manually before being used in script 05 by filling the column 'usg' (only for lexical information) and completing the strings in column 'tagging'.
Further it is necessary to modify some of the values (see chapter 6.2.3).

Input: list of abbreviations as TXT file 
Output: CSV file with columns: 'abbr' (abbreviation), 'expand' (expansion), 'usg' (only in case of lexical information), 'tagging' (prepared XML-tagging)

Used packages:
    re (see: https://docs.python.org/3/library/re.html)
    pandas (see: https://pandas.pydata.org/pandas-docs/stable/)
'''

# === Imports ===

import re
import pandas as pd
import S_01_helpers as helpers


# === Functions ===

def create_dataframe(text, key):
    ''' Takes list of abbreviations as TXT file and writes information into a dataframe.
        Depending on the key ('lexic' or 'pos') the dataframe contains an additional column 'usg' and column 'tagging' is filled with a different string.'''
    
    if key == "lexic":
        dataframe = pd.DataFrame(columns=['abbr', 'expand', 'usg', 'tagging'])
    if key == "pos":
        dataframe = pd.DataFrame(columns=['abbr', 'expand', 'tagging'])
    
    lines = text.split("\n")
    
    for line in lines:
        values = line.split(" = ")
        dataframe = dataframe.append({'abbr': values[0], 'expand': values[1]}, ignore_index=True)
        
    if key == "lexic":
        for index, row in dataframe.iterrows():
            dataframe.loc[index]['tagging'] = '<usg type="placeholder" expand="{}">{}</usg>'.format(dataframe.loc[index]['expand'], dataframe.loc[index]['abbr'])
                
    if key == "pos":
        for index, row in dataframe.iterrows():
            dataframe.loc[index]['tagging'] = '<gramGrp><gram type="placeholder" expand="{}">{}</gram></gramGrp>'.format(dataframe.loc[index]['expand'], dataframe.loc[index]['abbr'])
                    
    return dataframe


def save_dataframe(dataframe, key, title):
    """
    Saves the dataframe as CSV file.
    """
    if key == "lexic":
        dataframe.to_csv(title, sep='\t', columns=['abbr', 'expand', 'usg', 'tagging'], encoding="utf-8")
    if key == "pos":
        dataframe.to_csv(title, sep='\t', columns=['abbr', 'expand', 'tagging'], encoding="utf-8")


# === Coordinating function ===

def main(lexis_file, pos_file):
    print("--- 04_create_csv_pos_lexis.py running")
    # create CSV of lexical/stylistic information
    txt = helpers.read_file(lexis_file)
    dataframe = create_dataframe(txt, "lexic")
    save_dataframe(dataframe, "lexic","lexis_tofill.csv")
    # create CSV of grammatical information
    txt = helpers.read_file(pos_file)
    dataframe = create_dataframe(txt, "pos")
    save_dataframe(dataframe, "pos","pos_tofill.csv")
    print("... done!")
