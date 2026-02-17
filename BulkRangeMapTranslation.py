import arcpy
import EBARUtils
import StaticTranslations


range_map_ids = [3850]
geodatabase = r'C:\GIS\EBAR\nsc-gis-ebarkba.sde'
for range_map_id in range_map_ids:
    print('Translating ' + str(range_map_id))
    # RangeMap
    with arcpy.da.UpdateCursor(geodatabase + '/RangeMap',
                               ['RangeStage', 'RangeStage_FR', 'RangeMapScope', 'RangeMapScope_FR', 'RangeMapNotes',
                                'RangeMapNotes_FR', 'RangeMetadata', 'RangeMetadata_FR', 'ReviewerComments',
                                'ReviewerComments_FR'], 'RangeMapID = ' + str(range_map_id)) as update_cursor:
        for update_row in EBARUtils.updateCursor(update_cursor):
            stage_fr = None
            if update_row['RangeStage'] in StaticTranslations.range_stage_translation.keys():
                stage_fr = StaticTranslations.range_stage_translation[update_row['RangeStage']]
            notes_fr = update_row['RangeMapNotes']
            if notes_fr:
                notes_fr = notes_fr.replace('Primary Species', 'Espèce primaire')
                notes_fr = notes_fr.replace('Secondary Species', 'Espèces secondaires')
                notes_fr = notes_fr.replace('Synonyms', 'Synonymes')
            summary_fr = update_row['RangeMetadata']
            if summary_fr:
                summary_fr = summary_fr.replace('Input Records', 'Enregistrements saisis')
                summary_fr = summary_fr.replace('Input records', 'Enregistrements saisis')
                summary_fr = summary_fr.replace('Expert Reviews', "Avis d'experts")
                summary_fr = summary_fr.replace('Anonymous', 'Anonyme')
            reviewer_comments_fr = update_row['ReviewerComments']
            if reviewer_comments_fr:
                sections = reviewer_comments_fr.split('<br>')
                reviewer_comments_fr = ''
                used_deepl = False
                for section in sections:
                    # each subsection is a reviewer comment
                    subsections = section.split(' - ')
                    prefix = subsections[0]
                    prefix = prefix.replace('Reviewer Comment', 'Commentaire du réviseur')
                    prefix = prefix.replace('Anonymous', 'Anonyme')
                    postfix = subsections[1]
                    if postfix == 'Unpublished':
                        postfix = 'Non publié'
                    else:
                        postfix = EBARUtils.translateENtoFRUsingDeepL(postfix)
                        used_deepl = True
                    if len(reviewer_comments_fr) > 0:
                        reviewer_comments_fr += '<br>'
                    reviewer_comments_fr += prefix + ' - ' + postfix
                if used_deepl:
                    reviewer_comments_fr += ' (traduit par DeepL)'
            update_cursor.updateRow([update_row['RangeStage'], stage_fr, update_row['RangeMapScope'],
                                     StaticTranslations.range_map_scope_translation[update_row['RangeMapScope']],
                                     update_row['RangeMapNotes'], notes_fr, update_row['RangeMetadata'], summary_fr,
                                     update_row['ReviewerComments'], reviewer_comments_fr])

    # RangeMapEcoshape
    with arcpy.da.UpdateCursor(geodatabase + '/RangeMapEcoshape',
                               ['RangeMapEcoshapeNotes', 'RangeMapEcoshapeNotes_FR'],
                               'RangeMapID = ' + str(range_map_id),
                               sql_clause=[None, 'ORDER BY RangeMapEcoshapeID ASC']) as update_cursor:
        for update_row in EBARUtils.updateCursor(update_cursor):
            #print(update_row['RangeMapEcoshapeNotes'])
            notes_fr = update_row['RangeMapEcoshapeNotes']
            if notes_fr:
                sections = notes_fr.split('<br>')
                used_deepl = False
                notes_fr = sections[0]
                notes_fr = notes_fr.replace('Input records', 'Enregistrements saisis')
                # SHOULD ALSO INCORPORATE TRANSLATED DatasetSourceNames!!!
                notes_fr = notes_fr.replace('Expert Ecoshape Review', "Avis d'experts Ecoshape")
                # each subsequent section is a reviewer comment
                for section in sections[1:]:
                    subsections = section.split(' - ')
                    prefix = subsections[0]
                    prefix = prefix.replace('Reviewer Comment', 'Commentaire du réviseur')
                    prefix = prefix.replace('Anonymous', 'Anonyme')
                    prefix = prefix.replace('Expert Ecoshape Review', "Avis d'experts Ecoshape")
                    postfix = subsections[1]
                    if postfix == 'Unpublished':
                        postfix = 'Non publié'
                    else:
                        postfix = EBARUtils.translateENtoFRUsingDeepL(postfix)
                        used_deepl = True
                    notes_fr += '<br>' + prefix + ' - ' + postfix
                if used_deepl:
                    notes_fr += ' (traduit par DeepL)'
            update_cursor.updateRow([update_row['RangeMapEcoshapeNotes'], notes_fr])
