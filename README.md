# Aligneur unilingue

## Ce qu'est l'outil
L'outil qui est présenté ici vise à répondre à un problème simple: la collation microscropique est 
bien explorée par la recherche, mais quid de la collation macroscopique ? Comment aligner automatiquement de façon globale des textes
*similaires* (*id est*, que l'on peut collationer), en utilisant la TEI

## Ce que n'est pas l'outil
Un aligneur de versions linguistiques différentes ou de textes semblables mais non similaires (*id est* des textes non collationables)

## Idées

- le but de l'outil est de structurer *n* textes à partir d'un texte modèle encodé en XML-TEI


### Fonctionnement précis

#### Pré-requis
- on peut poser que la complexité du corpus est faible: on s'attend à ce que tous les textes soient relativement similaires 
  au niveau macro: cas d'une partie des corpus à éditer. L'outil ne peut en l'état reconnaître des déplacements
  de texte importants.
  
#### Formats

Le document base à partir duquel structurer les autres documents est structuré en XML-TEI. Les documents doivent être tokénisés et lemmatisés. 


#### xPath

La structure à aligner est indiquée à l'aide de requêtes XPATH: une requête qui permet de proposer un contexte (une partie par exemple), 
et une requête qui va chercher la structure précise (un titre, un paragraphe, une sous-partie).

L'outil est une aide à l'alignement et reste peu efficace en cas de gros changement structurel. Il
est efficace en interaction avec l'utilisateur.ice, qui viendra corriger à la main les erreurs ou impasses 
de l'alignement automatique. Un fichier de log vient indiquer les divisions qui n'ont pu être alignées.

L'outil est ainsi aussi efficace pour repérer les différences structurelles entre témoins.

Il est possible de fonctionner de façon progressive (chapitre par chapitre par exemple), 
ou par structure (les chapitres, les titres, les sous-chapitres, les paragraphes).


## Fonctionnement
1) Structuration en XML-TEI d'un texte
2) Structuration minimale des autres textes (teiHeader, text, pb, lb, rubriques si récupéré automatiquement) OU récupération en texte brut
3) Tokénisation et lemmatisation
4) Récupération des pré-échantillons (estimation de la fin d'une division)
5) Alignement sur les pré-échantillons (début, fin de chaîne?) et re-calcul au besoin


