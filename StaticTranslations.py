# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Samantha Stefanoff
# © NatureServe Canada 2026 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: StaticTranslations.py
# Translation dictionaries for EN to FR


range_map_scope_translation = {
    'N': 'Canadien',
    'A': 'Nord-américain',
    'G': 'mondial'}


presence_translation = {
    'P': 'Présente',
    'X': 'Présence attendue',
    'H': 'Historique'}


usage_type_translation = {
    'B': 'Reproduction',
    'P': 'Reproduction possible',
    'M': 'Migration'}


# controlling process - for testing
if __name__ == '__main__':
    print(range_map_scope_translation['A'])
    