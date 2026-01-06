# import deepl

# auth_key = "replace with your key"
# deepl_client = deepl.DeepLClient(auth_key)

# input_text = "Input records - 1 iNaturalist.ca (2025); Expert Ecoshape Review<br>Syd Cannings Reviewer Comment - Within known range; no reason to expect extirpation in this region"
# result = deepl_client.translate_text(input_text, source_lang="EN", target_lang="FR")
# print(result.text)


# g_var = None

# def test_func():
#     global g_var
#     if not g_var:
#         g_var = 1
#     else:
#         g_var += 1
#     return g_var


# if __name__ == '__main__':
#     print(str(test_func()))
#     print(str(test_func()))
#     print(str(test_func()))


import EBARUtils

# print(EBARUtils.translateENtoFRUsingDeepL('Random text to be translated...'))
# print(EBARUtils.translateENtoFRUsingDeepL('More text to be translated. This time with punctuation!'))
print(EBARUtils.translateENtoFRUsingDeepL('map and metadata for EBAR for each species within category/taxa group'))
print(EBARUtils.translateENtoFRUsingDeepL('background information on range map production, ecoshape sources and related topics'))
print(EBARUtils.translateENtoFRUsingDeepL('files comprising polygons shapefile of all ecoshapes'))
print(EBARUtils.translateENtoFRUsingDeepL('files comprising polygons shapefile of all generalized ecoshapes'))
print(EBARUtils.translateENtoFRUsingDeepL('table of species and range attributes for EBAR for all species within category/taxa group'))
print(EBARUtils.translateENtoFRUsingDeepL('table of per-ecoshape attributes for EBAR for all species within category/taxa group'))
print(EBARUtils.translateENtoFRUsingDeepL('table of jurisdictions'))
print(EBARUtils.translateENtoFRUsingDeepL('ArcGIS Pro project file for each species within category/taxa group, referencing the data files above, with appropriate definition queries and joins'))
print(EBARUtils.translateENtoFRUsingDeepL('ArcGIS Pro map file for each species within category/taxa group, referencing the data files above, with appropriate definition queries and joins'))
print(EBARUtils.translateENtoFRUsingDeepL('ArcGIS Pro layer file for each species within category/taxa group, with suggested symbology and appropriate definition queries and joins, referencing the original ecoshapes'))
print(EBARUtils.translateENtoFRUsingDeepL('ArcGIS Pro layer file for each species within category/taxa group, with suggested symbology and definition queries and appropriate joins, referencing the generalized ecoshapes'))
print(EBARUtils.translateENtoFRUsingDeepL('ArcMap project file referencing the data files above'))
print(EBARUtils.translateENtoFRUsingDeepL('ArcMap layer file, with suggested symbology and appropriate joins, referencing the original ecoshapes'))
print(EBARUtils.translateENtoFRUsingDeepL('ArcMap layer file, with suggested symbology and appropriate joins, referencing the generalized ecoshapes'))
print(EBARUtils.translateENtoFRUsingDeepL('ArcMap layer file, with suggested symbology and appropriate joins, referencing usage type, where applicable, of generalized ecoshapes'))
