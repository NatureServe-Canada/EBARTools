Fichiers compressés (ZIP) des aires de répartition des espèces sélectionnées extraites du projet de cartographie automatisée des aires de répartition basée sur les écosystèmes (CAARBÉ) pour une catégorie d'espèces/un groupe taxonomique sélectionné(e)
© NatureServe Canada 2026 sous CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/deed.fr)

Avertissement : Les versions anglaises des produits et documents CAARBÉ sont les versions officielles, car il n'existe pas toujours de traductions françaises officielles pour certains termes. Par exemple, il serait inapproprié de traduire certains noms et références de données d'entrée, car ceux-ci ont été fournis en anglais.

Ces fichiers compressés (ZIP) doivent contenir les fichiers suivants :
- CAARBExxxxx.pdf (cartes et métadonnées de la CAARBÉ des espèces sélectionnées)
- MethodsCAARBE.pdf (informations générales sur la production des cartes de répartition, les sources des unités écosystémiques et les sujets connexes)
- Ecoshape.* (fichiers comprenant des fichiers de forme (SHP) des tous les polygones précis des unités écosystémiques de la CAARBÉ)
- AppercuEcoshape.* (fichiers comprenant des fichiers de forme (SHP) des tous les polygones généralisés des unités écosystémiques de la CAARBÉ)
- CarteRepartition.csv (tableau des espèces et attributs de la CAARBÉ pour toutes les espèces au sein de la catégorie/groupe taxonomique)
- CarteRepartitionEcoshape.csv (tableau des attributs par unité écosystémique de la CAARBÉ pour toutes les espèces au sein de la catégorie/groupe taxonomique)
- Juridiction.csv (tableau des juridictions)
- CAARBExxxxx.aprx (fichier du projet ArcGIS Pro référençant les fichiers de données ci-dessus, avec les jointures appropriées pour chaque espèce au sein de la catégorie/groupe taxonomique)
- CAARBExxxxx.mapx (fichier de carte ArcGIS Pro référençant les fichiers de données ci-dessus, avec les jointures appropriées pour chaque espèce au sein de la catégorie/groupe taxonomique)
- CAARBExxxxxEcoshape.lyrx (fichier de couche ArcGIS Pro, avec la symbologie suggérée et les jointures appropriées, référençant les écoshapes d'origine pour chaque espèce au sein de la catégorie/groupe taxonomique)
- CAARBExxxxxAppercuEcoshape.lyrx (fichier de couche ArcGIS Pro, avec la symbologie suggérée et les jointures appropriées, référençant les écoshapes généraliséspour chaque espèce au sein de la catégorie/groupe taxonomique)
- CAARBExxxxxEcoshapesSupprime.lyrx (fichier de couche ArcGIS Pro, avec les jointures appropriées, affichant uniquement les écoshapes qui ont été supprimées à la suite de l'examen par les experts, référençant les écoshapes généralisées pour chaque espèce au sein de la catégorie/groupe taxonomique)
- CAARBExxxxxTypeUtilisation.lyrx (si applicable, fichier de couche ArcGIS Pro, avec la symbologie suggérée et les jointures appropriées, référençant le type d'utilisation des écoshapes généralisées pour chaque espèce au sein de la catégorie/groupe taxonomique)
[où xxxxx est l'ELEMENT_GLOBAL_ID de l'espèce sélectionnée]
[où yyyyy correspond au nom de la catégorie/du groupe taxonomique]
[les fichiers de projet ArcMap (.mxd) sont disponsible dans les fichiers ZIP anglais]

Les fichiers de données inclus sont liés comme suit :
CarteRepartition <-1---M-> CarteRepartitionEcoshape
Ecoshape/EcoshapeApercu <-1---M-> CarteRepartitionEcoshape
Juridiction <-1---M-> Ecoshape/EcoshapeApercu

Champs CarteRepartition :
objectid - identifiant unique ArcGIS
IDCarteRepartition - identifiant unique CAARBÉ
VersionRepartition - numéro de version CAARBÉ
EtapeRepartition - étape CAARBÉ dans la version (par exemple, généré automatiquement, examiné par des experts)
DateRepartition - date de génération
PorteeCarteRepartition - portée géographique (par exemple, N = Canadien, A = Nord-américain, G = mondial)
MetadonneesPortee - nombre d'enregistrements d'entrée par source, et nombre et détails (si publiables) des examens par des experts
NotesCarteRepartition - détails sur le(s) nom(s) de l'espèce
CommentairesCarteRepartition - notes supplémentaires
SynonymesUtilisee - liste des synonymes, le cas échéant, pour l'espèce principale sous laquelle les données d'entrée utilisées ont été importées
TypeUtilisationDifferencie - 1 si le type d'utilisation (reproduction, reproduction possible, migration) est différencié par écoshape
ID_ELEMENT_NATIONAL - identifiant unique national dans Biotics de NatureServe
ID_ELEMENT_MONDIAL - identifiant unique mondial dans Biotics de NatureServe
CODE_ELEMENT - identifiant de l'élément dans Biotics de NatureServe 
CATEGORIE - catégorie des espèces dans Biotics de NatureServe
GROUPE_TAX - groupe taxonomiquedes espèces dans Biotics de NatureServe
COM_FAMILLE - nom commun de la famille des espèces dans Biotics de NatureServe
GENRE - genre des espèces dans Biotics de NatureServe
EMBRANCHEMENT - embranchement des espèces dans Biotics de NatureServe
NIVEAU_NOMN_CA - nom canadien des espèces dans Biotics de NatureServe
NOM_SCIENTIFIQUE_NATIONAL - nom scientifique des espèces dans Biotics de NatureServe
NOM_ANGL_NATIONAL - nom anglais des espèces canadienne dans Biotics de NatureServe
NOM_FR_NATIONAL - nom français des espèces canadienne dans Biotics de NatureServe
NOM_COSEPAC - nom des espèces COSEPAC dans Biotics de NatureServe
ID_COSEPAC - identifiant des espèces COSEPAC dans Biotics de NatureServe
TYPE_ENDEMISME - type d'endémisme des espèces dans Biotics de NatureServe
RANGM - rang mondial des espèces dans Biotics de NatureServe
RANGN_CA - rang national canadien des espèces dans Biotics de NatureServe
RANGS_CA - rangs infranationaux canadiens des espèces dans Biotics de NatureServe
RANGN_EU - rang national américain des espèces dans Biotics de NatureServe
RANGS_EU - rangs infranationaux américains des espèces dans Biotics de NatureServe
RANGN_MX - rang national des espèces au mexique dans Biotics de NatureServe
RANGS_MX - rangs infranationaux des espèces au mexique dans Biotics de NatureServe
STATUT_LEP - statut en vertu de la Loi canadienne sur les espèces en péril dans Biotics de NatureServe
STATUT_COSEPAC - statut en vertu du Comité sur la situation des espèces en péril au Canada dans Biotics de NatureServe
STATUT_ESA - statut en vertu de la Loi Américaine sur les espèces menacées dans Biotics de NatureServe

Champs CarteRepartitionEcoshape :
objectid - identifiant unique ArcGIS
IDCarteRepartition - clé étrangère CAARBÉ relative à l'enregistrement CarteRepartition approprié
IDEcoshape - clé étrangère CAARBÉ relative à l'enregistrement Ecoshape/EcoshapeApercu approprié
Presence - catégorie de présence de l'espèce dans l'écoshape (P = Présente, X = Présence attendue, H = Historique, NULL = Supprimée*, voir le PDF des métadonnées pour les définitions)
TypeUtilisation - type d'utilisation de l'espèce dans l'écoshape (B = Reproduction, P = Reproduction possible, M = Migration, voir le PDF des métadonnées pour les définitions)
NotesCarteRepartitionEcoshape - nombre d'enregistrements saisis par source et commentaires des réviseurs, s'ils peuvent être publiés
DateMin - date la plus ancienne pour tous les enregistrements saisis qui chevauchent l'écoshape
DateMax - date la plus récente pour tous les enregistrements saisis qui chevauchent l'écoshape

[*Les écoshapes supprimées au cours du processus de révision par des experts sont incluses avec Présence=NULL et le champ RangeMapEcoshapeNotes contenant les commentaires des réviseurs, s'ils peuvent être publiés.]

Champs Juridiction :
objectid - identifiant unique ArcGIS
IDJuri - identifiant unique CAARBÉ
JuriAbbrev - code à deux lettres pour la juridiction
JuriNomE - nom anglais de la juridiction
JuriNomF - nom français de la juridiction

Champs Ecoshape/EcoshapeApercu :
FID - identifiant unique ArcGIS
EcoshapeID - identifiant unique CAARBÉ
IDEcoshape - clé étrangère CAARBÉ relative à l'enregistrement de la Juridiction appropriée
NomEco - nom de l'écoshape
ParentEco - nom anglais de l'écorégion parentale
ParentEcoF - nom français de l'écorégion parentale
Ecozone - nom anglais de l'écozone
EcozoneFR - nom français de l'écozone
VerMosaiq - version de la mosaïque d'écoshape
SuperTerr - superficie terrestre en mètres carrés dérivée de la Commission de coopération écologique «Grands lacs et réservoirs d'Amérique du Nord»
SuperTot - superficie totale en mètres carrés

Avertissement :
- Veuillez consulter notre document sur les méthodes à l'adresse https://1drv.ms/b/s!Ajv6BHSXrqqqm4xipeEOQ67IfH77IQ?e=dqM1FO avant d'utiliser CAARBÉ.
- Les données CAARBÉ sont relativement grossières et conviennent à des fins de dépistage et d'éducation, mais ne sont pas destinées à tous les types d'applications et d'analyses.
- L'absence de données dans une zone géographique ne signifie pas nécessairement qu'une espèce n'y est pas présente.
- Un écoshape avec une valeur de présence ne signifie pas nécessairement qu'une espèce est présente dans toute la zone géographique.

Citation de plusieurs espèces : NatureServe Canada, 2026. Cartographie automatisée des aires de répartition basée sur les écosystèmes (CAARBÉ). Ottawa, Canada. Consulté le [insérer la date] sur [insérer l'URL]
Citation d'une seule espèce : NatureServe Canada, 2026. Cartographie automatisée des aires de répartition basée sur les écosystèmes (CAARBÉ) pour [insérer le nom de l'espèce, la version, la portée]. Ottawa, Canada. Extrait de [insérer l'URL] le [insérer la date]
