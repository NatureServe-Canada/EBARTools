Export of Species data from EBAR-KBA database for HBJBL project team

Please refer to the species list (ECCC_dataRequest_speciesList.xlsx) for the full species list.

This ZIP package contains a single file geodatabase with the following:
- EBARPoints feature class
- EBARLines feature class
- EBARPolygons feature class
- BIOTICS_ELEMENT_NATIONAL (species) table
- Synonym table

The following rules were used when extracting data for export:
- Include records that overlap the HBJBL study area or fall within 10km of its boundary or coastline
- Only include records where the dataset provider explicitly permits NSC Biodiversity Science, or we have confirmed sharing permissions with the CDCs via the Data Sharing Agreement and data users have completed all required data security requirements
- Exclude polygon datasets not associated with confirmed species presence, such as Critical Habitat, Range Estimate, Habitat Suitability, and Area of Occupancy
- Exclude records flagged as Bad Data* 

Each feature class has the following fields:
ObjectID - ArcGIS unique identifier
Shape - geometry
InputPointID/InputLineID/InputPolygonID - EBAR unique identifier
MinDate - data begin date, if any
MaxDate - data end data
Accuracy - spatial uncertainty in metres
IndividualCount - the number of species individuals reported in the observation
DatasetSourceUniqueID - provider's unique identifier
URI - uniform resource identifier (e.g. URL, URN) for the observation/occurrence
License - provider's licensing terms for the record
CoordinatesObscured - 1 indicates exact location has been obscured by the data provided (currently only applies iNaturalist data)
RepresentationAccuracy - Level of accuracy associated with an Element Occurrence as per http://help.natureserve.org/biotics/#Record_Management/Element_Occurrence/EO_Representation_Accuracy_Value.htm. Accuracy varies on the basis of the area observed to be occupied by the Element (Field Observation) relative to the area contained within the footprint of the Source Feature. Differences in these two size values indicate that additional area was included within the feature boundary for locational uncertainty. Representation Accuracy (RA) provides a common index for the consistent comparison of these features, thus helping to ensure that aggregated data are correctly analyzed and interpreted.
SpeciesID - EBAR unique identifier for the species/element
ELEMENT_NATIONAL_ID - NatureServe Canadian unique identifier for the species
ELEMENT_GLOBAL_ID - NatureServe international unique identifier for the species
ELEMENT_CODE - unique identifier compatible with the Biological and Conservation Data system
NATIONAL_SCIENTIFIC_NAME - Canadian scientific name for the species
NATIONAL_ENGL_NAME - Canadian English name for the species
NATIONAL_FR_NAME - Canadian French name for the species
SynonymName - synonym name, if the data was originally provided using this synonym
DateReceived - date the the dataset was obtained from the provider
SensitiveEcologicalDataCat - the reason, if any, for sensitivity of or restrictions on the record
DatasetName - label used by EBAR team to identify the dataset
DatasetSourceName - the name of the dataset source
DatasetSourceCitation - the citation of the dataset source, to be used for crediting the data provider
DatasetType - one of Critical Habitat, Element Occurrences, Habitat Suitability, Range Estimate, Source Features, Species Observations, Other, Other Observations, Other Range, Area of Occupancy
DataQCStatus - Value selected from a drop-down menu that indicates the Quality Control (QC) status of the tabular data associated with the Source Feature.
DataSensitivity - Value selected from a drop-down menu that indicates whether or not locational information of the Element Occurrence (EO) or Source Feature (SF) is sensitive and should be restricted from unsecured use.
DataSensitivityCat - Explanation of why locational information of the Element Occurrence (EO) or Source Feature (SF) is sensitive and restricted.
Descriptor - Any label describing a Source Feature that would be useful to the agency in differentiating between different observations (e.g., east patch, west patch). This may be helpful in identifying the different Source Features that comprise a complex (multi-source) Element Occurrence Representation (EO Rep).
DigitizingComments - Comments related to the digitizing of the Source Feature.
IndependentSF - Checkbox that indicates the Source Feature is not currently a component of an Element Occurrence Representation [EO Rep]); rather, it is Independent.
LocUncertaintyDistCls - Value selected from a drop-down menu that indicates the estimated distance, selected from a defined set of ranges (i.e., classes), to be applied as a buffer representing the locational uncertainty associated with data having a real estimated uncertainty.
LocUncertaintyDistUnit - Value selected from a drop-down menu that indicates the unit associated with the entry in the Locational Uncertainty Distance field for Source Features with Estimated uncertainty.
LocUncertaintyType - Value selected from a drop-down menu that indicates the type of inaccuracy in the mapped location of an observation (i.e., Source Feature) compared with its actual on-the-ground location. This is determined on the basis of the underlying observation data (specifically its size as compared with the minimum mapping unit (mmu), indicated as the Conceptual Feature Type), and the amount and direction of the variability between the recorded and actual locations.
LocUseClass - Location use classes pertain only to Elements that occupy geographically disjunct locations at different seasons. Classes are not applicable to nonmigratory Elements, and are generally not applicable to terrestrial or freshwater migratory Elements that move between contiguous areas.
MappingComments - Comments related to how a Source Feature has been mapped.
MapQCStatus - Value selected from a drop-down menu that indicates the Quality Control (QC) status of the mapped Source Feature.
QCComments - Comments related to the Quality Control (QC) Status of this Source Feature record.
UnsuitableHabExcluded - Checkbox that indicates that the Source Feature has been digitized without including any known unsuitable habitat.

The BIOTICS_ELEMENT_NATIONAL table has the following fields:
SpeciesID - EBAR unique identifier for the species/element
ELEMENT_NATIONAL_ID - NatureServe Canadian unique identifier for the species
ELEMENT_GLOBAL_ID - NatureServe international unique identifier for the species
ELEMENT_CODE - unique identifier compatible with the Biological and Conservation Data system
NATIONAL_SCIENTIFIC_NAME - Canadian scientific name for the species
NATIONAL_ENGL_NAME - Canadian English name for the species
NATIONAL_FR_NAME - Canadian French name for the species
GLOBAL_SCIENTIFIC_NAME - international scientific name for the species
GLOBAL_SYNONYMS - international synonyms for the species
GLOBAL_ENGL_NAME - international English name for the species
GLOB_FR_NAME - international French name for the species
COSEWIC_NAME - Committee on the Status of Endangered Wildlife in Canada scientific name for the species
ENGLISH_COSEWIC_COM_NAME - Committee on the Status of Endangered Wildlife in Canada English name for the species
FRENCH_COSEWIC_COM_NAME - Committee on the Status of Endangered Wildlife in Canada French name for the species
COSEWIC_ID - Committee on the Status of Endangered Wildlife in Canada unique identifier for the species
CA_NNAME_LEVEL - level of the National Scientific Name in the taxonomic or classification hierarchy indicated by the Classification Framework (https://help.natureserve.org/biotics/Content/Record_Management/Scientific_Name/SN_Classification_Framework.htm)
CATEGORY - taxonomic category of the species
TAX_GROUP - taxonomic group of the species
FAMILY_COM - commom name of the taxonomic family of the species
GENUS - genus of the species
PHYLUM - phylum of the species
CLASSIFICATION_STATUS - status of the species (https://help.natureserve.org/biotics/biotics_help.htm#Record_Management/Element_Files/Element_Tracking/ETRACK_Classification_Status.htm)
SHORT_CITATION_AUTHOR - author(s) of the reference
SHORT_CITATION_YEAR - year the reference was published
FORMATTED_FULL_CITATION - formal citation for the reference
AUTHOR_NAME - author of the scientific name for the species
NSX_URL - NatureServe Explorer link for the species

The Synonym table has the following fields:
SynonymID - EBAR unique identifier for the Synonym
SpeciesID - EBAR unique identifier for the Species that the Synonym relates to
SynonymName - nane of the synonym
SHORT_CITATION_AUTHOR - author(s) of the reference
SHORT_CITATION_YEAR - year the reference was published
FORMATTED_FULL_CITATION - formal citation for the reference
AUTHOR_NAME - author of the scientific name for the species

*Individual records can be manually flagged as "Bad Data" by the EBAR team. Flagging is also done automatically using an algorithm that detects duplicates by Species, ObservationDate, and Location. Bad data is not included when generating range maps, but the EBAR team has chosen to retain, rather than delete, bad data to avoid re-importing it in future.

For additional information please contact EBAR-KBA@natureserve.ca
