#!/usr/bin/env python3
'''
SCRIPT 13:
Script for turning the Finereader-output of chapter "Abgekürzt zitierte Literatur" (TXT file) into XML-TEI and assigning xml:ids to each bibliographical entry. 

Input: chapter "Abgekürzt zitierte Literatur" as TXT file
Output: chapter as XML-TEI file

Used package:
    re (see: https://docs.python.org/3/library/re.html)
'''

# === Imports ===

import re
import S_01_helpers as helpers


# === Functions ===

def mark_head_desc(txt):
    '''Marks first line with <head>, second line with <desc>.'''
    
    lines = txt.split("\n")
    head = '<head>' + lines[0] + '</head>'
    txt = re.sub(lines[0], head, txt)
    desc = '<desc>' + lines[1] + '</desc>'
    txt = re.sub(lines[1], desc, txt)
    txt = txt.replace('(<desc>', '<desc>')
    txt = txt.replace('</desc>)', '</desc>')
    
    return txt

def mark_author(txt):
    '''Annotates author name.'''
    # standard case
    txt = re.sub(r'(<bibl>)(?P<author>([^,^=^\n]+,)+(\s[^\.]+\.)+)(?P<after>(\s*\(\d+(\/\d+)?(\sf{0,2}\.)?\))?:)', r'\1<author>\g<author></author>\g<after>', txt)
    # addition in '()' behind author name
    txt = re.sub(r'(<bibl>(?!FS))(?P<author>[^\(^\n^:^<]+)(?P<after>(\s\([^\)]+\))+:)', r'\1<author>\g<author></author>\g<after>', txt)
    # behind short title
    txt = re.sub(r'(<bibl>)(?P<short>[^=^\n^>]+)=(?P<author>([^,^=^\n^\.]+,)+(\s[^\.]+\.)+)\:', r'<bibl><title type="short">\g<short></title>=<author>\g<author></author>:', txt)
    # first name with hyphen 
    txt = re.sub(r'(<bibl>)(?P<author>([^,^=^\n]+,)+(\s([^\.]\.\-?)+))(?P<after>(\s*\(\d+(\sf{0,2}\.)?\))?:)', r'\1<author>\g<author></author>\g<after>', txt)
    # no first name
    txt = re.sub(r'<bibl>([^:^.^,^=^\s]+):', r'<bibl><author>\1</author>:', txt)
    # complete first name
    txt = re.sub(r'(<bibl>(?!(FS|GS)))(?P<author>([^,^<^=^\(]+(\,\s)?){2}):', r'\1<author>\g<author></author>:', txt)
    # two authors
    txt = re.sub(r'<bibl>(?P<a1><author>[^,]+,(\s\w\.)+)\,(?P<a2>[^,]+,(\s\w\.)+</author>)', r'<bibl>\g<a1></author>,<author>\g<a2>', txt)
    # three authors
    txt = re.sub(r'(?P<a1><author>\s*[^,]+,(\s\w\.)+)\,(?P<a2>\s*[^,]+,(\s\w\.)+)\,(?P<a3>\s*[^,]+,(\s\w\.)+</author>)', r'\g<a1></author>,<author>\g<a2></author>,<author>\g<a3>', txt)
    
    return txt

def mark_editor(txt):
    ''' Annotates the editor name when collected works are listed individually.'''

    txt = re.sub(r'(<bibl>)(?P<editor>([^,^=^\^<]+,)+(\s[^\.^<]+\.)+)(\s\(Hrsg\.\))', r'\1<editor>\g<editor></editor>\5', txt)
    
    # change <author> to <editor> when 'Hrsg.' is mentioned
    # three editors
    txt = re.sub(r'<author>([^<]+)</author>,<author>([^<]+)</author>,<author>([^<]+)</author>(\s\(Hrsg\.\))', r'<editor>\1</editor>,<editor>\2</editor><editor>\3</editor>\4', txt)
    # two editors
    txt = re.sub(r'<author>([^<]+)</author>,<author>([^<]+)</author>(\s\(Hrsg\.\))', r'<editor>\1</editor>,<editor>\2</editor>\3', txt)
    # one editor
    txt = re.sub(r'<author>([^<]+)</author>(\s\(Hrsg\.\))', r'<editor>\1</editor>\2', txt)
    
    # split multiple editors
    txt = re.sub(r'<bibl>(?P<e1><editor>[^,]+,(\s\w+\.)+)\,(?P<e2>[^,]+,(\s\w+\.)+</editor>)', r'<bibl>\g<e1></editor><editor>\g<e2>', txt)
    txt = re.sub(r'<bibl>(?P<e1><editor>[^,]+,(\s\w+\.)+)\,(?P<e2>[^,]+,(\s\w+\.)+\,)(?P<e3>[^,]+,(\s\w+\.)+</editor>)', r'<bibl>\g<e1></editor><editor>\g<e2></editor><editor>\g<e3>', txt)
    
    return txt


def mark_title(txt):
    ''' Annotates the title.'''
    
    # title if work is part of a collection or periodical
    txt = re.sub(r'(?P<before></author>(\s*\(\d+(\/\d+)?(\sf{0,2}\.)?\))?:)(?P<title>\s[^\.]+)(?P<after>\.\sIn:)', r'\g<before><title type="main">\g<title></title>\g<after>', txt)
    
    # the title is followed by a certain string 
    txt = re.sub(r'(?P<before></author>(\s*\(\d+(\/\d+)?(\sf{0,2}\.)?\))?:)(?P<title>\s[^<]+)(?P<after>\.\s(\d+\.\s(\w+\s)?Aufl|Bd\.|\d\sBde|FS|Teil|hrsg))', r'\g<before><title type="main">\g<title></title>\g<after>', txt)

    # title follows author
    txt = re.sub(r'(?P<before></author>(\s*\(\d+(\/\d+)?(\sf{0,2}\.)?\))?:)(?P<title>[^<]+)(?P<after>\.(\s[^\d^\.]+(u\.\sa\.)?\s\d{4}(\sf{0,2}|\/\d+)?\.))', r'\g<before><title type="main">\g<title></title>\g<after>', txt)
    
    # pattern short title = main title, "Hrsg." / "Bearbeitet von"
    txt = re.sub(r'(<bibl>)(?P<short>[^=^\n^>^\(]+)=(?P<main>.*?)(?P<after>\.\s(Hrsg|Bearbeitet))', r'\1<title type="short">\g<short></title>=<title type="main">\g<main></title>\g<after>', txt)
    # pattern short title = main title, followed by indicating the volume
    txt = re.sub(r'(<bibl>)(?P<short>[^=^\n^>^(]+)=(?P<main>[^<^>]*?)(?P<after>\.\s(Bd|I))', r'\1<title type="short">\g<short></title>=<title type="main">\g<main></title>\g<after>', txt)
    # pattern short title = main title, followed by place and year
    txt = re.sub(r'(<bibl>)(?P<short>[^=^<^\.]+)=(?P<main>[^<]+)(?P<after>\.\s[^\d^]+\d+(\sf{1,2})?.(\s*\([^\)]+\)\.?)?</bibl>)', r'\1<title type="short">\g<short></title>=<title type="main">\g<main></title>\g<after>', txt)
   
    # special case 'Freiburg/Br.' + 'Halle/S.' (placename ends with point)
    txt = re.sub(r'(?P<before></author>(\s\(\d{4}(\sf{0,2}f\.)?\))?:)(?P<title>[^<]+)(?P<after>\.\s(Freiburg/Br|Halle/S)\.\s\d{4}\.</bibl>)', r'\g<before><title type="main">\g<title></title>\g<after>', txt)

    # title follows "Hrsg." and is limited by "Aufl" or "Bd." 
    txt = re.sub(r'(\(Hrsg\.\)(\s\(\d+\))?:)(?P<title>[^<]+)(?P<after>\.\s(\d\.\sAufl|Bd\.))', r'\1<title type="main">\g<title></title>\g<after>', txt)
    # title follows "Hrsg."
    txt = re.sub(r'(\(Hrsg\.\)(\s\(\d+\))?:)([^<]+)(?P<after>\.(\s[^\d^\.]+\s\d{4}\.))', r'\1<title type="main">\3</title>\g<after>', txt)
    
    # behind text in '()' followed by volume 
    txt = re.sub(r'(?P<before></author>(\s*\([^\)]+\)):)(?P<title>\s[^\.]+)(?P<after>\.\s(\d|Bd|Hrsg))', r'\g<before><title type="main">\g<title></title>\g<after>', txt)
    # behind place + year + volume 
    txt = re.sub(r'(</author>:)([^\.^<]+)(\.\s[^\(]+([^\(^<]+\(\d{4}\)[.,]\s?)+)', r'\1<title type="main">\2</title>\3', txt)
    # behind place + year text in '()'
    txt = re.sub(r'(?P<before></author>(\s*\(\d+(\/\d+)?(\sf{0,2}\.)?\))?:)(?P<title>[^<]+)(?P<after>\.(\s[^\d^\.]+\s\d{4})\s\([^\)]+\)\.</bibl>)', r'\g<before><title type="main">\g<title></title>\g<after>', txt)
    
    # editor behind title 
    txt = re.sub(r'(</author>(\s\([^\)]+\))*:)([^\n^<]+)((hrsg\.|Hrsg\.))', r'\1<title type="main">\3</title>\4', txt)
    
    # without author + followed by 'Hrsg.' 
    txt = re.sub(r'(<bibl>)([^:^\n^<]+)(\.\sHrsg\.)', r'\1<title type="main">\2</title>\3', txt)
    # without author
    txt = re.sub(r'(<bibl>)([^:^\n^<]+)(\.[^\d]+\d{4}\.</bibl>)', r'\1<title type="main">\2</title>\3', txt)
    
    # English citation: withour author, with "ed."
    txt = re.sub(r'(<bibl>)([^\n^<]+)(\.\sEd\.)', r'\1<title type="main">\2</title>\3', txt)
    # special cases: limits of title can't be identified automatically
    txt = re.sub(r'(Studies in the Kinship Terminology of the Indo-European Languages. Acta Iranica. Textes et Memoires VII)', r'<title type="main">\1</title>', txt)
    txt = re.sub(r'(Wörterbuch der deutschen Tiernamen)', r'<title type="main">\1</title>', txt)
   
    ### Festschriften
    # title followed by 'Hrsg.' or 'Bd.' 
    txt = re.sub(r'(<bibl>)((FS|GS)(.*?))(\.\s(Hrsg.|Bd))', r'\1<title type="main">\2</title>\5', txt)
    # standard case FS
    txt = re.sub(r'(<bibl>)((FS|GS)(.*?))(\.\s[^\d\.]+\d{4}\.</bibl>)', r'\1<title type="main">\2</title>\5', txt)
    # without place/year
    txt = re.sub(r'(<bibl>)((FS|GS)[^<^\d]+)(</bibl>)', r'\1<title type="main">\2</title>\4', txt)
    # behind place/year additional text 
    txt = re.sub(r'(<bibl>)((FS|GS)(.*?))(\.\s[^\d\.]+\d{4}\.?[^<]+</bibl>)', r'\1<title type="main">\2</title>\5', txt)
    # special cases: places "Horn/N.-Ö." and "Halle/S."
    txt = re.sub(r'(<bibl>)(FS(.*?))(\.\s(Horn/N.-Ö.|Halle\/S\.)\s\d{4}\.</bibl>)', r'\1<title type="main">\2</title>\4', txt)
   
    # title ends with '?'
    txt = re.sub(r'(?P<before></author>(\s\(\d{4}(\sf{0,2}f\.)?\))?:)(?P<title>.*?\?)(?P<after>(\s[^\d^\.]+\s\d{4}(\sf{0,2})?\.))', r'\g<before><title type="main">\g<title></title>\g<after>', txt)
    
    return txt

def add_date(txt):
    ''' Annotates the publication year when the list contains more than one work of a certain author/editor.'''
    
    # author
    txt = re.sub(r'(<bibl><author>[^<]+</author>\s)(?P<date>\(\d+\/?(\sf{1,2}\.)?\d*\))', r'\1<date>\g<date></date>', txt)
    # editor
    txt = re.sub(r'(<bibl><editor>[^<]+</editor>\s\(Hrsg\.\)\s)(?P<date>\(\d+\/?(\sf{1,2}\.)?\d*\))', r'\1<date>\g<date></date>', txt)
    
    return txt


# === Coordinating function ===

def main(literature_file, literature_header):
    print("--- 13_mark_literature_list.py running")
    txt = helpers.read_file(literature_file)
    txt = helpers.change_brackets(txt)
    txt = mark_head_desc(txt)
    txt = helpers.mark_listBibl(txt)
    txt = helpers.mark_bibl(txt)
    txt = mark_author(txt)
    txt = mark_editor(txt)
    txt = mark_title(txt)
    txt = add_date(txt)
    txt = helpers.add_bibl_id(txt, 1)
    xml = helpers.transform2xml(txt, literature_header)
    helpers.save_file(xml, "literature.xml")
    print("... done!")
   
