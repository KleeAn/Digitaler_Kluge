#!/usr/bin/env python3
'''
SCRIPT 12:
Script for tagging remaining untagged entities (notes in bibl section, etymological section, whole section L),
typing related entries, deleting needless rendition and typographical information
and correcting tagging.

Used package:
    re (see: https://docs.python.org/3/library/re.html)
'''

# === Imports ===

import re
import S_01_helpers as helpers


# === Functions ===

def type_relatedEntry(tei):
    '''Inserts attribute 'type="relatedEntry' into <entry>-elements of referencing entries.'''
    
    matches = re.finditer('<entry><p><form type="lemmaGroup">(<form[^>]+><orth>[^<]+(<hi[^<]+</hi>)?</orth></form>\s?<gramGrp>(<gram [^<]+</gram>)*</gramGrp>(</form>)?\,?\s?)+(<usg[^<]+</usg>)?(<sense><def[^<]+</def></sense>\s?)?<xr><lbl>↗</lbl><ref[^<]+<hi[^<]+(<hi[^<]+</hi>)?</hi></ref></xr>\.?</p></entry>', tei)
    for match in matches:
        repl = match[0].replace(r'<entry>', r'<entry type="relatedEntry">')
        # inserting <mark/> in order to mark referencing entries (necessary for finding beginning of etym section)
        repl = repl.replace(r'</entry>', r'<mark/></entry>')
        tei = tei.replace(match[0], repl)
    return tei


def delete_hi_rendition(tei):
    '''Deletes remaining <hi>-tags with type="rendition".'''
    
    # step 1: rename <hi rend="italics" und "superscript"> temporarily into <t>-tags
    tei = re.sub(r'<hi(\srend="superscript">[^<]+)</hi>', r'<t\1</t>', tei)
    tei = re.sub(r'<hi(\srend="italics">[^<]+((<t[^<]+</t>)?[^<]?)*)</hi>', r'<t\1</t>', tei)
    
    # step 2: delete <hi rendition>-tags
    tei = re.sub(r'<hi rendition="font5"[^>]*>', '', tei)
    tei = tei.replace('</hi>', '')
    
    # rename <t> into <hi>
    tei = tei.replace('<t rend', '<hi rend')
    tei = tei.replace('</t>', '</hi>')
    
    return tei


def mark_etym(tei):
    '''Marks etymological section with '<etym type="undefined">'.'''
    
    # mark beginning:
    tei = re.sub(r'((</date>)?</usg>\)(.|,)\s)', r'\1<etym type="undefined">', tei)
    # mark end
    # case 1: with following bibliographical section
    tei = re.sub(r'(</p><note type="referencingSection">)', r'</etym>\1', tei)
    # case 2: without following bibliographical section
    tei = re.sub(r'(</p></entry>)', r'</etym>\1', tei)
    
    # delete <mark/>
    tei = tei.replace('<mark/>', '')
    
    return tei

def rename_note_seg(tei):
    '''Renames <note type="translation"> as <seg type="translation">'''
    tei = re.sub(r'<note type="translation">', r'<seg type="translation">', tei)
    tei = re.sub(r'<trans/></note>', r'</seg>', tei)
    
    return tei

def rename_note_etym(tei):
    '''Renames <note type="addition"> as <seg type="addition"> and inserts <etym>'''
    tei = re.sub(r'<note type="addition">', r'<seg type="addition"><etym type="undefined">', tei)
    tei = re.sub(r'<add/></note>', r'</etym></seg>', tei)
    
    return tei


def mark_bibl_note(tei):
    '''Inserts <note> around additons in <bibl>.'''
    tei = re.sub(r'(<bibl>[^<]+)(\([^\^\d)]+\))', r'\1<note type="bibl">\2</note>', tei)
    
    return tei


def delete_p(tei):
    '''Deletes <p>-tags.'''
    
    tei = tei.replace('<p>', '')
    tei = tei.replace('<p rendition="font4">', '')
    tei = tei.replace('</p>', '')
    return tei


def mark_missing_orth(tei):
    ''' Adds missing <orth>-tags around word forms with <hi rend="superscript">.'''
    
    tei = re.sub(r'((?<!"entry">)(?<!<orth>)<hi rend="italics">[^<]+(<hi[^<]+</hi>)?[^<]*</hi>)', r'<cit type="etymologicalForm"><form xml:lang=""><orth>\1</orth></form></cit>', tei)
    return tei


def correct_cit(tei):
    ''' Deletes <cit>, <form> and <orth> in case of mistaken word forms.'''

    # single character in <cit> followed by hyphen + certain strings
    tei = re.sub(r'<cit type="etymologicalForm"><form xml:lang="xxx"><orth><hi rend="italics">(\w)</hi></orth></form></cit>(-(Suffix|Präfix|Ableitung|Bildung|Stufe|Stamm|stämmig))', r'<mark>\1</mark>\2', tei)
    tei = re.sub(r'<cit type="etymologicalForm"><form xml:lang="xxx"><orth><hi rend="italics">(\w-)</hi></orth></form></cit>((Suffix|Präfix|Ableitung|Bildung|Stufe|Stamm|stämmig))', r'<mark>\1</mark>\2', tei)
    
    # s mobile
    tei = re.sub(r'<cit type="etymologicalForm"><form xml:lang="xxx"><orth><hi rend="italics">(s mobile)</hi></orth></form></cit>', r'<mark>\1</mark>', tei)
    tei = re.sub(r'<cit type="etymologicalForm"><form xml:lang="xxx"><orth><hi rend="italics">(s)</hi></orth></form></cit>(mobile)', r'<mark>\1</mark>\2', tei)
    
    return tei


def delete_hi_cit_ref(tei):
    '''Deletes '<hi rend="italics">' in <cit> and <ref>.'''
    
    # step 1: rename <hi rend="superscript"> into <temp>:
    tei = re.sub(r'<hi rend="superscript">([^<]+)</hi>', r'<temp>\1</temp>', tei)
    
    # step 2: delete remaining <hi>-tags
    tei = re.sub(r'<hi rend="italics">', '', tei)
    tei = re.sub(r'</hi>', r'', tei)
    
    # step 3: rename <temp> into <hi>
    tei = re.sub(r'<temp>', r'<hi rend="superscript">', tei)
    tei = re.sub(r'</temp>', r'</hi>', tei)
    tei = re.sub(r'<mark>', r'<hi rend="italics">', tei)
    tei = re.sub(r'</mark>', r'</hi>', tei)

    return tei


def correct_dateGroup(tei):
    '''
    Modifies date annotation. <seg> ist deleted, each <date> is embedded in its own <usg>.
    Changes are necessary because during the annotation process it became clear that <def>
    isn't allowed within <seg> or <usg>.
    '''
    # case 1a: one date (standard)
    tei = re.sub(r'(?P<begin><usg type="time" ana="date">)<date>(?P<firstOcc><date type="firstOccurrence[^>]+>\d+. Jh.</date>)</date>(?P<end></usg>)', r'\g<begin>\g<firstOcc>\g<end>', tei)
    
    # case 1b: one date +  additional text/word form/meaning
    tei = re.sub(r'(?P<begin><usg[^>]+>)<date>(?P<first><date[^<]+</date>)</date>(?P<end>,\s([^<]|<cit[^>]+><form[^>]+><orth[^<]+</orth></form></cit>)+)</usg>', r'\g<begin>\g<first></usg>\g<end>', tei)
    
    # case 2a: two dates + etymological form + possibly meaning/additional text 
    tei = re.sub(r'(?P<begin><usg[^>]+>)<date>(?P<firstOcc><date[^>]+>\d+. Jh.</date>)</date>(?P<sep>,\s)<date><seg type="dateLabel">\s*(?P<cit>[^<]*<cit[^>]+><form xml:lang[^<]+><orth>[^<]+</orth></form></cit>\.?)(?P<def><def>[^<]+</def>)*\s*</seg>(?P<second><date[^>]+>\s*\d+. Jh.</date>)</date>(?P<end></usg>)', r'\g<begin>\g<firstOcc></usg>\g<sep>\g<cit>\g<def>\g<begin>\g<second>\g<end>', tei)  
    
    # case 2b: two dates + Label "Form"/explication/meaning 
    tei = re.sub(r'(?P<begin><usg[^>]+>)<date>(?P<firstOcc><date[^>]+>\d+. Jh.</date>)</date>(?P<sep>,\s)<date><seg type="dateLabel">(?P<form>([^<]|<term[^<]+</term>|<def[^<]+</def>)+)</seg>(?P<second>\s*<date[^>]+>\s*\d+. Jh.</date>)</date>(?P<end></usg>)', r'\g<begin>\g<firstOcc></usg>\g<sep>\g<form>\g<begin>\g<second>\g<end>', tei)
    
    # case 2c: two dates: language as label
    tei = re.sub(r'(?P<begin><usg[^>]+>)<date>(?P<firstOcc><date[^>]+>\d+. Jh.</date>)</date>(?P<sep>,\s)<date><seg type="dateLabel">(?P<label>\s*<lang[^<]+</lang>)</seg>(?P<second>\s*<date[^>]+>\s*\d+. Jh.</date>)</date>(?P<end></usg>)', r'\g<begin>\g<firstOcc></usg>\g<sep>\g<label>\g<begin>\g<second>\g<end>', tei)
    
    # case 3: missing date
    tei = re.sub(r'(<usg type="time" ana="date">)<date>(<date type="firstOccurrence">-</date>)</date>(</usg>)', r'\1\2\3', tei)
    
    # moving <lang> into <usg>
    tei = re.sub(r'(<lang[^<]+</lang>)(<usg type="time"\sana="date">)', r'\2\1', tei)
    
    return tei


def correct_lemmaGroup(tei):
    '''special case entry 'Leumund': lemmaGroup is interrupted by addition with reference;
       limits of lemmaGroup have to be moved because <xr> isn't permitted in <form>.
    '''
    tei = re.sub(r'(<form type="lemmaGroup"><form type="lemma"><orth>Leumund </orth></form>)(\(durch <cit type="etymologicalForm"><form[^>]+><orth>Ruf </orth></form></cit>\[<xr><lbl>↗</lbl><ref[^>]+>rufen</ref></xr>\] ersetzt\) <gramGrp><gram[^>]+>S</gram><gram[^>]+>m</gram></gramGrp>)</form>', r'\1</form>\2', tei)
    return tei


def mark_section(tei):
    ''' Annotates the complete section 'L' with '<div xml:id="L" type="section">' and inserts '<head>L</head>'.'''
    
    tei = tei.replace('<body>', '<body><div xml:id="L" type="section"><head>L</head>')
    tei = tei.replace('</body>', '</div></body>')
    
    return tei
    
    
# === Coordinating function ===    
    
def main(tei):
    print("--- 12_finish_markup.py running")
    tei = type_relatedEntry(tei)
    tei = delete_hi_rendition(tei)
    tei = mark_etym(tei)
    tei = rename_note_seg(tei)
    tei = rename_note_etym(tei)
    tei = mark_bibl_note(tei)
    tei = delete_p(tei)
    tei = mark_missing_orth(tei)
    tei = correct_cit(tei)
    tei = delete_hi_cit_ref(tei)
    tei = correct_dateGroup(tei)
    tei = correct_lemmaGroup(tei)
    tei = mark_section(tei)
    print("... done!")
    return tei