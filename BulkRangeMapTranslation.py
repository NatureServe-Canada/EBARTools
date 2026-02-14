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
                summary_fr = summary_fr.replace('Expert Reviews', "Avis d'experts")
                summary_fr = summary_fr.replace('Anonymous', 'Anonyme')
            reviewer_comments_fr = update_row['ReviewerComments']
            if reviewer_comments_fr:
                # reviewer_comments_fr = reviewer_comments_fr.replace('Reviewer Comment', 'Commentaire du réviseur')
                # reviewer_comments_fr = reviewer_comments_fr.replace('Anonymous', 'Anonyme')
                # reviewer_comments_fr = reviewer_comments_fr.replace('Unpublished', 'Non publié')
                reviewer_comments_fr = EBARUtils.translateENtoFRUsingDeepL(reviewer_comments_fr) + \
                    ' (traduit par DeepL)'
            update_cursor.updateRow([update_row['RangeStage'], stage_fr, update_row['RangeMapScope'],
                                     StaticTranslations.range_map_scope_translation[update_row['RangeMapScope']],
                                     update_row['RangeMapNotes'], notes_fr, update_row['RangeMetadata'], summary_fr,
                                     update_row['ReviewerComments'], reviewer_comments_fr])

    # RangeMapEcoshape
    with arcpy.da.UpdateCursor(geodatabase + '/RangeMapEcoshape',
                               ['RangeMapEcoshapeNotes', 'RangeMapEcoshapeNotes_FR'],
                               'RangeMapID = ' + str(range_map_id)) as update_cursor:
        for update_row in EBARUtils.updateCursor(update_cursor):
            notes_fr = update_row['RangeMapEcoshapeNotes']
            if notes_fr:
                # notes_fr = notes_fr.replace('Input Records', 'Enregistrements saisis')
                # notes_fr = notes_fr.replace('Expert Ecoshape Review', "Avis d'experts Ecoshape")
                # notes_fr = notes_fr.replace('Reviewer Comment', 'Commentaire du réviseur')
                # notes_fr = notes_fr.replace('Anonymous', 'Anonyme')
                # notes_fr = notes_fr.replace('Unpublished', 'Non publié')
                notes_fr = EBARUtils.translateENtoFRUsingDeepL(notes_fr) + ' (traduit par DeepL)'
            update_cursor.updateRow([update_row['RangeMapEcoshapeNotes'], notes_fr])
