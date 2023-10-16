# Aligneur unilingue

## Ce qu'est l'outil
L'outil qui est présenté ici vise à répondre à un problème simple: la collation microscropique est 
bien explorée par la recherche, mais quid de la collation macroscopique ? Comment aligner automatiquement de façon globale des textes
*similaires* (*id est*, que l'on peut collationer), en utilisant la TEI

## Ce que n'est pas l'outil
Un aligneur de versions linguistiques différentes ou de textes semblables mais non similaires (*id est* des textes non collationables)

## Idées

- le but de l'outil est de structurer *n* textes à partir d'un texte modèle encodé en XML-TEI
- on fera usage d'un aligneur existant comme CollateX
- il y a un problème dans CollateX à aligner des séquences longues. Voir si cela suppose de changer d'aligneur.
  

### Fonctionnement précis

#### Pré-requis
- on peut poser que la complexité du corpus est faible: on s'attend à ce que tous les textes soient relativement similaires 
  au niveau macro.   
  
#### Formats
Le document base est structuré en XML-TEI, donc déjà divisé. 


#### Structure

On va travailler selon la structure du document source. 
Quel ordre ? Faire peu à peu ou en changeant la granularité niveau par niveau ?
Laisser la possibilité à l'utilisateur, en faisant des tests


## Besoins
La tokénisation et la lemmatisation du corpus est un plus.


## Premières idées

- On peut commencer par imaginer faire des divisions arbitraires 
  en utilisant des comptages de mots. on va prendre la longueur en mot de la division-base à retrouver; puis on va lui ajouter 10 ou 20%; et on va 
  pré-découper le texte cible. Il faudra ensuite aligner le début et la fin du texte? le texte entier?
  

## Fonctionnement
1) Structuration en XML-TEI d'un texte
2) Structuration minimale des autres textes (teiHeader, text, pb, lb, rubriques si récupéré automatiquement) OU récupération en texte brut
3) Tokénisation et lemmatisation
4) Récupération des pré-échantillons
5) Alignement sur les pré-échantillons (début, fin de chaîne?) et re-calcul au besoin

## Corpus du test

Travailler sur le Regimiento et les textes déjà structurés ? A et Z
Valider avec Ayala pour voir sur des textes pas structurés ?