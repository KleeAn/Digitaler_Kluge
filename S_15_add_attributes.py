#!/usr/bin/env python3
'''
SCRIPT 15:
Script for adding attributes using the python package ElementTree XML.

Used package:
    re (see: https://docs.python.org/3/library/re.html)
    pandas (see: https://pandas.pydata.org/pandas-docs/stable/)
    ElementTree XML (see: https://docs.python.org/2/library/xml.etree.elementtree.html)
'''

# === Imports ===

import re
import pandas as pd
import xml.etree.ElementTree as ET
import S_01_helpers as helpers


# === Parameters ===

ns = '{http://www.w3.org/XML/1998/namespace}'
xml = '<?xml version="1.0" encoding="UTF-8"?>\n<?xml-model href="./TEILex0-ODD_kluge.rng" schematypens="http://relaxng.org/ns/structure/1.0" type="application/xml"?>'


# === Functions ===

def entry_add_id(root):
    '''Generates xml:id (consisting of orthographical lemma form and grammatical information) and adds to entries.'''
    
    for entry in ET.ElementTree(root).findall(".//entry"):
        lemma = ''
        pos = ''
        number = ''
    
        for lemmaGroup in entry.findall('./form[@type="lemmaGroup"]'):
            for lemmaform in lemmaGroup.findall('./form[@type="lemma"]'):
                    for orth in lemmaform.findall('orth'):
                        lemma = orth.text
                        lemma = lemma.strip()
                        # deleting all non-alphabetical characters
                        lemma = re.sub("[^\w]+", "", lemma)
                        for hi in orth.findall('hi'):
                            # if lemma is a homograph, number is stored
                            if hi.text:               
                                number = hi.text
            for gramGrp in lemmaGroup.findall('gramGrp'):
                for gram in gramGrp.findall('gram'):
                    pos = pos + gram.text
        id = lemma + number + '.' + pos
        entry.set('xml:id', id)
        
    return root


def entry_add_type_homonymic(root):
    '''Adds type="homonymicEntry" to entries of homographs.'''
    
    for entry in ET.ElementTree(root).findall(".//entry"):
        if re.search('\d', entry.get('xml:id')):    
            entry.set('type', 'homonymicEntry')
    
    return root


def entry_add_xml_lang(root):
    '''Adds attribte xml:lang="de" to every <entry>.'''
    
    for entry in ET.ElementTree(root).findall(".//entry"):
        entry.set('xml:lang', 'de')
    return root


def sense_add_id(root):
    '''Adds xml:id to <sense>-elements.'''
    
    for entry in ET.ElementTree(root).findall(".//entry"):
        for sense in entry.findall('sense'):
            sense.set('xml:id', entry.get('xml:id') + '.sense')
    return root


def date_add_from_to(root):
    '''Adds attributes "from" and "to" to <date>-elements.'''
    
    for date in ET.ElementTree(root).findall(".//usg/date/date"):  
        if date.text:
           if date.text != '-':
                century = re.search('(\d{1,2})', date.text).group()
                if int(century) < 11:
                    begin = '0' + str(int(century)-1) + '00'
                    end = '0' + str(int(century)-1) + '99'
                else:
                    begin = str(int(century)-1) + '00'
                    end = str(int(century)-1) + '99'
                date.set('from', begin)
                date.set('to', end)
    
    return root


def ref_add_target(root):
    '''Adds attribute "target" to <ref>-elements. The value is '#' + the xml:id of the referenced entry. For now there exist only xm:ids of lemmas from section L.
       Other referenced entries get the target-value '#' and have to be completed after the digitizing of the whole dictionary text.
    '''
    
    ### step 1: create dictionary with lemmas and xml:ids from section L
    id_dict = {}
    
    for entry in ET.ElementTree(root).findall(".//entry"):
        id = entry.get('xml:id')
        lemma = id.split('.')[0]
        id_dict[lemma] = id

    ### step 2: searching for <ref>s and inserting target
    for ref in ET.ElementTree(root).findall(".//ref"):
        number = ''
        reflemma = ref.text
        reflemma = reflemma.strip()
        for hi in ref.findall('hi'):
            # lemma is homograph
            if hi.text:               
                 number = hi.text
        reflemma = reflemma + number
        if reflemma in id_dict:
            target = '#' + id_dict[reflemma]
            ref.set('target', target)
        # referenced entries that aren't part of section L    
        else:
            ref.set('target', '#')   
                
    return root


def form_add_xml_lang(root, lang_csv, lang_cap_csv):
    '''Adds attribute xml:lang to <form>-elements in <cit type="etymologicalForm"/"translationEquivalent"> according to values in passed CSV ('lang_csv' and 'lang_cap.csv').'''
    
    lang_df = pd.read_csv(lang_csv, delimiter="\t")
    lang_cap_df = pd.read_csv(lang_cap_csv, delimiter="\t")
    
    abbr_list = lang_df['abbr'].tolist()
    abbr_list_cap = lang_cap_df['abbr'].tolist()

    # in cit[@type="etymologicalForm"]
    for cit in ET.ElementTree(root).findall('.//cit[@type="etymologicalForm"]'):
        for form in cit.findall('form'):
            form.attrib.pop(ns+'lang') 
            # empty string if no language mentioned
            if not cit.find('lang'):
                form.set('xml:lang', '')   
            for lang in cit.findall('lang'):
                language = (lang.text).strip()
                if language in abbr_list:
                    index = lang_df.loc[lang_df['abbr'] == language].index[0]   
                    xml_lang = lang_df.loc[index, 'norm']
                if language in abbr_list_cap:
                    index = lang_df.loc[lang_cap_df['abbr'] == language].index[0]   
                    xml_lang = lang_df.loc[index, 'norm']
                form.set('xml:lang', xml_lang)
                
    # in cit[@type="translationEquivalent"]
    for cit in ET.ElementTree(root).findall('.//cit[@type="translationEquivalent"]'):
        for form in cit.findall('form'):
            form.attrib.pop(ns+'lang')
            for lang in cit.findall('lang'):
                language = (lang.text).strip()
                if language in abbr_list:
                    index = lang_df.loc[lang_df['abbr'] == language].index[0]   
                    xml_lang = lang_df.loc[index, 'norm']
                if language in abbr_list_cap:
                    index = lang_df.loc[lang_cap_df['abbr'] == language].index[0]   
                    xml_lang = lang_df.loc[index, 'norm']
                form.set('xml:lang', xml_lang)
                    
    return root


def get_p_dict(periodicals_xml):
    '''Takes list of periodicals (as XML file) and creates dictionary with short titles and corresponding ids.'''
    
    p_root = helpers.get_root(periodicals_xml)
    p_dict = {}
    
    for bibl in ET.ElementTree(p_root).findall('.//listBibl/bibl'):
        id = bibl.get(ns + 'id')
        for title in bibl.findall('./title[@type="short"]'):
            title = title.text
        p_dict[title] = id
    
    return p_dict

def get_l_short_dict(literature_xml):
    '''Takes list of bibliographical entries (as XML file) and creates dictionary with short titles and corresponding ids.'''
    
    l_root = helpers.get_root(literature_xml)
    l_short_dict = {}
    
    for bibl in ET.ElementTree(l_root).findall('.//listBibl/bibl'):
        for short in bibl.findall('./title[@type="short"]'):
            short = short.text.strip()
            id = bibl.get(ns + 'id')
            l_short_dict[short] = id
    
    return l_short_dict


def get_FS_dict(literature_xml):
    '''Takes list of bibliographical entries (as XML file) and creates dictionary with short titles of Festschriften and Gedenkschriften and corresponding ids.'''
    
    l_root = helpers.get_root(literature_xml)
    fs_dict = {}
    
    for bibl in ET.ElementTree(l_root).findall('.//listBibl/bibl'):
        for title in bibl.findall('./title'):
            str_title = title.text.split(':')[0]
            if 'FS' in str_title or 'GS' in str_title:
                fs_dict[str_title] = bibl.get(ns + 'id')
            
    return fs_dict

def get_author_dict(literature_xml):
    '''Takes list of bibliographical entries (as XML file) and creates dictionary with author names (and possibly publication year) and corresponding ids.'''

    l_root = helpers.get_root(literature_xml)
    author_dict = {}
    
    for bibl in ET.ElementTree(l_root).findall('.//listBibl/bibl'):
        for author in bibl.findall('./author'):
            auth = author.text.strip()
            id = bibl.get(ns + 'id')
            
            year = bibl.find('date')
            # if there is a date mentioned behind author
            if year != None:              
                year = year.text
                auth = auth + '_' + year
                author_dict[auth] = id
            else:
                author_dict[auth] = id

    return author_dict


def get_editor_dict(literature_xml):
    '''Takes list of bibliographical entries (as XML file) and creates dictionary with editor names (and possibly publication year) and corresponding ids.'''
    l_root = helpers.get_root(literature_xml)
    editor_dict = {}

    for bibl in ET.ElementTree(l_root).findall('.//listBibl/bibl'):
        for editor in bibl.findall('./editor'):
            ed = editor.text.strip()
            id = bibl.get(ns + 'id')
            
            year = bibl.find('date')
            # if there is a date mentioned behind editor
            if year != None:               
                year = year.text
                ed = ed + ',' + year
                editor_dict[ed] = id
            else:
                editor_dict[ed] = id
    
    return editor_dict


def bibl_add_corresp(root, periodicals_xml, literature_xml):
    '''Adds attribute corresp to <bibl>-elements if the mentioned work is abbreviated and can be linked to an entry in chapter "Abgekürzt zitierte Literatur".
       Takes XML-files of tagged periodical list and literature list containing xml:ids for each mentioned work.
       Values for corresp are '#' + xml:id of the corresponding <bibl>.
    '''
    
    ### get different dictionaries 
    p_dict = get_p_dict(periodicals_xml)
    l_short_dict = get_l_short_dict(literature_xml)
    fs_dict = get_FS_dict(literature_xml)
    author_dict = get_author_dict(literature_xml)
    editor_dict = get_editor_dict(literature_xml)
    
    ### periodicals
    for bibl in ET.ElementTree(root).findall('.//bibl[@type="list"]/bibl'):
        for p in p_dict:
            # in case of "FS" exclude that cited work is not a "Festschrift"
            if p == "FS":  
                if p in bibl.text:
                    # if "FS" is followed by whitespace + a digit, it's a periodical
                    if re.search('FS\s\d', bibl.text):  
                        bibl.set('corresp', '#' + p_dict[p])
            else:
                if p in bibl.text:
                    bibl.set('corresp', '#' + p_dict[p])
                    
        # special case: "Sprache" is abbreviation for "Zeitschrift für Sprachwissenschaft" 
        if re.search(r'Sprache\s\d{1,2}\s\(\d{4}\)', bibl.text):
            bibl.set('corresp', '#B804')
    
    
    ### short titles
    for bibl in ET.ElementTree(root).findall('.//bibl[@type="list"]/bibl'):
        # <bibl>-elements without attribute 'corresp':
        if not bibl.get('corresp'):
            strlist = bibl.text.split()
            for short in l_short_dict:
                # compare short title to first word in <bibl>
                if short == strlist[0]:   
                    bibl.set('corresp', '#' + l_short_dict[short])


    ### parts of collected editions
    for bibl in ET.ElementTree(root).findall('.//bibl[@type="list"]/bibl'):
        # <bibl>-elements without attribute 'corresp':
        if not bibl.get('corresp'):
            bibl_text = bibl.text
            # searching for pattern containg "in"
            if re.search(r'([^,^=^\n^\.]+,)+(\s[^\.]+\.)+\sin', bibl.text):
                # searching for "in" + following word (which is probably the title or editor)
                bibl_text = re.search(r'in\s[^\s]+', bibl.text).group()  
                strlist = bibl_text.split()
                editor = strlist[1]  # possible editor
                
                for e in editor_dict:
                    e_list = e.split(',')
                    # getting surname
                    name = e_list[0]
                    if name == editor:
                        try:
                            # if there exists a year (means editor has published multiple works)
                            year = e_list[2]
                            # if text in <bibl> contains publication date
                            if year in bibl.text:   
                                id = editor_dict[e]
                                bibl.set('corresp', '#' + editor_dict[e])
                        # no publication year:         
                        except:
                            bibl.set('corresp', '#' + editor_dict[e])    
                         
    
    ### Festschriften and Gedenkschriften
    for bibl in ET.ElementTree(root).findall('.//bibl[@type="list"]/bibl'):
        # <bibl>-elements without attribute 'corresp':
        if not bibl.get('corresp'):
            # searching for pattern author name follwed by "FS" or "GS"
            if re.search(r'([^,^=^\n^\.]+,)+(\s[^\.]+\.)+\s(FS|GS)\s[^\s]+', bibl.text):
                # getting "FS" + following word  
                fs = re.search(r'FS\s[^\(]+', bibl.text).group()  
                fs = fs.strip()

                for f in fs_dict:
                    if f == fs:
                        bibl.set('corresp', '#' + fs_dict[f])
    
    ### authors
    for bibl in ET.ElementTree(root).findall('.//bibl[@type="list"]/bibl'):
        # <bibl>-elements without attribute 'corresp':
        if not bibl.get('corresp'):
            for author in author_dict:
                author_str = author.split(',')
                surname = author_str[0]
                bibl_text = bibl.text.strip()
            
                if bibl_text.startswith(surname):
                    
                    try:
                        # if there exists a year (means author has published multiple works)
                        year = author.split('_')[1]   
                        # if text in <bibl> contains publication date    
                        if year in bibl.text:   
                            bibl.set('corresp', '#' + author_dict[author])
                    # no publication year:        
                    except:
                        bibl.set('corresp', '#' + author_dict[author])    
                       
    return root


def ET2string(root):
    '''takes root and returns text as string object'''
    # changing ElementTree object into string
    tei= ET.tostring(root, encoding='utf-8').decode('utf-8')
    # add namespace declaration to root element
    tei = tei.replace('<TEI>', '<TEI xmlns="http://www.tei-c.org/ns/1.0">') 
    tei = xml + tei
    return tei
    



# === Coordinating function ===
 
def main(tei, periodicals_xml, literature_xml, lang_csv, lang_cap_csv):
    print("--- 15_add_attributes.py running")
    tei_parsed = helpers.parse_xml(tei)
    tei_parsed = entry_add_id(tei_parsed)
    tei_parsed = entry_add_type_homonymic(tei_parsed)
    tei_parsed = entry_add_xml_lang(tei_parsed)
    tei_parsed = sense_add_id(tei_parsed)
    tei_parsed = date_add_from_to(tei_parsed)
    tei_parsed = ref_add_target(tei_parsed)
    tei_parsed = form_add_xml_lang(tei_parsed, lang_csv, lang_cap_csv)
    tei_parsed = bibl_add_corresp(tei_parsed, periodicals_xml, literature_xml)
    tei = ET2string(tei_parsed)
    print("... done!")
    return tei
