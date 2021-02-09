Export of Species data from EBAR-KBA database

This ZIP package contains a single file geodatabase with the following feature classes:
- EBARPoints
- EBARLines
- EBARPolygons

The following rules were used when extracting data for export:
- Include records that overlap the jurisdiction or fall within 32km of its boundary or coastline (32km is the approximate maximum locational obscuring applied to iNaturalist obscured records)
- Exclude records marked as EBAR Restricted or that come from a United States Natural Heritage Program (i.e., acquired through a licensing agreement that restricts sharing)
- Exclude records marked as Bad Data (this is done by the EBAR team either manually based on expert input, or automatically using a tool that compares an expert-review range map to the underlying species data)
- Exclude records that were provided by a Conservation Data Centre
- Exclude polygon datasets not associated with confirmed species presence, such as Critical Habitat, Range Estimate, Habitat Suitability, and Area of Occupancy

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
ELEMENT_NATIONAL_ID - Canadian unique identier for the element
ELEMENT_GLOBAL_ID - international unique identier for the element
ELEMENT_CODE - unique identifier compatible with the Biological and Conservation Data system
NATIONAL_SCIENTIFIC_NAME - Canadian scientific name for the species
NATIONAL_ENGL_NAME - Canadian English name for the species
NATIONAL_FR_NAME - Canadian French name for the species
SynonymName - synonym name, if the data was originally provided using this synonym
DateReceived - date the the dataset was obtained from the provider
Restrictions - N=Non-restricted; R=Restrictions apply to the record
DatasetName - label used by EBAR team to identify the dataset
DatasetSourceName - the name of the dataset source
DatasetSourceCitation - the citation of the dataset source, to be used for crediting the data provider
DatasetType - one of Critical Habitat, Element Occurrences, Habitat Suitability, Range Estimate, Source Features, Species Observations, Other, Other Observations, Other Range, Area of Occupancy

For additional information please contact EBAR-KBA@natureserve.ca
