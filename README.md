# Digitaler_Kluge


## Porpuse

This repository contains the code that was created for my Digital Humanities Master's thesis "Der Kluge digital – Die automatisierte Retrodigitalisierung eines etymologischen Wörterbuchs durch Python-basierte Auszeichnung in XML nach den Richtlinien von TEI Lex-0".

Using the section L as an example, the thesis shows how an etymological dictionary can be retro-digitized by automated processes. The resulting encoded text may serve as the basis for an online version of the dictionary.

The purpose of the code is to mark the digital text (output of the OCR process) in XML TEI-Lex-0. 


## Requirements

The scripts are written in Python 3 so you need Python 3 on your computer. The scripts have been tested with Python 3.7.

In addition, you need to have the following packages installed: pandas, ElementTree XML.

Finally you need the text data. Please note: Since the data are protected by copyright, they may not be published on this platform.


## Input Data
**Dictionary text in HTML:**
- Kluge_L_FR_output.html (Finereader Output of chapter L; used to run S_02)
- kluge_L.html  (postprocessed recognized text of chapter L)

**Lists of literature and abbreviations in TXT:**
- languages.txt
- lexis.txt
- literature.txt
- periodicals.txt
- pos.txt
- register.txt
- terminology.txt

**Header files:**
- header_L.txt
- header_literature.txt
- header_periodicals.txt
- header_terminology.txt

**CSV files:**
- languages_norm.csv
- languages_cap_norm.csv
- lexis.csv
- pos.csv


## Output Data
- Kluge_L_FR_output_postprocessed.html: automatically corrected version of Finereader output (still has to be corrected manually)
- kluge_lex0.xml: section "L" annotated according to TEI Lex-0
- literature.xml, periodicals.xml, terminology.xml: tagged chapters necessary to link information
- pos_tofill.csv, usg_tofill.csv, languages.csv, languages_cap.csv, term.csv: interstage products used in the anntoating process


## Running the code

In order to run the code, the input data has to be stored in the same directory as the code.
(The output is written into this directory as well.)

- S_02_correct_html.py has to be run seperately. It is used to correct the Finereader output.
Please note: The output (Kluge_L_FR_output_postprocessed.html) is not used to run S_00 because it is further improved manually at first.

- Run S_00_run_kluge2lex0.py to start the annotating process. The coordinating script calls all required scripts in the required order.
