#!/usr/bin/env python3
'''
SCRIPT 05:
Script for tagging the entry entities and different entities that belong to the entry head as lemma,
grammatical information, lexical/stylistic information and date
as well as entities found in the entry head but also at other positions like references and sublemmata.

Used package:
    re (see: https://docs.python.org/3/library/re.html)
'''


# === Imports ===

import re
import S_01_helpers as helpers


# === Functions ===

def mark_entry(tei):
    ''' Inserts <entry>-tags.'''
    tei = tei.replace('</p><p><hi rendition="font1"', '</p></entry><entry><p><hi rendition="font1"')  
    tei = tei.replace('<body><p><hi rendition="font1"', '<body><entry><p><hi rendition="font1"')  
    tei = tei.replace('</p></body>', '</p></entry></body>') 
    return tei


def mark_lemma(tei):
    '''Marks the lemma with <orth> and <form type="lemma"> and deletes <hi> around the lemma.'''
    
    tei = re.sub(r'(?P<entry><entry><p>)<hi rendition="font1" style="font-weight:bold;">(?P<lemma>([^<]|<hi[^<]+</hi>)+)</hi>', r'\g<entry><form type="lemma"><orth>\g<lemma></orth></form>', tei)
    
    return tei

def mark_sublemma(tei):
    '''Marks the sublemmata with <orth> and <form type="sublemma">.'''

    ### step 1: tagging whole content of <hi rendition="font1" style="font-weight:bold;"> 
    tei = re.sub(r'<hi rendition="font1" style="font-weight:bold;">(?P<sublem>([^<]|<hi[^<]+</hi>)+\.?)</hi>', r'<form type="sublemma"><orth>\g<sublem></orth></form>', tei)
    

    ### step 2: tagging various sublemmata seperately

    # searching for parts that are tagged as sublemma
    regex = re.compile(r'(?P<start><form type="sublemma"><orth>)(?P<sublem>[^<]+)(?P<end></orth></form>)')
    for match in regex.finditer(tei):
        text = match[2]               # text contains one ore several sublemmata
        
        ### splitting at whitespace
        
        # excluding sublemmta consisting of multiple words by masking the whitespace:
        text = text.replace(', ', ',#')   # whitespace after ',' is replaced by #
        text = text.replace(r' ', r'$')  # remaining whitespace is replaced by $
        text = text.replace('#', '# ')  # inserting whitespace behind #
        # splitting at whitespace
        sublemmata = text.split()
        # undo masking of whitespace
        text = text.replace('#', '')  
        text = text.replace('$', ' ') 
        
        ## sublemmata is a list of strings (the single sublemmata)
        
        # tagging
        for n, item in enumerate(sublemmata):
            sublemmata[n] = item.replace(item, '<form type="sublemma"><orth>' + sublemmata[n] + '</orth></form>')
    
        ## list sublemmata contains tagged strings
            
        ### transforming list into string
        
        replaceStr = ''
        for subl in sublemmata:
            replaceStr = replaceStr + subl 
            
        ## replaceStr contains tagged sublemmata as string
            
        ### replacing in text
        searchStr = '<form type="sublemma"><orth>' + text + '</orth></form>'
        tei = tei.replace(searchStr, replaceStr)
        
        # undo masking of whitespace
        tei = tei.replace(r'#', r' ')
        tei = tei.replace(r'$', r' ')

     ### end step 2
        
        # special case: sublemma in '()'
        tei = re.sub(r'(?P<start><form type="lemma"><orth>)(?P<lemma>[\u002D\w]+\s)(?P<sublem>\([\u002D\w]+(<hi[^<]+</hi>)?\)\s?)(?P<end></orth></form>)', r'\g<start>\g<lemma>\g<end><form type="sublemma"><orth>\g<sublem>\g<end>', tei)
        
     ### step 3: move punctuation and whitespace 
        tei = re.sub(r'(?P<start><form type="sublemma"><orth>)(?P<front>\s*\(*)(?P<sublemma>[\u002D\u2197\w]+(<hi[^<]+</hi>)?)(?P<back>[\s,.;)]*)(?P<end></orth></form>)', r'\g<front>\g<start>\g<sublemma>\g<end>\g<back>', tei)
    
    return tei


def mark_def(tei):
    '''Marks meaning information with <def>.'''
    
    ### adapting <hi>-annotation
    
    # special case 1: change of typography within meaning paraphrase
    tei = re.sub(r'(‘[^<’]*)</hi><hi rendition="font5" style="font-style:italic;">([^<]+)</hi><hi rendition="font5">([^<]*’)', r'\1<hi rend="italics">\2</hi>\3', tei)
    # special case 2: change of typography after the first word of meaning paraphrase
    tei = re.sub(r'</hi><hi rendition="font5" style="font-style:italic;">‘([^<]+)</hi>(<hi rendition="font5">)([^<]*’)', r'</hi>‘<hi rend="italics">\1</hi>\3\2', tei)
    # special case 3: change of typography after the last word of meaning paraphrase    
    tei = re.sub(r'(‘[^<]*)</hi><hi rendition="font5" style="font-style:italic;">([^<’]*)(’[^<]?)</hi>', r'</hi>\1<hi rend="italics">\2</hi>\3', tei)
    
    ### inserting <def></def> 
    tei = re.sub(r'(‘[^’]+’)', r'<def>\1</def>', tei)
    
    ### deleting <hi> around <def>
    tei = re.sub(r'<hi rendition[^>]+>\s?(?P<d><def>[^<]+</def>)(?P<add>[^<]?(\([^<]+\))?\s?)</hi>', r'\g<d>\g<add>', tei)
    
    return tei


def mark_usg_pos(tei, lexis_csv, pos_csv):
    '''Marks grammatical and lexical/stylistical information.'''
    
    ### searching and tagging
    # standard case
    pattern = r'(</form>\s?<hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    
    # case 1: meaning paraphrase between POS and lexical/stylistical information
    # case 1a: standard case
    pattern = r'(</def>\s?<hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'  
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    # case 1b: meaning paraphrase + addition in '()'
    pattern = r'(</def>\s?\([^<]+\)\s?<hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    # case 1c: meaning paraphrase + additional text
    pattern = r'(</form><hi rendition="font5" style="font-style:italic;">[^<]+</hi><hi rendition="font5">[^<]+<def>[^<]+</def>\s?</hi><hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    pattern = r'(</gramGrp></hi><hi rendition="font5">[^<]+<def>[^<]+</def>\s?</hi><hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    # case 1d: meaning paraphrase + reference  
    pattern = r'(</def>\s?\([^)]+\)\s?</hi><hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)

    # case 2: lemma + addition  in '()'
    pattern = r'(</form><hi rendition="font5">\([^)]+\)\s?</hi><hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    
    # case 3: sublemmata behind lemma
    # case 3a: sublemmata in '()'
    pattern = r'(</form>\([^)]+\)\s?<hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    # case 3b: sublemmata + additional text
    pattern = r'(</form><hi rendition="font5">\([^)]+\)\s?<hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    
    # case 4: '()' between POS and lexical/stylistical information
    # case 4a: text in '()' in italics
    pattern = r'(</form><hi rendition="font5" style="font-style:italic;">[^<]+</hi><hi rendition="font5"> \([^\)]+\) </hi><hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    pattern = r'(</gramGrp></hi><hi rendition="font5">\s\([^\)]+\) </hi><hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    # case 4b: in recte
    pattern = r'(</gramGrp></hi><hi rendition="font5">\s\([^\)]+\))([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    # case 4c: meaning paraphrase in '()'
    pattern = r'(</form><hi rendition="font5" style="font-style:italic;">[^<]+</hi><hi rendition="font5">\s?\([^\)]+\)\s?<hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    pattern = r'(</gramGrp></hi><hi rendition="font5">\s?\([^\)]+\)\s?<hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    
    # case 5: sublemmata + additional text in '()'
    pattern = r'(</form>\([^)]+\)\s?<hi rendition="font5" style="font-style:italic;">[^<]+</hi><hi rendition="font5">\s?\([^)]+\)\s?</hi><hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    
    # case 6a: reference behind POS
    pattern = r'(</form>\s?<hi rendition="font5" style="font-style:italic;">)([^<]+\u2197[^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    # case 6b: referenced entry is a homonymic entry
    pattern = r'(</form>\s?<hi rendition="font5" style="font-style:italic;">)([^<]+\u2197[^<]+<hi[^<]+</hi>[^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    
    # case 7: behind POS homographs are differentiated includiung numbering
    pattern = r'(\s?<hi[^<]+>\d\)\s</hi><hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    pattern = r'(</def>\s?</hi><hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    
    # case 8: additional POS information in '()'
    # move <hi>-tagging
    tei = re.sub(r'(?P<before></gramGrp></hi><hi[^>]+>)(?P<between>\s?\([^<]+)(?P<hiEnd></hi>)(?P<hiStart><hi[^>]+>)?(?P<after>[^)^<]+\)\s)', r'\g<before>\g<hiEnd>\g<between>\g<after>\g<hiStart>', tei)
    # tagging
    pattern = r'(</gramGrp></hi>\s\()([^)]+)(\))'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    pattern = r'(</gramGrp>\s?\)\s?<hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)'   
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    
    # case 9
    # case 9 a: addition to POS (in case of suffixes)
    pattern = r'(</gramGrp></hi><hi rendition="font5"> zur Bildung von[^<]+</hi><hi rendition[^>]+>)([^<]+)(</hi>)'
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    # case 9b: addition to POS + meaning paraphrase + references in brackets
    pattern = r'(</gramGrp></hi><hi rendition="font5"> zur Bildung von[^<]+<def>[^<]+</def>\s\([^\)]+\))([^<]+)(</hi>)'
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)

    return tei


def delete_hi_pos_usg(tei):
    '''Deletes or moves <hi>-tags around <gramGrp> and <usg>.'''
    
    # deletes <hi> around <usg>
    tei = re.sub(r'<hi rendition="font5" style="font-style:italic;">(?P<keep>\s?(<usg[^<]+</usg>\s?)+[^<]*)</hi>', r'\g<keep>', tei)
    
    # moves </hi> in front of <usg> (case: <hi> contains additional text in front of <usg>)
    tei = re.sub(r'(<usg[^<]+</usg>\s?[^<]*)+(</hi>)', r'\2\1', tei)
    
    # deletes <hi> around <gramGrp>
    tei = re.sub(r'<hi rendition="font5" style="font-style:italic;">(?P<keep>\s?<gramGrp>(<gram[^<]+</gram>(\s\/)?){1,4}</gramGrp>\s?(\u2197[^<]+(<hi[^<]+</hi>[^<]?)?)?[^<]?)\s?</hi>', r'\g<keep>', tei)
    
    # deletes <hi> around <gramGrp> + <usg>
    tei = re.sub(r'<hi rendition="font5" style="font-style:italic;">(?P<keep><gramGrp>(<gram[^<]+</gram>(\s+/)?){1,4}</gramGrp>\s{0,2}(<usg[^<]+</usg>\s?){1,3}(\w+\.)?)</hi>', r'\g<keep>', tei)
       
    return tei


def mark_lemmaGroup(tei):
    ''' Inserts <form type="lemmaGroup"> around <form type="lemma"> (+ possibly sublemmata) and <gramGrp>.'''

    # standard case
    tei = re.sub(r'(<form type="lemma"><orth>([^<]|<hi[^<]+</hi>)+</orth></form>\s?<gramGrp>(<gram[^<]+</gram>(\s+/)?){1,4}</gramGrp>)', r'<form type="lemmaGroup">\1</form>', tei)
    
    # special case 1: sublemmata
    tei = re.sub(r'(<form type="lemma"><orth>([^<]|<hi[^<]+</hi>)+</orth></form>(<hi[^>]+>)?\([^)]+\)\s?(</hi>)?<gramGrp>(<gram[^<]+</gram>(\s+/)?){1,4}</gramGrp>)', r'<form type="lemmaGroup">\1</form>', tei)
    
    # special case 2: homographs
    tei = re.sub(r'(<form type="lemma"><orth>([^<]|<hi[^<]+</hi>)+</orth></form>(<hi[^>]+>\d\)\s(</hi>)?<gramGrp>(<gram[^<]+</gram>){1,4}</gramGrp>){1,3})', r'<form type="lemmaGroup">\1</form>', tei)

    # special case 3: additonal POS in '()'
    tei = re.sub(r'(</gramGrp>)(</form>)(\s\(([^<]+)?<gramGrp><gram[^>]+>[^<]+</gram></gramGrp>\s?\))', r'\1\3\2', tei)

    return tei


def mark_sense(tei):
    ''' Inserts <sense> around <def> in entry head.'''
    
    # possible addition in '()' 
    tei = re.sub(r'(</gramGrp></form>)(<def>[^<]+</def>(\s\([^)]+\))?)', r'\1<sense>\2</sense>', tei)
    
    # reference in '()' including change of typography
    tei = re.sub(r'(?P<before></gramGrp></form>)(?P<child>(<hi rendition="font5">\s)<def>[^<]+</def>(\s\([^)]+\))\s?</hi>)', r'\g<before><sense>\g<child></sense>', tei)

    # multiple <def>s + additional text
    tei = re.sub(r'(?P<before></gramGrp></form>)<hi rendition[^>]+>(?P<sense>(([^<]+)?<def>[^<]+</def>([^<]+)?)*)</hi>', r'\g<before><sense>\g<sense></sense>', tei)

    # <def> behind <usg>
    tei = re.sub(r'(</gramGrp></form>\s(<usg[^<]+</usg>)+)(<def>[^<]+</def>)', r'\1<sense>\3</sense>', tei)
    
    # deleting empty <sense>-elements
    tei = tei.replace('<sense></sense>', '')

    return tei


def mark_missing_usg(tei, lexis_csv, pos_csv):
    ''' Adds tagging of not found lexical/stylistic information.
        Has to be called after mark_sense().   
    '''
    
    pattern = r'(</sense><hi rendition="font5" style="font-style:italic;">)([^<]+)(</hi>)' 
    tei = helpers.mark_abbr_usg_pos(pattern, lexis_csv, pos_csv, tei)
    tei = delete_hi_pos_usg(tei)
    
    return tei


def mark_ref(tei):
    '''Marks references and deletes <hi>-elements.'''
    
    ### finding references (indication: arrow) and inserting tagging
    tei = re.sub(r'(?P<arrow>\u2197)(?P<ref>\-?\w+(\(\w+\))?(\w+)?(\(\w+\))?\-?(<hi[^<]+</hi>)?)', r'<xr><lbl>\g<arrow></lbl><ref type="entry"><hi rend="italics">\g<ref></hi></ref></xr>', tei)

    ### deleting <hi>-elements in <ref>
    
    # case: sublemmata
    tei = re.sub(r'(?P<before><form type="sublemma"><orth><xr><lbl>↗</lbl><ref type="entry">)<hi rend="italics">(?P<ref>\w+(<hi[^<]+</hi>)?)</hi>(?P<after></ref></xr>)', r'\g<before>\g<ref>\g<after>', tei)
    # case: multiple references
    tei = re.sub(r'<hi\srendition[^>]+>(?P<keep>(\(?\s?<xr><lbl>↗</lbl><ref type="entry"><hi rend="italics">([^<]|<hi[^<]+</hi>)+</hi></ref></xr>([,;]?\s)?)+[^<]*)</hi>', r'\g<keep>', tei)
    
    # case: without indication of language
    tei = re.sub(r'(?P<before><hi rendition="font(4|5)" style="font-style:italic;">[^<]+)(?P<ref>(<xr><lbl>↗</lbl><ref type="entry">(<hi rend="italics">)?([^<]|<hi[^<]+</hi>)+(</hi>)?</ref></xr>([,;]\s)?)*[^<]{,3}\s?)</hi>', r'\g<before></hi>\g<ref>', tei)
    
    # case: in etymological section; reference in '()' 
    tei = re.sub(r'(?P<before><(hi|p) rendition="font5"[^>]+>[^<]*)(?P<ref>\((<xr><lbl>↗</lbl><ref type="entry">(<hi rend="italics">)?([^<]|<hi[^<]+</hi>)+(</hi>)?</ref></xr>([,;]?\s?))+\)[^<]*)</hi>', r'\g<before></hi>\g<ref>', tei)
    tei = re.sub(r'(?P<before><(hi|p) rendition="font[^>]+>)(?P<ref>([^<]*\(?<xr><lbl>↗</lbl><ref type="entry">(<hi rend="italics">)?([^<]|<hi[^<]+</hi>)+(</hi>)?</ref></xr>([,;]?\s?))+\)[^<]*)</hi>', r'\g<before></hi>\g<ref>', tei)
    
    # delete empty <hi>-elements
    tei = re.sub(r'<hi rendition="font(4|5)" style="font-style:italic;"></hi>', r'', tei)
    
    return tei

        
def mark_dateGroup(tei):
    ''' Mark date information in entry head.
    Note: This annotation is going to be modified in S_12 because it became evident
    that according to TEI <def> isn't allowed in <usg> or <seg>.
    '''

    ### correct OCR errors:
    tei = re.sub(r'ıo. Jh.', r'10. Jh.', tei)
    tei = re.sub(r'ıı. Jh.', r'11. Jh.', tei)
    
    ### move <hi> behind date information
    
    # case 1a: one date (standard)
    tei = re.sub(r'(<hi rendition[^>]+>)(\(\d{1,2}.\sJh.\))', r'\2\1', tei)
    # case 1b: one date + explanation
    tei = re.sub(r'(<hi rendition="font5">)([^(^<]+\(\d{,2}.\sJh.(,[^)^<]+)?\))', r'\2\1', tei)
    # case 2: two dates Daten; "form"/explanation
    tei = re.sub(r'(<hi rendition="font5">)(\s?\(\d{,2}.\sJh.\,\s[^\d]+\d{,2}.\sJh.\))', r'\2\1', tei)
    # case 3a: one date + word form
    tei = re.sub(r'<hi rendition="font5">(?P<date>\s?\(\d{1,2}.\sJh.\,\s[^<]+)</hi><hi[^>]+>(?P<etym>[^<]+)</hi>(?P<end><hi[^>]+>)\)', r'\g<date><hi rend="italics">\g<etym></hi>)\g<end>', tei)
    # case 3b: one date sublemma 
    tei = re.sub(r'<hi rendition="font5">\s?(?P<date>\(\d{1,2}.\sJh.\,\s[^<]+)</hi>(?P<sublem><form type="sublemma"><orth>[^<]+</orth></form>\))', r'\g<date>\g<sublem>', tei)
    # case 4a: two dates; word form as label 
    tei = re.sub(r'<hi rendition="font5">(?P<dateFirst>\s\(\d{,2}.\sJh.,\s[^<]*)</hi><hi[^>]+>(?P<etym>[^<]+</hi>)(?P<hi><hi[^>]+>)(?P<dateForm>\s?\d{,2}.\sJh.\))', r'\g<dateFirst><hi rend="italics">\g<etym>\g<dateForm>\g<hi>', tei)
    tei = re.sub(r'(\(\d{1,2}.\sJh.,[^<]+<hi[^<]+</hi>)(<hi[^>]+>)(\d{1,2}.\sJh.\))', r'\1\3\2', tei)
    # case 4b: two dates; word form as label + meaning
    tei = re.sub(r'<hi rendition="font5">(?P<dateFirst>\s\(\d{,2}.\sJh.,\s)</hi><hi[^>]+>(?P<etym>[^<]+</hi>)(?P<hi><hi[^>]+>)(?P<def>\s<def>[^<]+</def>)(?P<dateForm>\s\d{,2}.\sJh.\))', r'\g<dateFirst><hi rend="italics">\g<etym>\g<def>\g<dateForm>\g<hi>', tei)
    # case 5: two dates; meaning as label
    tei = re.sub(r'(<hi rendition="font5">)(\s\(\d{,2}.\sJh.,\s<def>[^<]+</def>\s\d{,2}.\sJh.\))', r'\2\1', tei)

    ### tagging
    # case 1a
    tei = re.sub(r'(?P<before></usg>([^<]{,5}</hi>)?\s?\()(?P<date>\d{,2}.\sJh.)(?P<after>\))', r'\g<before><usg type="time" ana="date"><date><date type="firstOccurrence">\g<date></date></date></usg>\g<after>', tei)
    # case 1b
    tei = re.sub(r'(?P<before></usg>([^(^<]+)\()(?P<date>\d{,2}.\sJh.)(?P<add>,[^)^<^\d]+)(?P<after>\))', r'\g<before><usg type="time" ana="date"><date><date type="firstOccurrence">\g<date></date></date>\g<add></usg>\g<after>', tei)
    
    # case 2
    tei = re.sub(r'(?P<before></usg>([^<]{,5}</hi>)?\s?\()(?P<date1>\d{,2}.\sJh.)\,(?P<label>[^\d^‘]+)(?P<date2>\d{1,2}\.\sJh.)(?P<after>\))', r'\g<before><usg type="time" ana="date"><date><date type="firstOccurrence">\g<date1></date></date>, <date><seg type="dateLabel">\g<label></seg><date type="form">\g<date2></date></date></usg>\g<after>', tei)
    
    # case 3a
    tei = re.sub(r'(?P<before></usg>\s?\()(?P<date>\d{1,2}.\sJh.)(?P<add>,[^<]*)<hi[^>]+>(?P<etym>[^<]+)</hi>(?P<end>\))', r'\g<before><usg type="time" ana="date"><date><date type="firstOccurrence">\g<date></date></date>\g<add><cit type="etymologicalForm"><form xml:lang=""><orth><hi rend="italics">\g<etym></hi></orth></form></cit></usg>\g<end>', tei)
    
    # case 3b
    tei = re.sub(r'(?P<before></usg>([^<]{,5}</hi>)?\s?\()(?P<date1>\d{,2}.\sJh.)\,\s(?P<betw>[^<]+)(?P<subl><form type="sublemma"><orth>[^<]+</orth></form>)\)', r'\g<before><usg type="time" ana="date"><date><date type="firstOccurrence">\g<date1></date></date>, \g<betw>\g<subl></usg>)', tei)
    
    # case 4a
    tei = re.sub(r'(?P<before></usg>([^<]{,5}</hi>)?\s?\()(?P<date1>\d{,2}.\sJh.)\,\s(?P<etym><hi[^>]+>[^<]+</hi>)\s(?P<date2>\d{,2}.\sJh.)(?P<after>\))', r'\g<before><usg type="time" ana="date"><date><date type="firstOccurrence">\g<date1></date></date>, <date><seg type="dateLabel"><cit type="etymologicalForm"><form xml:lang="">\g<etym></form></cit></seg> <date type="form">\g<date2></date></date></usg>\g<after>', tei)
    
    # case 4b
    tei = re.sub(r'(?P<before></usg>([^<]{,5}</hi>)?\s?\()(?P<date1>\d{,2}.\sJh.)\,\s(?P<etym><hi[^>]+>[^<]+</hi>)\s(?P<def><def>[^<]+</def>\s)(?P<date2>\d{,2}.\sJh.)(?P<after>\))', r'\g<before><usg type="time" ana="date"><date><date type="firstOccurrence">\g<date1></date></date>, <date><seg type="dateLabel"><cit type="etymologicalForm"><form xml:lang=""><orth>\g<etym></orth></form></cit>\g<def></seg><date type="form"> \g<date2></date></date></usg>\g<after>', tei)
    
    # case 5a: two dates; meaning as label
    tei = re.sub(r'(?P<before></usg>([^<]{,5}</hi>)?\s\()(?P<date1>\d{,2}.\sJh.),\s(?P<meaning><def>[^<]+</def>)(?P<date2>\s\d{1,2}.\sJh.)(?P<after>\))', r'\g<before><usg type="time" ana="date"><date><date type="firstOccurrence">\g<date1></date></date>, <date><seg type="dateLabel">\g<meaning></seg><date type="meaning">\g<date2></date></date></usg>\g<after>', tei)
    
    # case 5b: two dates; meaning + explanation as label
    tei = re.sub(r'(?P<before></usg>([^<]{,5}</hi>)?\s\()(?P<date1>\d{,2}.\sJh.),\s(?P<meaning>[^<]*<def>[^<]+</def>[^<]*)(?P<date2>\s\d{1,2}.\sJh.)(?P<after>\))', r'\g<before><usg type="time" ana="date"><date><date type="firstOccurrence">\g<date1></date></date>, <date><seg type="dateLabel">\g<meaning></seg> <date type="meaning">\g<date2></date></date></usg>\g<after>', tei)
    
    # case 6: language acronym between <usg> and <date>
    tei = re.sub(r'(?P<before>\w+.</usg>(<hi rendition="font5">)?\s{,2}\w+.\s?(</hi>)?\s?\()(?P<date>\d{1,2}\.\sJh.)(?P<after>\))', r'\g<before><usg type="time" ana="date"><date><date type="firstOccurrence">\g<date></date></date></usg>\g<after>', tei)
    
    # case 7: missing date information, indicated by '-'
    tei = re.sub(r'(\()(-)(\))', r'\1<usg type="time" ana="date"><date><date type="firstOccurrence">\2</date></date></usg>\3', tei)
    
    return tei

          
# === Coordinating function ===

def main(tei, lexis_csv, pos_csv):
    print("--- 05_mark_entry_head.py running")
    tei = mark_entry(tei)
    tei = mark_lemma(tei)
    tei = mark_sublemma(tei)
    tei = mark_def(tei)
    tei = mark_usg_pos(tei, lexis_csv, pos_csv)
    tei = delete_hi_pos_usg(tei)
    tei = mark_lemmaGroup(tei)
    tei = mark_ref(tei)
    tei = mark_sense(tei)
    tei = mark_missing_usg(tei, lexis_csv, pos_csv)
    tei = mark_dateGroup(tei)
    print("... done!")
    return tei
    