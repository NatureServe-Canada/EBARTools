Ensemble de fichiers ZIP pour le project Cartographie automatisée des aires de répartissaient basée sur les écosystèmes (CAARBE) pour certaines espèces
© NatureServe Canada 2026 sous CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/deed.fr)

Cet ensemble de fichiers ZIP doit contenir les fichiers suivants :
- CAARBExxxxx.pdf (carte et métadonnées CAARBE pour certaines espèces)
- MethodsCAARBE.pdf (informations générales sur la production de cartes de répartition, les sources d'écoshapes et les sujets connexes)
- Ecoshape.* (fichiers comprenant un fichier de formes polygonales des formes écologiques originales pour CAARBE pour certaines espèces)
- AppercuEcoshape.* (fichiers comprenant un fichier de formes polygonales des écoshapes généralisées pour CAARBE pour certaines espèces)
- UsageType.* (le cas échéant, fichiers comprenant un fichier de formes polygonales du type d'utilisation, des écoshapes généralisées pour CAARBE pour certaines espèces)
- CarteRepartition.csv (tableau des espèces et des attributs de l'aire de répartition pour CAARBE pour certaines espèces)
- CarteRepartitionEcoshape.csv (tableau des attributs par écoshape pour CAARBE pour certaines espèces)
- Juridiction.csv (tableau des juridictions)
- CAARBExxxxx.aprx (fichier de projet ArcGIS Pro référençant les fichiers de données ci-dessus, avec les jointures appropriées)
- CAARBExxxxx.mapx (fichier de carte ArcGIS Pro référençant les fichiers de données ci-dessus, avec les jointures appropriées)
- CAARBExxxxxEcoshape.lyrx (fichier de couche ArcGIS Pro, avec la symbologie suggérée et les jointures appropriées, référençant les écoshapes d'origine)
- CAARBExxxxxAppercuEcoshape.lyrx (fichier de couche ArcGIS Pro, avec la symbologie suggérée et les jointures appropriées, référençant les écoshapes généralisés)
- CAARBExxxxxEcoshapesSupprime.lyrx (fichier de couche ArcGIS Pro, avec les jointures appropriées, affichant uniquement les écoshapes qui ont été supprimées à la suite de l'examen par les experts, référençant les écoshapes généralisées)
- CAARBExxxxxTypeUtilisation.lyrx (le cas échéant, fichier de couche ArcGIS Pro, avec la symbologie suggérée et les jointures appropriées, référençant le type d'utilisation des écoshapes généralisées)
[où xxxxx est l'ELEMENT_GLOBAL_ID de l'espèce sélectionnée]

Les fichiers de projet ArcMap sont disponsible dans les fichiers ZIP anglais

Les fichiers de données inclus sont liés comme suit :
RangeMap <-1---M-> RangeMapEcoshape
Ecoshape/EcoshapeOverview <-1---M-> RangeMapEcoshape
Jurisdiction <-1---M-> Ecoshape/EcoshapeOverview

Champs CarteRepartition :
objectid - identifiant unique ArcGIS
IDCarteRepartition - identifiant unique CAARBE
VersionRepartition - numéro de version CAARBE
EtapeRepartition - étape CAARBE dans la version (par exemple, généré automatiquement, examiné par des experts)
DateRepartition - date de génération
PorteeCarteRepartition - portée géographique (par exemple, N = Canadien, A = Nord-américain, G = mondial)
MetadonneesPortee - nombre d'enregistrements d'entrée par source, et nombre et détails (si publiables) des examens par des experts
NotesCarteRepartition - détails sur le(s) nom(s) de l'espèce
CommentairesCarteRepartition - notes supplémentaires
SynonymesUtilisee - liste des synonymes, le cas échéant, pour l'espèce principale sous laquelle les données d'entrée utilisées ont été importées
TypeUtilisationDifferencie - 1 si le type d'utilisation (reproduction, reproduction possible, migration) est différencié par écoshape
ID_ELEMENT_NATIONAL - identifiant unique national NatureServe Biotics
ID_ELEMENT_MONDIAL - identifiant unique mondial NatureServe Biotics
CODE_ELEMENT - identifiant d'élément NatureServe Biotics
CATEGORIE - catégorie d'espèce NatureServe Biotics
GROUPE_TAX - groupe taxonomique d'espèce NatureServe Biotics
COM_FAMILLE - nom commun de la famille d'espèce NatureServe Biotics
GENRE - genre d'espèce NatureServe Biotics
EMBRANCHEMENT - embranchement NatureServe Biotics
NIVEAU_NOMN_CA - nom Canadien de l'espèce NatureServe Biotics
NOM_SCIENTIFIQUE_NATIONAL - nom scientifique de l'espèce Canadienne NatureServe Biotics
NOM_ANGL_NATIONAL - nom Anglais de l'espèce Canadienne NatureServe Biotics
NOM_FR_NATIONAL - nom Français de l'espèce Canadienne NatureServe Biotics
NOM_COSEPAC - nom de l'espèce COSEPAC NatureServe Biotics
ID_COSEPAC - identifiant de l'espèce COSEPAC NatureServe Biotics
TYPE_ENDEMISME - type d'endémisme de l'espèce NatureServe Biotics
CLASSEMENTM - classement mondial de l'espèce NatureServe Biotics
CLASSEMENTN_CA - classement national Canadien de l'espèce NatureServe Biotics
CLASSEMENTS_CA - classements infranationaux Canadiens de l'espèce NatureServe Biotics
CLASSEMENTN_EU - classement national Américain de l'espèce NatureServe Biotics
CLASSEMENTS_EU - NatureServe Biotics species United States subnational ranksclassements infranationaux Américains de l'espèce NatureServe Biotics
CLASSEMENTN_MX - NatureServe Biotics espèce rang national au Mexique
CLASSEMENTS_MX - NatureServe Biotics espèce rangs infranationaux au Mexique
STATUT_LEP - NatureServe Biotics espèce statut en vertu de la Loi sur les espèces en péril au Canada
STATUT_COSEPAC - NatureServe Biotics espèce statut en vertu du Comité sur la situation des espèces en péril au Canada
STATUT_ESA - NatureServe Biotics espèce statut en vertu de la Loi Américaine sur les espèces en voie de disparition

Champs CarteRepartitionEcoshape :
objectid - identifiant unique ArcGIS
IDCarteRepartition - clé étrangère CAARBE relative à l'enregistrement RangeMap approprié
IDEcoshape - clé étrangère CAARBE relative à l'enregistrement Ecoshape/EcoshapeOverview approprié
Presence - catégorie de présence de l'espèce dans l'écoshape (P = Présente, X = Présence attendue, H = Historique, NULL = Supprimée*, voir le PDF des métadonnées pour les définitions)
TypeUtilisation - type d'utilisation de l'espèce dans l'écoshape (B = Reproduction, P = Reproduction possible, M = Migration, voir le PDF des métadonnées pour les définitions)
NotesCarteRepartitionEcoshape - nombre d'enregistrements saisis par source et commentaires des réviseurs, s'ils peuvent être publiés
DateMin - date la plus ancienne pour tous les enregistrements saisis qui chevauchent l'écoshape
DateMax - date la plus récente pour tous les enregistrements saisis qui chevauchent l'écoshape

[*Les écoshapes supprimées au cours du processus de révision par des experts sont incluses avec Présence=NULL et le champ RangeMapEcoshapeNotes contenant les commentaires des réviseurs, s'ils peuvent être publiés.]

Champs Juridiction :
objectid - identifiant unique ArcGIS
IDJuri - identifiant unique CAARBE
JuriAbbrev - code à deux lettres pour la juridiction
JuriNomE - nom Anglais de la juridiction
JuriNomF - nom Français de la juridiction

Champs Ecoshape/ApercuEcoshape :
FID - identifiant unique ArcGIS
EcoshapeID - identifiant unique CAARBE
IDEcoshape - clé étrangère CAARBE relative à l'enregistrement de la juridiction appropriée
NomEco - nom de l'écoshape
ParentEco - nom Anglais de l'écorégion parentale
ParentEcoF - nom Français de l'écorégion parentale
Ecozone - nom Anglais de l'écozone
EcozoneFR - nom Français de l'écozone
VerMosaiq - version de la mosaïque d'écoshape
SuperTerr - superficie terrestre en mètres carrés dérivée de la Commission de coopération écologique «Grands lacs et réservoirs d'Amérique du Nord»
SuperTot - superficie totale en mètres carrés

Avertissement :
- Veuillez consulter notre document sur les méthodes à l'adresse https://1drv.ms/b/s!Ajv6BHSXrqqqm4xipeEOQ67IfH77IQ?e=dqM1FO avant d'utiliser CAARBE.
- Les données CAARBE sont relativement grossières et conviennent à des fins de dépistage et d'éducation, mais ne sont pas destinées à tous les types d'applications et d'analyses.
- L'absence de données dans une zone géographique ne signifie pas nécessairement qu'une espèce n'y est pas présente.
- Un écoshape avec une valeur de présence ne signifie pas nécessairement qu'une espèce est présente dans toute la zone géographique.

Citation de plusieurs espèces : NatureServe Canada. 2026. Le project Cartographie automatisée des aires de répartissaient basée sur les écosystèmes (CAARBE). Ottawa, Canada. Consulté le [insérer la date] sur [insérer l'URL]
Citation d'une seule espèce : NatureServe Canada. 2023. Le project Cartographie automatisée des aires de répartissaient basée sur les écosystèmes (CAARBE) pour [insérer le nom de l'espèce, la version, le stade et la portée]. Ottawa, Canada. Consulté le [insérer la date] sur [insérer l'URL]
