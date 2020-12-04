Export of Species data from EBAR-KBA database

This ZIP package contains a single file geodatabase with the following feature classes:
- EBARPoints
- EBARLines
- EBARPolygons

Each feature class has the following fields:
ObjectID - ArcGIS unique identifier
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
Shape - geometry
ELEMENT_NATIONAL_ID - Canadian unique identier for the element
ELEMENT_GLOBAL_ID - international unique identier for the element
ELEMENT_CODE - unique identifier compatible with the Biological and Conservation Data system
NATIONAL_SCIENTIFIC_NAME - Canadian scientific name for the species
NATIONAL_ENGL_NAME - Canadian English name for the species
NATIONAL_FR_NAME - Canadian French name for the species
SynonymName - synonym name, if the data was originally provided using this synonym
DateReceived - date the the dataset was obtainted from the provider
Restrictions - indicates whether any restrictions apply to the record
DatasetName - label used by EBAR team to identify the dataset
DatasetSourceName - the name of the dataset source
DatasetSourceCitation - the citation of the dataset source, to be used for crediting the data provider
DatasetType - one of Critical Habitat, Element Occurrences, Habitat Suitability, Range Estimate, Source Features, Species Observations
