# encoding: utf-8

import requests
import json

print('Get Taxon')
print('---------')
r = requests.get('https://explorer.natureserve.org/api/data/taxon/ELEMENT_GLOBAL.2.112976')
parsed = json.loads(r.content)
for k in parsed:
    print(k + ': ' + str(parsed[k]))
if parsed['speciesGlobal']['saraStatus']:
    print('saraStatus: ' + parsed['speciesGlobal']['saraStatus'])
if parsed['speciesGlobal']['saraStatusDate']:
    print('saraStatusDate: ' + parsed['speciesGlobal']['saraStatusDate'])
if parsed['speciesGlobal']['interpretedCosewic']:
    print('interpretedCosewic: ' + parsed['speciesGlobal']['interpretedCosewic'])
if parsed['speciesGlobal']['cosewicDate']:
    print('cosewicDate: ' + parsed['speciesGlobal']['cosewicDate'])

print('')
print('Species Search (nation=CA)')
print('--------------------------')
url = 'https://explorer.natureserve.org/api/data/search'
headers = {'Accept': 'application/json', 'Content-Type': 'application/json; charset=UTF-8'}
params = {'criteriaType': 'combined',
          #'textCriteria': [{'paramType': 'quickSearch',
          #                  'searchToken': 'IICOL7C012'}]}
          #'textCriteria': [{'paramType': 'textSearch',
          #                  'searchToken': 'ABNCA03012',
          #                  'matchAgainst': 'code',
          #                  'operator': 'equals'}]}
          'textCriteria': [{'paramType': 'textSearch',
                            'searchToken': 'IILEYGA040',
                            'matchAgainst': 'code',
                            'operator': 'equals'}]}
          #'locationCriteria': [{'paramType': 'nation',
          #                      'nation': 'CA'}]}
payload = json.dumps(params)
r = requests.post(url, data=payload, headers=headers)
content = json.loads(r.content)
results = content['results']
for k in results[0]:
    print(k + ': ' + str(results[0][k]))
    if k == 'nations':
        for knation in results[0][k]:
            if knation['nationCode'] == 'CA':
                print('CA roundedNRank: ' + knation['roundedNRank'])
                print('CA exotic: ' + str(knation['exotic']))
                for ksub in knation['subnations']:
                    if ksub['subnationCode'] == 'NF':
                        print('NF roundedSRank: ' + ksub['roundedSRank'])
                        print('NF exotic: ' + str(ksub['exotic']))
                    if ksub['subnationCode'] == 'LB':
                        print('LB roundedSRank: ' + ksub['roundedSRank'])
                        print('LB exotic: ' + str(ksub['exotic']))
            if knation['nationCode'] == 'US':
                print('US roundedNRank: ' + knation['roundedNRank'])
                print('US exotic: ' + str(knation['exotic']))
if results[0]['speciesGlobal']['cosewicCode']:
    print('cosewicCode: ' + results[0]['speciesGlobal']['cosewicCode'])
if results[0]['speciesGlobal']['saraCode']:
    print('saraCode: ' + results[0]['speciesGlobal']['saraCode'])

