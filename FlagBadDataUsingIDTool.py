# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Gabrielle Miller
# © NatureServe Canada 2021 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: FlagBadDataUsingIDTool.py
# ArcGIS Python tool for flagging bad input data using an InputPoint/Line/PolygonID

# Notes:
# - Normally called from EBAR Tools.pyt, unless doing interactive debugging
#   (see controlling process at the end of this file)


# import Python packages
import EBARUtils
import arcpy
import datetime


class FlagBadDataUsingIDTool:
    """Flag bad input data using an InputPoint/Line/PolygonID"""
    def __init__(self):
        pass

    def runFlagBadDataUsingIDTool(self, parameters, messages, quiet=False):
        # check out any needed extension licenses
        #arcpy.CheckOutExtension('Spatial')

        # start time
        start_time = datetime.datetime.now()
        if not quiet:
            EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        if not quiet:
            EBARUtils.displayMessage(messages, 'Processing parameters')
        param_geodatabase = parameters[0].valueAsText
        param_input_point_id = parameters[1].valueAsText
        param_input_line_id = parameters[2].valueAsText
        param_input_polygon_id = parameters[3].valueAsText
        param_justification = parameters[4].valueAsText
        param_undo = parameters[5].valueAsText
        id_count = 0
        if param_input_point_id:
            id_count += 1
            input_table = param_geodatabase + '/InputPoint'
            bad_table  = param_geodatabase + '/BadInputPoint'
            id_field = 'InputPointID'
            id_value = param_input_point_id
        if param_input_line_id:
            id_count += 1
            input_table = param_geodatabase + '/InputLine'
            bad_table  = param_geodatabase + '/BadInputLine'
            id_field = 'InputLineID'
            id_value = param_input_line_id
        if param_input_polygon_id:
            id_count += 1
            input_table = param_geodatabase + '/InputPolygon'
            bad_table  = param_geodatabase + '/BadInputPolygon'
            id_field = 'InputPolygonID'
            id_value = param_input_polygon_id
        if id_count == 0:
            EBARUtils.displayMessage(messages, 'ERROR: Please provide one ID')
            # terminate with error
            return
        if id_count > 1:
            EBARUtils.displayMessage(messages, 'ERROR: Please provide only one ID')
            # terminate with error
            return
        if param_undo == 'false' and not param_justification:
            EBARUtils.displayMessage(messages, 'ERROR: Please provide a justification')
            # terminate with error
            return

        if param_undo == 'false':
            # check for record
            arcpy.MakeFeatureLayer_management(input_table, 'input_layer', id_field + ' = ' + id_value)
            result = arcpy.GetCount_management('input_layer')
            if int(result[0]) == 0:
                EBARUtils.displayMessage(messages, 'ERROR: input record with specified ID not found')
                # terminate with error
                return

            # check for SF or EO
            if EBARUtils.checkSFEO(param_geodatabase, input_table.rsplit('/')[-1], id_field, id_value):
                EBARUtils.displayMessage(messages, 'ERROR: Source Features and Element Occurrences cannot be flagged')
                # terminate with error
                return

            # check for related records
            if EBARUtils.checkInputRelatedRecords(param_geodatabase + '/Visit', id_field + ' = ' + id_value):
                EBARUtils.displayMessage(messages, 'ERROR: related Visit record prevents flagging')
                # terminate with error
                return
            if EBARUtils.checkInputRelatedRecords(param_geodatabase + '/InputFeedback', id_field + ' = ' + id_value):
                EBARUtils.displayMessage(messages, 'ERROR: related InputFeedback record prevents flagging')
                # terminate with error
                return
            if EBARUtils.checkInputRelatedRecords(param_geodatabase + '/SecondaryInput', id_field + ' = ' + id_value):
                EBARUtils.displayMessage(messages, 'ERROR: related SecondaryInput record prevents flagging')
                # terminate with error
                return

            # create InputFeedback record, append to bad, delete input
            if not quiet:
                EBARUtils.displayMessage(messages, 'Saving InputFeedback and appending Bad record')
            with arcpy.da.InsertCursor(param_geodatabase + '/InputFeedback',
                                       ['Bad' + id_field, 'Justification']) as insert_cursor:
                insert_cursor.insertRow([id_value, param_justification])
            EBARUtils.appendUsingCursor('input_layer', bad_table)
            if not quiet:
                EBARUtils.displayMessage(messages, 'Deleting original Input record')
            arcpy.DeleteRows_management('input_layer')
        else:
            # check for record
            arcpy.MakeFeatureLayer_management(bad_table, 'bad_input_layer', id_field + ' = ' + id_value)
            result = arcpy.GetCount_management('bad_input_layer')
            if int(result[0]) == 0:
                EBARUtils.displayMessage(messages, 'ERROR: bad record with specified ID not found')
                # terminate with error
                return

            # delete InputFeedback record, append to input, delete bad
            if not quiet:
                EBARUtils.displayMessage(messages, 'Deleting InputFeedback and re-adding Input record')
            EBARUtils.deleteRows(param_geodatabase + '/InputFeedback', 'if_view', 'Bad' + id_field + ' = ' + id_value)
            # don't copy back the id field; a new one will be generated
            if param_input_point_id:
                skip_fields_lower = ['inputpointid']
            if param_input_line_id:
                skip_fields_lower = ['inputlineid']
            if param_input_polygon_id:
                skip_fields_lower = ['inputpolygonid']
            EBARUtils.appendUsingCursor('bad_input_layer', input_table, skip_fields_lower=skip_fields_lower)
            if not quiet:
                EBARUtils.displayMessage(messages, 'Deleting Bad record')
            arcpy.DeleteRows_management('bad_input_layer')

        # clean up
        if arcpy.Exists('input_layer'):
            arcpy.Delete_management('input_layer')
        if arcpy.Exists('bad_input_layer'):
            arcpy.Delete_management('bad_input_layer')

        # end time
        end_time = datetime.datetime.now()
        if not quiet:
            EBARUtils.displayMessage(messages, 'End time: ' + str(end_time))
        elapsed_time = end_time - start_time
        if not quiet:
            EBARUtils.displayMessage(messages, 'Elapsed time: ' + str(elapsed_time))
        return


# controlling process
if __name__ == '__main__':
    fbdui = FlagBadDataUsingIDTool()
    # hard code parameters for debugging
    for pid in (16,32,38,39,43,44,74,81,91,118,119,120,135,137,140,147,156,167,178,198,202,211,227,249,254,255,259,268,271,281,283,285,299,317,318,321,322,323,326,347,353,363,366,378,384,395,402,408,417,430,433,436,440,441,448,449,454,460,462,474,475,478,488,489,502,508,520,543,569,575,576,583,597,617,622,624,626,633,640,642,643,649,650,661,689,694,701,716,723,731,733,740,743,746,751,759,760,783,784,801,804,811,826,869,879,881,891,901,915,916,938,939,940,964,965,968,973,974,990,994,998,1001,1010,1041,1069,1078,1086,1092,1111,1114,1118,1137,1139,1148,1156,1157,1162,1164,1194,1195,1204,1214,1219,1228,1234,1249,1258,1260,1274,1288,1292,1296,1302,1307,1330,1348,1350,1354,1356,1357,1360,1365,1373,1377,1378,1381,1398,1414,1430,1439,1445,1451,1467,1469,1492,1496,1536,1545,1549,1553,1570,1578,1579,1581,1592,1593,1596,1615,1619,1626,1633,1636,1664,1675,1680,1684,1688,1694,1697,1714,1720,1725,1763,1770,1779,1790,1793,1812,1823,1825,1862,1865,1866,1875,1880,1881,1883,1884,1900,1902,1907,1911,1925,1926,1933,1938,1942,1955,1956,1959,1966,1983,1984,1985,1988,1994,1996,2003,2007,2008,2012,2021,2038,2069,2083,2085,2101,2110,2113,2128,2129,2140,2159,2173,2175,2180,2184,2189,2190,2205,2206,2228,2229,2233,2244,2250,2263,2265,2278,2282,2283,2292,2294,2295,2320,2321,2330,2339,2342,2344,2345,2346,2374,2381,2402,2404,2408,2418,2425,2438,2441,2442,2449,2465,2481,2500,2503,2506,2518,2542,2566,2568,2584,2588,2590,2608,2621,2625,2647,2651,2653,2665,2667,2679,2680,2686,2689,2696,2703,2704,2708,2725,2731,2733,2741,2768,2770,2773,2780,2785,2793,2794,2796,2799,2808,2836,2843,2858,2888,2894,2898,2899,2900,2902,2905,2907,2921,2924,2941,2943,2948,2950,2987,2995,2996,3000,3007,3013,3032,3034,3040,3042,3044,3046,3055,3060,3063,3064,3068,3077,3078,3081,3082,3105,3111,3119,3125,3129,3150,3154,3157,3177,3183,3187,3189,3191,3194,3195,3202,3205,3208,3227,3229,3236,3238,3242,3246,3251,3252,3262,3264,3267,3279,3282,3283,3309,3314,3327,3338,3341,3351,3355,3361,3382,3409,3411,3429,3462,3467,3468,3474,3491,3504,3508,3520,3534,3540,3544,3567,3573,3579,3581,3582,3589,3590,3598,3599,3611,3617,3623,3626,3627,3637,3641,3643,3644,3649,3677,3683,3685,3693,3712,3714,3715,3721,3727,3732,3746,3751,3765,3766,3768,3776,3777,3798,3799,3808,3810,3823,3825,3827,3830,3831,3833,3847,3851,3855,3856,3862,3870,3877,3885,3897,3904,3905,3908,3920,3939,3940,3944,3945,3964,3966,3967,3970,4012,4017,4026,4049,4058,4064,4078,4081,4095,4097,4098,4107,4111,4119,4128,4137,4153,4154,4157,4158,4161,4176,4182,4195,4200,4212,4218,4230,4234,4247,4274,4280,4282,4284,4285,4302,4306,4312,4323,4348,4358,4365,4371,4380,4382,4383,4385,4401,4415,4427,4429,4436,4442,4444,4457,4460,4464,4480,4485,4488,4495,4500,4505,4517,4518,4526,4528,4533,4546,4547,4548,4550,4557,4562,4564,4576,4583,4589,4595,4605,4612,4615,4616,4621,4624,4626,4630,4639,4641,4648,4658,4674,4710,4715,4720,4733,4734,4748,4759,4762,4772,4773,4779,4784,4794,4796,4805,4806,4816,4826,4843,4854,4859,4868,4874,4879,4882,4886,4891,4892,4898,4913,4923,4930,4936,4937,4944,4952,4955,4956,4961,4962,4973,4974,4988,5005,5012,5013,5033,5039,5058,5070,5116,5121,5128,5137,5155,5159,5163,5167,5173,5175,5180,5181,5192,5193,5199,5205,5209,5215,5223,5236,5241,5247,5255,5256,5272,5278,5281,5290,5295,5312,5315,5318,5320,5339,5351,5363,5402,5423,5459,5463,5472,5478,5489,5499,5504,5514,5520,5527,5530,5536,5539,5543,5545,5552,5557,5561,5572,5573,5574,5584,5595,5604,5612,5626,5641,5646,5653,5675,5679,5687,5688,5689,5725,5733,5750,5752,5757,5758,5765,5806,5816,5824,5828,5835,5840,5845,5858,5863,5884,5889,5905,5919,5928,5932,5941,5943,5946,5956,5957,5970,5975,5995,5996,5998,6008,6015,6019,6023,6038,6046,6062,6069,6074,6083,6084,6093,6115,6117,6124,6129,6146,6158,6162,6176,6181,6199,6202,6205,6227,6230,6233,6234,6238,6240,6257,6270,6295,6296,6306,6315,6330,6332,6346,6354,6370,6372,6379,6380,6404,6417,6418,6438,6443,6448,6455,6498,6501,6502,6511,6512,6516,6531,6550,6562,6577,6579,6582,6583,6598,6601,6608,6615,6623,6630,6638,6642,6644,6646,6653,6659,6672,6678,6680,6683,6708,6727,6733,6740,6746,6752,6783,6786,6792,6808,6811,6812,6813,6816,6823,6844,6846,6852,6856,6862,6864,6866,6880,6890,6898,6904,6911,6913,6920,6923,6930,6935,6964,6969,6978,6993,7003,7004,7011,7020,7022,7029,7039,7046,7049,7050,7052,7055,7058,7069,7080,7086,7090,7092,7094,7101,7105,7109,7110,7111,7117,7120,7129,7136,7143,7144,7147,7153,7155,7160,7168,7199,7204,7205,7214,7232,7242,7259,7263,7271,7274,7282,7291,7315,7317,7319,7321,7323,7324,7328,7333,7343,7356,7367,7397,7403,7407,7408,7419,7462,7506,7521,7522,7533,7539,7551,7568,7581,7582,7583,7593,7595,7598,7601,7614,7633,7636,7638,7643,7646,7654,7655,7663,7665,7672,7673,7674,7676,7715,7718,7726,7734,7736,7744,7747,7766,7769,7770,7771,7774,7779,7780,7790,7793,7796,7798,7805,7806,7817,7829,7846,7852,7853,7867,7871,7875,7879,7880,7893,7907,7908,7929,7930,7932,7935,7936,7938,7945,7949,7954,7965,7966,7967,7974,7990,8008,8019,8030,8032,8037,8040,8047,8055,8056,8080,8082,8083,8095,8108,8113,8160,8191,8194,8203,8204,8205,8210,8226,8227,8231,8237,8247,8253,8255,8259,8260,8267,8269,8273,8280,8288,8301,8310,8324,8331,8332,8333,8339,8345,8353,8363,8381,8382,8401,8402,8407,8415,8417,8419,8424,8428,8435,8441,8449,8457,8458,8459,8461,8472,8475,8483,8489,8494,8496,8497,8498,8502,8509,8519,8527,8532,8534,8536,8539,8554,8562,8578,8589,8604,8643,8651,8654,8662,8670,8701,8703,8705,8709,8715,8717,8720,8724,8734,8739,8742,8744,8745,8746,8776,8785,8797,8802,8811,8823,8827,8841,8844,8849,8857,8863,8882,8883,8895,8904,8911,8913,8922,8926,8933,8937,8956,8962,8977,8980,8988,8990,8996,9002,9006,9008,9011,9020,9021,9023,9030,9031,9032,9038,9043,9052,9065,9071,9075,9082,9087,9089,9114,9118,9122,9130,9133,9134,9139,9155,9168,9180,9181,9184,9185,9192,9209,9215,9217,9223,9231,9241,9256,9272,9278,9279,9282,9285,9286,9287,9288,9293,9315,9319,9321,9322,9323,9325,9347,9349,9351,9365,9366,9367,9372,9374,9379,9383,9388,9391,9398,9402,9411,9424,9425,9426,9433,9435,9438,9440,9460,9464,9471,9478,9479,9500,9510,9518,9527,9538,9542,9545,9553,9559,9564,9584,9586,9591,9604,9607,9619,9623,9624,9628,9632,9642,9645,9657,9660,9679,9689,9698,9700,9707,9710,9714,9729,9740,9752,9766,9770,9785,9794,9795,9797,9807,9816,9832,9840,9842,9844,9848,9876,9877,9894,9897,9898,9914,9921,9922,9926,9935,9938,9945,9946,9949,9960,9963,9982,10001,10007,10010,10020,10042,10049,10055,10061,10062,10068,10083,10098,10104,10106,10108,10109,10133,10134,10140,10155,10160,10164,10169,10170,10171,10177,10184,10185,10187,10200,10211,10215,10228,10232,10240,10246,10250,10251,10256,10270,10283,10293,10296,10301,10309,10316,10317,10325,10331,10341,10344,10351,10355,10361,10374,10375,10379,10380,10409,10415,10429,10434,10437,10448,10456,10470,10475,10480,10502,10506,24299,24318,24325,24326,24333,24339,24353,24359,24365,24379,24381,24384,24396,24407,24416,24423,24425,24432,24438,24443,24450,24464,24468,24470,24484,24488,24492,24500,24506,24514,24516,24532,24536,24546,24556,24578,24594,24605,24609,24616,24628,24632,24636,24640,24644,24648,24656,24677,24678,24696,24709,24710,24735,24742,24772,24777,24782,24787,24788,24794,24810,24836,24846,24847,24854,24856,24862,24869,24892,24895,24896,24911,24917,24923,24925,24936,24938,24947,24952,24954,24960,24961,24966,24973,24976,25001,25010,25013,25038,25043,25045,25049,25060,25086,25109,25110,25115,25129,25143,25149,25151,25169,25170,25171,25172,25174,25195,25197,25209,25215,25221,25225,25245,25270,25276,25301,25325,25332,25337,25342,25343,25345,25353,25361,25363,25366,25369,25372,25375,25383,25390,25402,25414,25420,25442,25448,25456,25458,25467,25477,25480,25487,25494,25501,25515,25529,25552,25555,25563,25570,25582,25587,25592,25600,25611,25617,25633,25635,25645,25659,25661,25670,25671,25683,25684,25693,25701,25750,25752,25757,25760,25769,25771,25782,25830,25831,25832,25837,25845,25847,25874,25881,25885,25896,25917,25938,25940,25951,25952,25968,25979,25983,25988,25996,26002,26004,26005,26018,26020,26027,26043,26048,26051,26070,26071,26097,26100,26103,26117,26125,26130):
        param_geodatabase = arcpy.Parameter()
        param_geodatabase.value = 'C:/GIS/EBAR/EBAR-KBA-Dev.gdb'
        param_input_point_id = arcpy.Parameter()
        param_input_point_id.value = None
        param_input_line_id = arcpy.Parameter()
        param_input_line_id.value = None
        param_input_polygon_id = arcpy.Parameter()
        param_input_polygon_id.value = str(pid)
        param_justification = arcpy.Parameter()
        param_justification.value = None
        param_undo = arcpy.Parameter()
        param_undo.value = 'true'
        parameters = [param_geodatabase, param_input_point_id, param_input_line_id, param_input_polygon_id,
                      param_justification, param_undo]
        fbdui.runFlagBadDataUsingIDTool(parameters, None)
