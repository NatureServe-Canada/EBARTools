# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Christine Terwissen
# © NatureServe Canada 2019 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: SpatialFieldMapping.py
# Field mapping dictionaries for spatial data sources


cdc_eo_fields = {'unique_id': 'EO_ID',
                 'uri': None,
                 'scientific_name': 'SName',
                 'min_date': None,
                 'max_date': 'LAST_OBS_D',
                 'eo_rank': 'BASIC_EO_R'}

bc_eo_fields = {'unique_id': 'OCCR_ID',
                'uri': None,
                'scientific_name': 'SCI_NAME',
                'min_date': 'FIRST_OBS',
                'max_date': 'LAST_OBS',
                'eo_rank': 'RANK'}

cdc_sf_fields = {'unique_id': 'SOURCE_FEA',
                 'uri': None,
                 'scientific_name': 'SNAME',
                 'min_date': None,
                 'max_date': None,
                 'eo_rank': None}

eccc_critical_habitat_fields = {'unique_id': 'Identifier',
                                'uri': None,
                                'scientific_name': 'SciName',
                                'min_date': None,
                                'max_date': None,
                                'eo_rank': None}

ncc_endemics_polygons_fields = {'unique_id': 'OBJECTID',
                                'uri': 'Link',
                                'scientific_name': 'MATCH_NSC',
                                'min_date': None,
                                'max_date': None,
                                'eo_rank': None}
