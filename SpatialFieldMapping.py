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
                 'rep_accuracy': 'EST_REP_AC',
                 'eo_rank': 'BASIC_EO_R'}

bc_eo_fields = {'unique_id': 'OCCR_ID',
                'uri': None,
                'scientific_name': 'SCI_NAME',
                'min_date': 'FIRST_OBS',
                'max_date': 'LAST_OBS',
                'rep_accuracy': None,
                'eo_rank': 'RANK'}

cdc_sf_fields = {'unique_id': 'SOURCE_FEA',
                 'uri': None,
                 'scientific_name': 'SNAME',
                 'min_date': None,
                 'max_date': 'MAX_DATE',
                 'rep_accuracy': 'EST_REP_AC',
                 'eo_rank': None}

eccc_critical_habitat_fields = {'unique_id': 'Identifier',
                                'uri': None,
                                'scientific_name': 'SciName',
                                'min_date': None,
                                'max_date': None,
                                'rep_accuracy': None,
                                'eo_rank': None}

ncc_endemics_polygons_fields = {'unique_id': 'OBJECTID',
                                'uri': 'Link',
                                'scientific_name': 'MATCH_NSC',
                                'min_date': None,
                                'max_date': None,
                                'rep_accuracy': None,
                                'eo_rank': None}

spatial_field_mapping_dict = {'NU CDC Element Occurrences': cdc_eo_fields,
                              'YT CDC Element Occurrences': cdc_eo_fields,
                              'BC CDC Element Occurrences': bc_eo_fields,
                              'NU CDC Source Feature Polygons': cdc_sf_fields,
                              'YT CDC Source Feature Polygons': cdc_sf_fields,
                              'NU CDC Source Feature Points': cdc_sf_fields,
                              'YT CDC Source Feature Points': cdc_sf_fields,
                              'YT CDC Source Feature Lines': cdc_sf_fields,
                              'ECCC Critical Habitat': eccc_critical_habitat_fields,
                              'NCC Endemics Literature': ncc_endemics_polygons_fields}
