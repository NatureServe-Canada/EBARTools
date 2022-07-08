# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: TabularFieldMapping.py
# Field mapping dictionaries for point data sources


gbif_fields = {'quality_grade': None,
               'unique_id': 'gbifID',
               'uri': 'occurrenceID',
               'license': 'license',
               'scientific_name': 'species',
               'longitude': 'decimalLongitude',
               'latitude': 'decimalLatitude',
               'srs': 'geodeticDatum',
               'coordinates_obscured': None,
               'private_longitude': None,
               'private_latitude': None,
               'accuracy': 'coordinateUncertaintyInMeters',
               'private_accuracy': None,
               'year': 'year',
               'month': 'month',
               'day': 'day',
               'date': None,
               'basis_of_record': 'basisOfRecord',
               'individual_count': 'individualCount',
               'geoprivacy': None,
               'taxon_geoprivacy': None,
               'breeding_code': None}

ncc_gbif_fields = {'quality_grade': None,
                   'unique_id': 'gbifID',
                   'uri': 'occurrence',
                   'license': 'license',
                   'scientific_name': 'species',
                   'longitude': 'decimalLon',
                   'latitude': 'decimalLat',
                   'srs': None,
                   'coordinates_obscured': None,
                   'private_longitude': None,
                   'private_latitude': None,
                   'accuracy': 'coordinate',
                   'private_accuracy': None,
                   'year': 'year_',
                   'month': 'month_',
                   'day': 'day_',
                   'date': 'eventDate',
                   'basis_of_record': 'basisOfRec',
                   'individual_count': None,
                   'geoprivacy': None,
                   'taxon_geoprivacy': None,
                   'breeding_code': None}

vertnet_fields = {'quality_grade': None,
                  'unique_id': 'occurrenceid',
                  'uri': 'occurrenceid',
                  'license': 'license',
                  'scientific_name': 'name',
                  'longitude': 'longitude',
                  'latitude': 'latitude',
                  'srs': 'geodeticdatum',
                  'coordinates_obscured': None,
                  'private_longitude': None,
                  'private_latitude': None,
                  'accuracy': 'coordinateuncertaintyinmeters',
                  'private_accuracy': None,
                  'year': 'year',
                  'month': 'month',
                  'day': 'day',
                  'date': 'eventdate',
                  'basis_of_record': 'basisofrecord',
                  'individual_count': 'individualcount',
                  'geoprivacy': None,
                  'taxon_geoprivacy': None,
                  'breeding_code': None}

#ecoengine_fields = {'quality_grade': None,
#                    'unique_id': 'key',
#                    'uri': 'url',
#                    'license': None,
#                    'scientific_name': 'name',
#                    'longitude': 'longitude',
#                    'latitude': 'latitude',
#                    'srs': None,
#                    'coordinates_obscured': None,
#                    'private_longitude': None,
#                    'private_latitude': None,
#                    'accuracy': 'coordinate_uncertainty_in_meters',
#                    'private_accuracy': None,
#                    'year': None,
#                    'month': None,
#                    'day': None,
#                    'date': 'begin_date',
#                    'basis_of_record': 'observation_type',
#                    'individual_count': None,
#                    'geoprivacy': None,
#                    'taxon_geoprivacy': None,
#                    'breeding_code': None}

inaturalistorg_fields = {'quality_grade': 'quality_grade',
                         'unique_id': 'id',
                         'uri': 'uri',
                         'license': 'license_code',
                         'scientific_name': 'name',
                         'longitude': 'longitude',
                         'latitude': 'latitude',
                         'srs': None,
                         'coordinates_obscured': 'obscured',
                         'private_longitude': None,
                         'private_latitude': None,
                         'accuracy': 'public_positional_accuracy',
                         'private_accuracy': 'positional_accuracy',
                         'year': None,
                         'month': None,
                         'day': None,
                         'date': 'observed_on',
                         'basis_of_record': None,
                         'individual_count': None,
                         'geoprivacy': 'geoprivacy',
                         'taxon_geoprivacy': 'taxon_geoprivacy',
                         'breeding_code': None}

inaturalistca_fields = {'quality_grade': 'quality_grade',
                        'unique_id': 'id',
                        'uri': 'url',
                        'license': 'license',
                        'scientific_name': 'scientific_name',
                        'longitude': 'longitude',
                        'latitude': 'latitude',
                        'srs': None,
                        'coordinates_obscured': 'coordinates_obscured',
                        'private_longitude': 'private_longitude',
                        'private_latitude': 'private_latitude',
                        'accuracy': 'public_positional_accuracy',
                        'private_accuracy': 'positional_accuracy',
                        'year': None,
                        'month': None,
                        'day': None,
                        'date': 'observed_on_text',
                        'basis_of_record': None,
                        'individual_count': None,
                        'geoprivacy': 'geoprivacy',
                        'taxon_geoprivacy': 'taxon_geoprivacy',
                        'breeding_code': None}

bison_fields = {'quality_grade': None,
                'unique_id': 'occurrenceID',
                'uri': None,
                'license': 'license',
                'scientific_name': 'name',
                'longitude': 'longitude',
                'latitude': 'latitude',
                'srs': None,
                'coordinates_obscured': None,
                'private_longitude': None,
                'private_latitude': None,
                'accuracy': None,
                'private_accuracy': None,
                'year': 'year',
                'month': None,
                'day': None,
                'date': 'date',
                'basis_of_record': 'basisOfRecord',
                'individual_count': None,
                'geoprivacy': None,
                'taxon_geoprivacy': None,
                'breeding_code': None}

canadensys_fields = {'quality_grade': None,
                     'unique_id': 'occurrenceID',
                     'uri': None,
                     'license': 'dcterms:license',
                     'scientific_name': 'species',
                     'longitude': 'decimalLongitude',
                     'latitude': 'decimalLatitude',
                     'srs': 'verbatimCoordinateSystem',
                     'coordinates_obscured': None,
                     'private_longitude': None,
                     'private_latitude': None,
                     'accuracy': 'coordinateUncertaintyInMeters',
                     'private_accuracy': None,
                     'year': 'year',
                     'month': 'month',
                     'day': None,
                     'date': 'eventDate',
                     'basis_of_record': 'basisOfRecord',
                     'individual_count': 'individualCount',
                     'geoprivacy': None,
                     'taxon_geoprivacy': None,
                     'breeding_code': None}

ncc_endemics_fields = {'quality_grade': None,
                       'unique_id': 'OBJECTID',
                       'uri': None,
                       'license': None,
                       'scientific_name': 'SCIENTIFIC',
                       'longitude': 'longitude',
                       'latitude': 'latitude',
                       'srs': None,
                       'coordinates_obscured': None,
                       'private_longitude': None,
                       'private_latitude': None,
                       'accuracy': None,
                       'private_accuracy': None,
                       'year': 'OBSERVAT_3',
                       'month': None,
                       'day': None,
                       'date': 'OBSERVAT_2',
                       'basis_of_record': None,
                       'individual_count': None,
                       'geoprivacy': None,
                       'taxon_geoprivacy': None,
                       'breeding_code': None}

idigbio_fields = {'quality_grade': None,
                  'unique_id': 'etag',
                  'uri': None,
                  'license': None,
                  'scientific_name': 'name',
                  'longitude': 'longitude',
                  'latitude': 'latitude',
                  'srs': None,
                  'coordinates_obscured': None,
                  'private_longitude': None,
                  'private_latitude': None,
                  'accuracy': None,
                  'private_accuracy': None,
                  'year': None,
                  'month': None,
                  'day': None,
                  'date': 'datecollected',
                  'basis_of_record': 'basisofrecord',
                  'individual_count': 'individualcount',
                  'geoprivacy': None,
                  'taxon_geoprivacy': None,
                  'breeding_code': None}

bbna_fields = {'quality_grade': None,
               'unique_id': 'BBNA.code',
               'uri': None,
               'license': None,
               'scientific_name': 'sciname',
               'longitude': 'longitude',
               'latitude': 'latitude',
               'srs': None,
               'coordinates_obscured': None,
               'private_longitude': None,
               'private_latitude': None,
               'accuracy': None,
               'private_accuracy': None,
               'year': None,
               'month': None,
               'day': None,
               'date': 'date',
               'basis_of_record': None,
               'individual_count': None,
               'geoprivacy': None,
               'taxon_geoprivacy': None,
               'breeding_code': None}

ebird_fields = {'quality_grade': 'approved',
                'unique_id': 'global_unique_identifier',
                'uri': None,
                'license': None,
                'scientific_name': 'scientific_name',
                'longitude': 'longitude',
                'latitude': 'latitude',
                'srs': None,
                'coordinates_obscured': None,
                'private_longitude': None,
                'private_latitude': None,
                'accuracy': 'ebar_buffer',
                'private_accuracy': None,
                'year': None,
                'month': None,
                'day': None,
                'date': 'observation_date',
                'basis_of_record': None,
                'individual_count': 'observation_count',
                'geoprivacy': None,
                'taxon_geoprivacy': None,
                'breeding_code': 'breeding_code'}

bba_fields = {'quality_grade': None,
              'unique_id': 'GlobalUniqueIdentifier',
              'uri': None,
              'license': None,
              'scientific_name': 'ScientificName',
              'longitude': 'DecimalLongitude',
              'latitude': 'DecimalLatitude',
              'srs': 'GeodeticDatum',
              'coordinates_obscured': None,
              'private_longitude': None,
              'private_latitude': None,
              'accuracy': 'EBARBuffer',
              'private_accuracy': None,
              'year': None,
              'month': None,
              'day': None,
              'date': 'YearCollected',
              'basis_of_record': None,
              'individual_count': None,
              'geoprivacy': None,
              'taxon_geoprivacy': None,
              'breeding_code': 'BreedingBirdAtlasCode'}

other_fields = {'quality_grade': None,
                'unique_id': 'originalID',
                'uri': None,
                'license': None,
                'scientific_name': 'speciesName',
                'longitude': 'longitude',
                'latitude': 'latitude',
                'srs': 'datum',
                'coordinates_obscured': None,
                'private_longitude': None,
                'private_latitude': None,
                'accuracy': 'uncertaintyDistance',
                'private_accuracy': None,
                'year': 'Year',
                'month': 'Month',
                'day': 'Day',
                'date': 'observationDate',
                'basis_of_record': None,
                'individual_count': 'individualsCount',
                'geoprivacy': None,
                'taxon_geoprivacy': None,
                'breeding_code': None}

tabular_field_mapping_dict = {'GBIF': gbif_fields,
                              'NCC_GBIF': ncc_gbif_fields,
                              'VertNet': vertnet_fields,
                              #'Ecoengine': ecoengine_fields,
                              'iNaturalist.org': inaturalistorg_fields,
                              'iNaturalist.ca': inaturalistca_fields,
                              'BISON': bison_fields,
                              'Canadensys': canadensys_fields,
                              'NCCEndemics': ncc_endemics_fields,
                              'iDigBio': idigbio_fields,
                              'Bumble Bees of North America': bbna_fields,
                              'eBird': ebird_fields,
                              'BC Breeding Bird Atlas': bba_fields,
                              'AB Breeding Bird Atlas': bba_fields,
                              'SK Breeding Bird Atlas': bba_fields,
                              'MB Breeding Bird Atlas': bba_fields,
                              'ON Breeding Bird Atlas': bba_fields,
                              'QC Breeding Bird Atlas': bba_fields,
                              'Maritimes Breeding Bird Atlas': bba_fields,
                              'NF Breeding Bird Atlas': bba_fields,
                              'Other': other_fields}
