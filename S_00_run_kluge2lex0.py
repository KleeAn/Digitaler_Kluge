#!/usr/bin/env python3
'''
SCRIPT 00:
Coordinating script for converting OCR-recognised HTML-text of
section "L" of Kluge "Etymologisches Wörterbuch der deutschen Sprache"
into TEI-Lex-0.

Input:
    Files listed under "Parameters"
Output:
    - "kluge_lex0.xml" : section "L" annotated according to TEI Lex-0
    - "literature.xml", "periodicals.xml", "terminology.xml": tagged chapters necessary to link information
    - CSV-files as interstage products: "pos_tofill.csv", "usg_tofill.csv", "languages.csv", "languages_cap.csv", "term.csv"
'''
# === Imports ===

import S_01_helpers
import S_03_kluge2validtei
import S_04_create_csv_pos_lexis
import S_05_mark_entry_head
import S_06_mark_bibl
import S_07_mark_lang
import S_08_mark_etym
import S_09_mark_translation_addition
import S_10_mark_term_chapter
import S_11_mark_term
import S_12_finish_markup
import S_13_mark_literature_list
import S_14_mark_periodicals_list
import S_15_add_attributes
import S_16_sort_attributes


# === Parameters ===

htmlfile = "kluge_L.html"
headerfile = "header_L.txt"

# --- lexis/style ---
lexis_file = "lexis.txt"
lexis_csv = "lexis.csv"

# --- grammar ---
pos_file = "pos.txt"
pos_csv = "pos.csv"

# --- languages ---
lang_file = "languages.txt"
lang_csv = "languages_norm.csv"
lang_cap_csv = "languages_cap_norm.csv"

# --- terms ---
term_file = "terminology.txt"
term_header = "header_terminology.txt"
reg_file = "register.txt"

# --- literature and periodicals ---
literature_file = "literature.txt"
literature_header = "header_literature.txt"
literature_xml = "literature.xml"
periodicals_file = "periodicals.txt"
periodicals_header = "header_periodicals.txt"
periodicals_xml = "periodicals.xml"


# === Coordinating function ===

def main():
    tei = S_03_kluge2validtei.main(htmlfile, headerfile)
    S_04_create_csv_pos_lexis.main(lexis_file, pos_file)
    tei = S_05_mark_entry_head.main(tei, lexis_csv, pos_csv)
    tei = S_06_mark_bibl.main(tei)
    tei = S_07_mark_lang.main(tei, lang_file)
    tei = S_08_mark_etym.main(tei, pos_csv)
    tei = S_09_mark_translation_addition.main(tei)
    S_10_mark_term_chapter.main(term_file, term_header, reg_file)
    tei = S_11_mark_term.main(tei, reg_file)
    tei = S_12_finish_markup.main(tei)
    S_13_mark_literature_list.main(literature_file, literature_header)
    S_14_mark_periodicals_list.main(periodicals_file, periodicals_header)
    tei = S_15_add_attributes.main(tei, periodicals_xml, literature_xml, lang_csv, lang_cap_csv)
    tei = S_16_sort_attributes.main(tei)
    S_01_helpers.save_file(tei, "kluge_lex0.xml")
    

main()