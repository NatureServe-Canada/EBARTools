Paquet ZIP pour le project Cartographie automatisée des aires de répartissaient basée sur les écosystèmes (CAARBE) pour une catégorie d'espèces/un groupe taxonomique sélectionné(e)
© NatureServe Canada 2026 sous CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/deed.fr)

Ce paquet ZIP devrait contenir les fichiers suivants :
- EBARxxxxx.pdf (carte et métadonnées pour CAARBE pour chaque espèce au sein d'une catégorie/d'un groupe de taxons)
- EBARMethods.pdf (informations générales sur la production de cartes des aires de répartition, les sources d'écoshape et les sujets connexes)
- Ecoshape.* (fichiers comprenant des polygones fichier de forme de tous les écoshapes)
- EcoshapeOverview.* (fichiers comprenant des polygones fichier de forme de tous les écoshapes généralisés)
- RangeMap.csv (tableau des espèces et des attributs de l'aire de répartition pour EBAR pour toutes les espèces au sein de la catégorie/groupe taxonomique)
- RangeMapEcoshape.csv (tableau des attributs par écoshape pour CAARBE pour toutes les espèces dans la catégorie/le groupe de taxons)
- Jurisdiction.csv (tableau des juridictions)
- EBARxxxxx.aprx (fichier de projet ArcGIS Pro pour chaque espèce au sein d'une catégorie ou d'un groupe de taxons, faisant référence aux fichiers de données ci-dessus, avec des requêtes de définition et des jointures appropriées)
- EBARxxxxx.mapx (fichier cartographique ArcGIS Pro pour chaque espèce au sein d'une catégorie ou d'un groupe de taxons, faisant référence aux fichiers de données ci-dessus, avec les requêtes de définition et les jointures appropriées)
- EBARxxxxxEcoshape.lyrx (fichier de couche ArcGIS Pro pour chaque espèce au sein d'une catégorie ou d'un groupe de taxons, avec une symbologie suggérée et des requêtes de définition et des jointures appropriées, faisant référence aux écopaysages d'origine)
- EBARxxxxxEcoshapeOverview.lyrx (fichier de couche ArcGIS Pro pour chaque espèce au sein d'une catégorie ou d'un groupe de taxons, avec des suggestions de symbologie et des requêtes de définition, ainsi que des jointures appropriées, faisant référence aux écopaysages généralisés)
- EBARyyyyy.mxd (fichier de projet ArcMap faisant référence aux fichiers de données ci-dessus)
- Ecoshape.lyr (fichier de couche ArcMap, avec symbologie suggérée et jointures appropriées, faisant référence aux écoshapes originaux)
- EcoshapeOverview.lyr (fichier de couche ArcMap, avec symbologie suggérée et jointures appropriées, faisant référence aux écoshapes généralisés)
- UsageType.lyr (fichier de couche ArcMap, avec symbologie suggérée et jointures appropriées, faisant référence au type d'utilisation, le cas échéant, des écoshapes généralisés)
[où xxxxx est l'ELEMENT_GLOBAL_ID de l'espèce sélectionnée]
[où yyyyy correspond au nom de la catégorie/du groupe taxonomique]
[REMARQUE : les fichiers de projet et de couche ArcMap devront faire l'objet d'une requête de définition appliquée à chaque couche - « RangeMapID = yyy », où yyy correspond à une valeur RangeMapID appropriée issue du fichier RangeMap.csv]

Les fichiers de données inclus sont liés comme suit :
RangeMap <-1---M-> RangeMapEcoshape
Ecoshape/EcoshapeOverview <-1---M-> RangeMapEcoshape
Jurisdiction <-1---M-> Ecoshape/EcoshapeOverview

Champs RangeMap :
objectid - identifiant unique ArcGIS
RangeMapID - identifiant unique CAARBE
RangeVersion - numéro de version CAARBE
RangeStage - étape CAARBE dans la version (par exemple, généré automatiquement, examiné par des experts)
RangeDate - date de génération
RangeMapScope - portée géographique (par exemple, N = Canadien, A = Nord-américain, G = mondial)
RangeMetadata - nombre d'enregistrements d'entrée par source, et nombre et détails (si publiables) des examens par des experts
RangeMapNotes - détails sur le(s) nom(s) de l'espèce
RangeMapComments - notes supplémentaires
SynonymsUsed - liste des synonymes, le cas échéant, pour l'espèce principale sous laquelle les données d'entrée utilisées ont été importées
DifferentiateUsageType - 1 si le type d'utilisation (reproduction, reproduction possible, migration) est différencié par écoshape
ELEMENT_NATIONAL_ID - identifiant unique national NatureServe Biotics
ELEMENT_GLOBAL_ID - identifiant unique mondial NatureServe Biotics
ELEMENT_CODE - identifiant d'élément NatureServe Biotics
CATEGORY - catégorie d'espèce NatureServe Biotics
TAX_GROUP - groupe taxonomique d'espèce NatureServe Biotics
FAMILY_COM - nom commun de la famille d'espèce NatureServe Biotics
GENUS - genre d'espèce NatureServe Biotics
PHYLUM - embranchement NatureServe Biotics
CA_NNAME_LEVEL - nom Canadien de l'espèce NatureServe Biotics
NATIONAL_SCIENTIFIC_NAME - nom scientifique de l'espèce Canadienne NatureServe Biotics
NATIONAL_ENGL_NAME - nom Anglais de l'espèce Canadienne NatureServe Biotics
NATIONAL_FR_NAME - nom Français de l'espèce Canadienne NatureServe Biotics
COSEWIC_NAME - nom de l'espèce COSEPAC NatureServe Biotics
COSEWIC_ID - identifiant de l'espèce COSEPAC NatureServe Biotics
ENDEMISM_TYPE - type d'endémisme de l'espèce NatureServe Biotics
GRANK - classement mondial de l'espèce NatureServe Biotics
NRANK_CA - classement national Canadien de l'espèce NatureServe Biotics
SRANKS_CA - classements infranationaux Canadiens de l'espèce NatureServe Biotics
NRANK_US - classement national Américain de l'espèce NatureServe Biotics
SRANKS_US - NatureServe Biotics species United States subnational ranksclassements infranationaux Américains de l'espèce NatureServe Biotics
NRANK_MX - NatureServe Biotics espèce rang national au Mexique
SRANKS_MX - NatureServe Biotics espèce rangs infranationaux au Mexique
SARA_STATUS - NatureServe Biotics espèce statut en vertu de la Loi sur les espèces en péril au Canada
COSEWIC_STATUS - NatureServe Biotics espèce statut en vertu du Comité sur la situation des espèces en péril au Canada
ESA_STATUS - NatureServe Biotics espèce statut en vertu de la Loi Américaine sur les espèces en voie de disparition

Champs RangeMapEcoshape :
objectid - identifiant unique ArcGIS
RangeMapID - clé étrangère CAARBE relative à l'enregistrement RangeMap approprié
EcoshapeID - clé étrangère CAARBE relative à l'enregistrement Ecoshape/EcoshapeOverview approprié
Presence - catégorie de présence de l'espèce dans l'écoshape (P = Présente, X = Présence attendue, H = Historique, NULL = Supprimée*, voir le PDF des métadonnées pour les définitions)
UsageType - type d'utilisation de l'espèce dans l'écoshape (B = Reproduction, P = Reproduction possible, M = Migration, voir le PDF des métadonnées pour les définitions)
RangeMapEcoshapeNotes - nombre d'enregistrements saisis par source et commentaires des réviseurs, s'ils peuvent être publiés
MinDate - date la plus ancienne pour tous les enregistrements saisis qui chevauchent l'écoshape
MaxDate - date la plus récente pour tous les enregistrements saisis qui chevauchent l'écoshape

[*Les écoshapes supprimées au cours du processus de révision par des experts sont incluses avec Présence=NULL et le champ RangeMapEcoshapeNotes contenant les commentaires des réviseurs, s'ils peuvent être publiés.]

Champs Jurisdiction :
objectid - identifiant unique ArcGIS
JurisID - identifiant unique CAARBE
JurisAbbrev - code à deux lettres pour la juridiction
JurisName - nom complet de la juridiction

Champs Ecoshape/EcoshapeOverview :
FID - identifiant unique ArcGIS
EcoshapeID - identifiant unique CAARBE
JurisID - clé étrangère CAARBE relative à l'enregistrement de la juridiction appropriée
EcoName - nom de l'écoshape
ParentEco - nom Anglais de l'écorégion parentale
ParentEcoF - nom Français de l'écorégion parentale
Ecozone - nom Anglais de l'écozone
EcozoneFR - nom Français de l'écozone
MosaicVer - version de la mosaïque d'écoshape
TerrArea - superficie terrestre en mètres carrés dérivée de la Commission de coopération écologique «Grands lacs et réservoirs d'Amérique du Nord»
TotalArea - superficie totale en mètres carrés

Avertissement :
- Veuillez consulter notre document sur les méthodes à l'adresse https://1drv.ms/b/s!Ajv6BHSXrqqqm4xipeEOQ67IfH77IQ?e=dqM1FO avant d'utiliser CAARBE.
- Les données CAARBE sont relativement grossières et conviennent à des fins de dépistage et d'éducation, mais ne sont pas destinées à tous les types d'applications et d'analyses.
- L'absence de données dans une zone géographique ne signifie pas nécessairement qu'une espèce n'y est pas présente.
- Un écoshape avec une valeur de présence ne signifie pas nécessairement qu'une espèce est présente dans toute la zone géographique.

Citation de plusieurs espèces : NatureServe Canada. 2026. Le project Cartographie automatisée des aires de répartissaient basée sur les écosystèmes (CAARBE). Ottawa, Canada. Consulté le [insérer la date] sur [insérer l'URL]
Citation d'une seule espèce : NatureServe Canada. 2023. Le project Cartographie automatisée des aires de répartissaient basée sur les écosystèmes (CAARBE) pour [insérer le nom de l'espèce, la version, le stade et la portée]. Ottawa, Canada. Consulté le [insérer la date] sur [insérer l'URL]
