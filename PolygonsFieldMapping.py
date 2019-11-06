# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: PolygonsFieldMapping.py
# Field mapping dictionaries for polygon data sources


cdc_eos_fields = {'unique_id': 'EO_ID',
                  'uri': None,
                  'scientific_name': 'SName',
                  'date': 'LAST_OBS_D',
                  'eo_rank': 'BASIC_EO_R'}

cdc_sf_fields = {'unique_id': 'SOURCE_FEA',
                 'uri': None,
                 'scientific_name': 'SNAME',
                 'date': None,
                 'eo_rank': None}

eccc_critical_habitat_fields = {'unique_id': 'Identifier',
                                'uri': None,
                                'scientific_name': 'SciName',
                                'date': None,
                                'eo_rank': None}

ncc_endemics_polygons_fields = {'unique_id': 'OBJECTID',
                                'uri': 'Link',
                                'scientific_name': 'MATCH_NSC',
                                'date': None,
                                'eo_rank': None}
