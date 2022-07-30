#! /usr/bin/python3

import sys, json

from PyPDF2 import PdfFileReader


from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

def convert_pdf_to_string(file_path, pagenum):

    output_string = StringIO()
    with open(file_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            pagenum -= 1
            if pagenum == 0:
                interpreter.process_page(page)
                break

    return(output_string.getvalue())



reader = PdfFileReader(sys.argv[1])
infos = reader.documentInfo

meta = {'filename': sys.argv[1], 'pages': reader.getNumPages()}
if '/CreationDate' in infos:
    meta['creationDate'] = infos['/CreationDate'][2:6] + '-' + infos['/CreationDate'][6:8]+ '-' + infos['/CreationDate'][8:10]

if '/Producer' in infos and infos['/Producer'] == 'FPDF 1.7':
    # page de titre
    page = 1
    txt = convert_pdf_to_string(sys.argv[1],page).split('\n')
    if len(txt)>2:
        meta['titre'] = txt[0]+' '+txt[1]+' '+txt[2]
        #meta['date'] = txt[6].replace('PUBLIÉ LE ','').strip()

        # page(s) de sommaire
        page += 1
        txt = convert_pdf_to_string(sys.argv[1],page).split('\n')
        while txt[0] == 'Sommaire':
            print(txt)
            page += 1
            txt = convert_pdf_to_string(sys.argv[1],page).split('\n')

    print(txt)
    print(json.dumps(meta, ensure_ascii=False, indent=2))

