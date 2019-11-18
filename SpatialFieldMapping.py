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

ab_eo_fields = {'unique_id': 'EO_ID',
                'uri': None,
                'scientific_name': 'SNAME',
                'min_date': None,
                'max_date': 'LAST_OBS_D',
                'rep_accuracy': None,
                'eo_rank': None}

bc_eo_fields = {'unique_id': 'OCCR_ID',
                'uri': None,
                'scientific_name': 'SCI_NAME',
                'min_date': 'FIRST_OBS',
                'max_date': 'LAST_OBS',
                'rep_accuracy': None,
                'eo_rank': 'RANK'}

mt_plant_so_fields = {'unique_id': 'SO_ID',
                      'uri': None,
                      'scientific_name': 'S_Sci_Name',
                      'min_date': 'First_Obs_Date',
                      'max_date': 'Last_Obs_Date',
                      'rep_accuracy': 'Rep_Accuracy',
                      'eo_rank': 'SO_Rank'}

mt_animal_so_fields = {'unique_id': 'SO_ID',
                       'uri': None,
                       'scientific_name': 'S_Sci_Name',
                       'min_date': 'First_Obs_Date',
                       'max_date': 'Last_Obs_Date',
                       'rep_accuracy': None,
                       'eo_rank': None}

cdc_sf_fields = {'unique_id': 'SOURCE_FEA',
                 'uri': None,
                 'scientific_name': 'SNAME',
                 'min_date': None,
                 'max_date': 'MAX_DATE',
                 'rep_accuracy': 'EST_REP_AC',
                 'eo_rank': None}

mt_sf_fields = {'unique_id': 'Obs_ID',
                'uri': None,
                'scientific_name': 'S_Sci_Name',
                'min_date': 'Obs_Date_Start',
                'max_date': 'Obs_Date_End',
                'rep_accuracy': None,
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
                              'AB CDC Element Occurrences': ab_eo_fields,
                              'MT Species Occurrence Plants': mt_plant_so_fields,
                              'MT Species Occurrence Animals': mt_animal_so_fields,
                              'NU CDC Source Feature Polygons': cdc_sf_fields,
                              'YT CDC Source Feature Polygons': cdc_sf_fields,
                              'NU CDC Source Feature Points': cdc_sf_fields,
                              'MT Source Feature Points': mt_sf_fields,
                              'YT CDC Source Feature Points': cdc_sf_fields,
                              'YT CDC Source Feature Lines': cdc_sf_fields,
                              'ECCC Critical Habitat': eccc_critical_habitat_fields,
                              'NCC Endemics Literature': ncc_endemics_polygons_fields}
