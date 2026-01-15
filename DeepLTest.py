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
# print(EBARUtils.translateENtoFRUsingDeepL('go to NatureServe Explorer'))
print(EBARUtils.translateENtoFRUsingDeepL('translated by DeepL'))
