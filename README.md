# Reccueil des Actes Administratifs préfectoraux

Scripts de téléchargement des RAA disponibles sur les sites web des préfectures.

## Principe

raa.csv: contient les URL de base des pages donnant accès aux RAA.

scrap.py : récupére les pages puis les analyse pour télécharger les fichiers PDF correspondants.

extract.py : extrait le contenu textuel des fichiers PDF

## Dépendances

requests : pour récupération des pages et PDF

Beautifulsoup: pour l'analyse de l'HTML des pages web

PyPDF2 : pour analyse des PDF

Pour installation:

`pip install -r requirements.txt`
