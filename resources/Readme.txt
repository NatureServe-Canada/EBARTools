Ecosystem-based Automated Range (EBAR) ZIP package for selected species
� NatureServe Canada 2020 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

This ZIP package should contain the following files:
- EBARxxxxx.pdf (map and metadata for EBAR for selected species)
- EBARMethods.pdf (background information on range map production, ecoshape sources and related topics)
- Ecoshape.* (files comprising polygons shapefile of original ecoshapes for EBAR for selected species)
- EcoshapeOverview.* (files comprising polygons shapefile of generalized ecoshapes for EBAR for selected species)
- RangeMap.csv (table of species and range attributes for EBAR for selected species)
- RangeMapEcoshape.csv (table of per-ecoshape attributes for EBAR for selected species)
- Jurisdiction.csv (table of jurisdictions)
- EXARxxxxx.aprx (ArcGIS Pro project file referencing the data files above, with appropriate joins)
- EXARxxxxx.mapx (ArcGIS Pro map file referencing the data files above, with appropriate joins)
- EBARxxxxxEcoshape.lyrx (ArcGIS Pro layer file, with suggested symbology and appropriate joins, referencing the original ecoshapes)
- EBARxxxxxEcoshapeOverview.lyrx (ArcGIS Pro layer file, with suggested symbology and appropriate joins, referencing the generalized ecoshapes)
- EBARxxxxx.mxd (ArcMap project file referencing the data files above)
- EBARxxxxxEcoshape.lyr (ArcMap layer file, with suggested symbology and appropriate joins, referencing the original ecoshapes)
- EBARxxxxxEcoshapeOverview.lyr (ArcMap layer file, with suggested symbology and appropriate joins, referencing the generalized ecoshapes)
[where xxxxx is the ELEMENT_GLOBAL_ID of the selected species]

The included data files are related as follows:
RangeMap <-1---M-> RangeMapEcoshape
Ecoshape/EcoshapeOverview <-1---M-> RangeMapEcoshape
Jurisdiction <-1---M-> Ecoshape/EcoshapeOverview

RangeMap fields:
objectid - ArcGIS unique identifier
RangeMapID - EBAR unique identifier
RangeVersion - EBAR version number
RangeStage - EBAR stage within the version (e.g. Auto-generated, Expert reviewed)
RangeDate - date generated
RangeMapScope - geographic scope (e.g. N=Canadian, A=North American, G=Global)
RangeMetadata - numbers of input records by source, and count and details (if publishable) of expert reviews
RangeMapNotes - details on the species name(s)
RangeMapComments - additional notes
SynonymsUsed - a list of the synonyms, if any, for the primary species under which the input data used was imported
ELEMENT_NATIONAL_ID - NatureServe Biotics national unique identifier
ELEMENT_GLOBAL_ID - NatureServe Biotics global unique identifier
ELEMENT_CODE - NatureServe Biotics element identifier
CATEGORY - NatureServe Biotics species category
TAX_GROUP - NatureServe Biotics species taxa group
FAMILY_COM - NatureServe Biotics species family common name
GENUS - NatureServe Biotics species genus
PHYLUM - NatureServe Biotics phylum
CA_NNAME_LEVEL - NatureServe Biotics species Canadian name level
NATIONAL_SCIENTIFIC_NAME - NatureServe Biotics Canadian species scientific name
NATIONAL_ENGL_NAME - NatureServe Biotics Canadian species English name
NATIONAL_FR_NAME - NatureServe Biotics Canadian species French name
COSEWIC_NAME - NatureServe Biotics COSEWIC species name
ENDEMISM_TYPE - NatureServe Biotics species endemism type
GRANK - NatureServe Biotics species global rank
NRANK_CA - NatureServe Biotics species Canadian national rank
SRANKS_CA - NatureServe Biotics species Canadian subnational ranks
NRANK_US - NatureServe Biotics species United States national rank
SRANKS_US - NatureServe Biotics species United States subnational ranks
NRANK_MX - NatureServe Biotics species Mexico national rank
SRANKS_MX - NatureServe Biotics species Mexico subnational ranks
SARA_STATUS - NatureServe Biotics species Canadian Species at Risk Act status
COSEWIC_STATUS - NatureServe Biotics species Committee on the Status of Endangered Wildlife in Canada status
ESA_STATUS - NatureServe Biotics species US Endangered Species Act status

RangeMapEcoshape fields:
objectid - ArcGIS unique identifier
RangeMapID - EBAR foreign key relating to the appropriate RangeMap record
EcoshapeID - EBAR foreign key relating to the appropriate Ecoshape/EcoshapeOverview record
Presence - the category of species presence in the Ecoshape (P=Present, X=Presence Expected, H=Historical, see metadata PDF for definitions)
RangeMapEcoshapeNotes - numbers of input records by source

Jurisdiction fields:
objectid - ArcGIS unique identifier
JurisID - EBAR unique identifier
JurisAbbrev - two-letter code for the jurisdiction
JurisName - full name for the jurisdiction

Ecoshape/EcoshapeOverview fields:
FID - ArcGIS unique identifier
EcoshapeID - EBAR unique identifier
JurisID - EBAR foreign key relating to the appropriate Jurisdiction record
EcoName - name of the ecoshape
ParentEco - English name of the parent ecoregion
ParentEcoF - French name of the parent ecoregion
Ecozone - English name of the ecozone 
EcozoneFR - French name of the ecozone
MosaicVer - version of the ecoshape mosaic
TerrArea - terrestrial area in square metres derived from Commission for Ecological Cooperation "Major Lakes and Reservoirs of North America"
TotalArea - total area in square metres

Disclaimer:
- Please review our methods document at https://1drv.ms/b/s!Ajv6BHSXrqqqm4xipeEOQ67IfH77IQ?e=dqM1FO before using EBAR.
- EBAR range data are relatively coarse scale and appropriate for screening and education purposes, but are not intended for all types of applications and analysis.
- The absence of data in any geographic areas does not necessarily mean that a species is not present.
- An ecoshape with a presence value does not necessarily mean that a species is present throughout the entire geographic area.

Multiple species citation: NatureServe Canada. 2020. Ecosystem-based Automated Range (EBAR). Ottawa, Canada. Retrieved on [insert date] from [insert url]
Single species citation: NatureServe Canada. 2020. [insert species name] Ecosystem-based Automated Range (EBAR). Ottawa, Canada. Retrieved on [insert date] from [insert url]
