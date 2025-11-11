import deepl

auth_key = "87b2d0f7-f933-4ce9-95ef-80974e2a8a55:fx" # replace with your key
deepl_client = deepl.DeepLClient(auth_key)

input_text = "Input records - 1 iNaturalist.ca (2025); Expert Ecoshape Review<br>Syd Cannings Reviewer Comment - Within known range; no reason to expect extirpation in this region"
result = deepl_client.translate_text(input_text, source_lang="EN", target_lang="FR")
print(result.text)
