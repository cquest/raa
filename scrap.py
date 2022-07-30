#! /usr/bin/python3

import csv, json, sys, re, os, subprocess, urllib, urllib3

import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader

urllib3.disable_warnings()

mois_noms = {
    '01': 'janvier',
    '02': 'fevrier',
    '03': 'mars',
    '04': 'avril',
    '05': 'mai',
    '06': 'juin',
    '07': 'juillet',
    '08': 'aout',
    '09': 'septembre',
    '10': 'octobre',
    '11': 'novembre',
    '12': 'decembre'
}
dep = sys.argv[1] if len(sys.argv) > 1 else None
annee = '2020' if len(sys.argv)<3 else sys.argv[2]
mois_mm = '10' if len(sys.argv)<4 else sys.argv[3]
mois = mois_noms[mois_mm]

liste_raa = csv.DictReader(open('raa.csv'))
for raa in liste_raa:
    # pour ne traiter qu'un département (debug)
    if dep and dep != raa['dep']:
        continue

    url_raa = raa['url'].replace('!annee!',annee)
    url_raa = url_raa.replace('!mois!', mois)
    url_raa = url_raa.replace('!Mois!', mois.capitalize())
    url_raa = url_raa.replace('!MOIS!', mois.upper())
    url_raa = url_raa.replace('!MM!', mois_mm)
    print("RAA "+raa['url']+" -> "+url_raa)
    web = requests.get(url_raa, verify=False, headers={"user-agent": "Mozilla/4.0"})
    if web.status_code != 200:
        print("HTTP ERROR", web.status_code)
        continue

    # parsing URL d'origine du RAA
    parsed_url = urllib3.util.parse_url(raa['url'])
    host = parsed_url.scheme+"://" + parsed_url.netloc
    base = host + re.sub(r'^.*/','/',parsed_url.path)

    # création du dossier de stockage
    try:
        os.mkdir('data/'+raa['dep'])
    except:
        pass


    # parsing de la page web
    html = BeautifulSoup(web.text, 'html.parser')

    if 'ezjscore' in web.text:
        for link in html.find_all('a'):
            url = link.get('href')
            print(url)
            if 'ezjscore' in url:
                url = url.replace('::10::10::','::0::1000::')
                print(url)
                web = requests.get(url, verify=False, headers={"user-agent": "Mozilla/4.0"})
                # parsing de la page web
                html = BeautifulSoup(web.text, 'lxml')
                print(html)


    # analyse des liens
    for link in html.find_all('a'):
        url = link.get('href')
        # lien vers un fichier PDF
        if url and url[-4:] == '.pdf':
            titre = link.get('title')
            # nettoyage du titre du document
            if titre:
                titre = titre.replace('Ouvrir le document ','')
                titre = titre.replace(' dans une nouvelle fenêtre','')
                titre = titre.replace(' (ouverture nouvelle fenêtre)', '')
                titre = titre.replace('- pdf ', '')
                titre = titre.replace('format pdf', '')
                titre = re.sub(r' - [0-9\.\,]* [kM][ob]','',titre)

            filename = re.sub(r'^.*/','',url)
            if url[0] == '/':
                url = host + url
            elif url[:4] != 'http':
                url = host + '/' + url
 
            filepath = "data/"+raa['dep']+"/"+urllib.parse.unquote(filename)
            # téléchargement du fichier PDF si absent
            if not os._exists(filepath):
                subprocess.run("wget -nc -nv --no-check-certificate --header='User-Agent: Mozilla/5.0' -P %s \"%s\" " %
                            ("data/"+raa['dep'], url), shell=True)

            # traitement du fichier pour extraction des métadonnées                
            try:
                pdf = PdfFileReader(open(filepath, "rb"))
                meta = {
                    'filename': filename,
                    'url': url,
                    'pages': len(pdf.pages),
                    'docinfo' : pdf.getDocumentInfo()
                    }
                with open(filepath+'.meta', "w") as metafile:
                    metafile.write(json.dumps(meta))
            except:
                print("PDF ERR : ",filepath)
                pass
            