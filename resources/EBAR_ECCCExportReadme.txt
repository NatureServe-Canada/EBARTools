Export of Species data from EBAR-KBA database for ECCC-LERS project team

Please refer to the species list (ECCC_dataRequest_speciesList.xlsx) for the full species list.

This ZIP package contains a single file geodatabase with the following feature classes:
- EBARPoints
- EBARLines
- EBARPolygons

The following rules were used when extracting data for export:
- Include records that overlap the jurisdictional boundaries of the provinces and territories of Canada or fall within 32km of its boundary or coastline (32km is the approximate maximum locational obscuring applied to iNaturalist obscured records)
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
RepresentationAccuracy - Level of accuracy associated with an Element Occurrence as per http://help.natureserve.org/biotics/#Record_Management/Element_Occurrence/EO_Representation_Accuracy_Value.htm
SpeciesID - EBAR unique identifier for the species/element
ELEMENT_NATIONAL_ID - Canadian unique identifier for the element
ELEMENT_GLOBAL_ID - international unique identifier for the element
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
dataqcstatus - Value selected from a drop-down menu that indicates the Quality Control (QC) status of the tabular data associated with the Source Feature.
datasensitivity - Value selected from a drop-down menu that indicates whether or not locational information of the Element Occurrence (EO) or Source Feature (SF) is sensitive and should be restricted from unsecured use.
datasensitivitycat - Explanation of why locational information of the Element Occurrence (EO) or Source Feature (SF) is sensitive and restricted.
descriptor - Any label describing a Source Feature that would be useful to the agency in differentiating between different observations (e.g., east patch, west patch). This may be helpful in identifying the different Source Features that comprise a complex (multi-source) Element Occurrence Representation (EO Rep).
digitizingcomments - Comments related to the digitizing of the Source Feature.
independentsf - Checkbox that indicates the Source Feature is not currently a component of an Element Occurrence Representation [EO Rep]); rather, it is Independent.
locuncertaintydistcls - Value selected from a drop-down menu that indicates the estimated distance, selected from a defined set of ranges (i.e., classes), to be applied as a buffer representing the locational uncertainty associated with data having a real estimated uncertainty.
locuncertaintydistunit - Value selected from a drop-down menu that indicates the unit associated with the entry in the Locational Uncertainty Distance field for Source Features with Estimated uncertainty.
locuncertaintytype - Value selected from a drop-down menu that indicates the type of inaccuracy in the mapped location of an observation (i.e., Source Feature) compared with its actual on-the-ground location. This is determined on the basis of the underlying observation data (specifically its size as compared with the minimum mapping unit (mmu), indicated as the Conceptual Feature Type), and the amount and direction of the variability between the recorded and actual locations.
locuseclass - Location use classes pertain only to Elements that occupy geographically disjunct locations at different seasons. Classes are not applicable to nonmigratory Elements, and are generally not applicable to terrestrial or freshwater migratory Elements that move between contiguous areas.
mappingcomments - Comments related to how a Source Feature has been mapped.
mapqcstatus - Value selected from a drop-down menu that indicates the Quality Control (QC) status of the mapped Source Feature.
qccomments - Comments related to the Quality Control (QC) Status of this Source Feature record.
RepresentationAccuracy - Value selected from a drop-down menu that indicates the level of accuracy associated with the Source Feature (SF). Accuracy varies on the basis of the area observed to be occupied by the Element (Field Observation) relative to the area contained within the footprint of the Source Feature. Differences in these two size values indicate that additional area was included within the feature boundary for locational uncertainty. Representation Accuracy (RA) provides a common index for the consistent comparison of these features, thus helping to ensure that aggregated data are correctly analyzed and interpreted.
unsuitablehabexcluded - Checkbox that indicates that the Source Feature has been digitized without including any known unsuitable habitat.



*Individual records can be manually flagged as "Bad Data" by the EBAR team. Flagging is also done automatically using an algorithm that detects duplicates by Species, ObservationDate, and Location. Bad data is not included when generating range maps, but the EBAR team has chosen to retain, rather than delete, bad data to avoid re-importing it in future.

For additional information please contact EBAR-KBA@natureserve.ca
