Ensemble de fichiers ZIP pour le project Cartographie automatisée des aires de répartissaient basée sur les écosystèmes (CAARBE) pour certaines espèces
© NatureServe Canada 2026 sous CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/deed.fr)

Cet ensemble de fichiers ZIP doit contenir les fichiers suivants :
- EBARxxxxx.pdf (carte et métadonnées CAARBE pour certaines espèces)
- EBARMethods.pdf (informations générales sur la production de cartes de répartition, les sources d'écocoupes et les sujets connexes)
- Ecoshape.* (fichiers comprenant un fichier de formes polygonales des formes écologiques originales pour CAARBE pour certaines espèces)
- EcoshapeOverview.* (fichiers comprenant un fichier de formes polygonales des formes écologiques généralisées pour CAARBE pour certaines espèces)
- UsageType.* (le cas échéant, fichiers comprenant un fichier de formes polygonales du type d'utilisation, des formes écologiques généralisées pour CAARBE pour certaines espèces)
- RangeMap.csv (tableau des espèces et des attributs de l'aire de répartition pour CAARBE pour certaines espèces)
- RangeMapEcoshape.csv (tableau des attributs par forme écologique pour CAARBE pour certaines espèces)
- Jurisdiction.csv (tableau des juridictions)
- EBARxxxxx.aprx (fichier de projet ArcGIS Pro référençant les fichiers de données ci-dessus, avec les jointures appropriées)
- EBARxxxxx.mapx (fichier de carte ArcGIS Pro référençant les fichiers de données ci-dessus, avec les jointures appropriées)
- EBARxxxxxEcoshape.lyrx (fichier de couche ArcGIS Pro, avec la symbologie suggérée et les jointures appropriées, référençant les écosystèmes d'origine)
- EBARxxxxxEcoshapeOverview.lyrx (fichier de couche ArcGIS Pro, avec la symbologie suggérée et les jointures appropriées, référençant les écosystèmes généralisés)
- EBARxxxxxRemovedEcoshapes.lyrx (fichier de couche ArcGIS Pro, avec les jointures appropriées, affichant uniquement les écoformes qui ont été supprimées à la suite de l'examen par les experts, référençant les écoformes généralisées)
- EBARxxxxxUsageType.lyrx (le cas échéant, fichier de couche ArcGIS Pro, avec la symbologie suggérée et les jointures appropriées, référençant le type d'utilisation des écoformes généralisées)
- EBARxxxxx.mxd (fichier de projet ArcMap faisant référence aux fichiers de données ci-dessus)
- EBARxxxxxEcoshape.lyr (fichier de couche ArcMap, avec la symbologie suggérée et les jointures appropriées, faisant référence aux formes écologiques d'origine)
- EBARxxxxxEcoshapeOverview.lyr (fichier de couche ArcMap, avec la symbologie suggérée et les jointures appropriées, faisant référence aux formes écologiques généralisées)
- EBARxxxxxRemovedEcoshapes.lyr (fichier de couche ArcMap, avec les jointures appropriées, affichant uniquement les formes écologiques qui ont été supprimées à la suite de l'examen par des experts, faisant référence aux formes écologiques généralisées)
- EBARxxxxxUsageType.lyr (fichier de couche ArcMap, avec symbologie suggérée et jointures appropriées, référençant le type d'utilisation des formes écologiques généralisées)
[où xxxxx est l'ELEMENT_GLOBAL_ID de l'espèce sélectionnée]

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
DifferentiateUsageType - 1 si le type d'utilisation (reproduction, reproduction possible, migration) est différencié par forme écologique
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
Presence - catégorie de présence de l'espèce dans l'Ecoshape (P = Présente, X = Présence attendue, H = Historique, NULL = Supprimée*, voir le PDF des métadonnées pour les définitions)
UsageType - type d'utilisation de l'espèce dans l'Ecoshape (B = Reproduction, P = Reproduction possible, M = Migration, voir le PDF des métadonnées pour les définitions)
RangeMapEcoshapeNotes - nombre d'enregistrements saisis par source et commentaires des réviseurs, s'ils peuvent être publiés
MinDate - date la plus ancienne pour tous les enregistrements saisis qui chevauchent l'Ecoshape
MaxDate - date la plus récente pour tous les enregistrements saisis qui chevauchent l'Ecoshape

[*Les Ecoshapes supprimées au cours du processus de révision par des experts sont incluses avec Présence=NULL et le champ RangeMapEcoshapeNotes contenant les commentaires des réviseurs, s'ils peuvent être publiés.]

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
MosaicVer - version de la mosaïque de l'écoshape
TerrArea - superficie terrestre en mètres carrés dérivée de la Commission de coopération écologique «Grands lacs et réservoirs d'Amérique du Nord»
TotalArea - superficie totale en mètres carrés

Avertissement :
- Veuillez consulter notre document sur les méthodes à l'adresse https://1drv.ms/b/s!Ajv6BHSXrqqqm4xipeEOQ67IfH77IQ?e=dqM1FO avant d'utiliser CAARBE.
- Les données CAARBE sont relativement grossières et conviennent à des fins de dépistage et d'éducation, mais ne sont pas destinées à tous les types d'applications et d'analyses.
- L'absence de données dans une zone géographique ne signifie pas nécessairement qu'une espèce n'y est pas présente.
- Une forme écologique avec une valeur de présence ne signifie pas nécessairement qu'une espèce est présente dans toute la zone géographique.

Citation de plusieurs espèces : NatureServe Canada. 2026. Le project Cartographie automatisée des aires de répartissaient basée sur les écosystèmes (CAARBE). Ottawa, Canada. Consulté le [insérer la date] sur [insérer l'URL]
Citation d'une seule espèce : NatureServe Canada. 2023. Le project Cartographie automatisée des aires de répartissaient basée sur les écosystèmes (CAARBE) pour [insérer le nom de l'espèce, la version, le stade et la portée]. Ottawa, Canada. Consulté le [insérer la date] sur [insérer l'URL]
