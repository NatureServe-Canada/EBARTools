# encoding: utf-8

# Project: Ecosytem-based Automated Range Mapping (EBAR)
# Credits: Randal Greene, Gabrielle Miller
# © NatureServe Canada 2022 under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

# Program: PackageECCCPrioritySpecies.py
# Unpublished ArcGIS Python tool for creating Zip of PDFs and Spatial Data for all ECCC Priority Species

# Notes:
# - For one off or very occasional use only, so not integrated into the EBARTools toolbox
#   (see controlling process at the end of this file)


# import Python packages
import EBARUtils
import shutil
import arcpy
import datetime


class PackageECCCPrioritySpeciesTool:
    """Create Zip of PDFs and Spatial Data for all ECCC Priority Species"""
    def __init__(self):
        pass

    def processPackage(self, messages, range_map_ids, attributes_dict, zip_folder, metadata):
        # export range maps, with biotics/species additions
        EBARUtils.displayMessage(messages, 'Exporting RangeMap records to CSV')
        EBARUtils.ExportRangeMapToCSV('range_map_view_pkg', range_map_ids, attributes_dict, zip_folder, 'RangeMap.csv',
                                      metadata, messages)

        # export range map ecoshapes
        EBARUtils.displayMessage(messages, 'Exporting RangeMapEcoshape records to CSV')
        EBARUtils.ExportRangeMapEcoshapesToCSV('range_map_ecoshape_view', range_map_ids, zip_folder,
                                               'RangeMapEcoshape.csv', metadata)

        # export ecoshapes
        EBARUtils.displayMessage(messages, 'Exporting Ecoshape polygons to shapefile')
        EBARUtils.ExportEcoshapesToShapefile('ecoshape_layer', 'range_map_ecoshape_view', zip_folder, 'Ecoshape.shp',
                                             metadata, True)

        # export overview ecoshapes
        EBARUtils.displayMessage(messages, 'Exporting EcoshapeOverview polygons to shapefile')
        EBARUtils.ExportEcoshapeOverviewsToShapefile('ecoshape_overview_layer', 'range_map_ecoshape_view', zip_folder, 
                                                     'EcoshapeOverview.shp', metadata, True)

        # copy ArcMap template
        EBARUtils.displayMessage(messages, 'Copying ArcMap template')
        shutil.copyfile(EBARUtils.resources_folder + '/EBAR.mxd', zip_folder + '/EBAR_ECCC_2023-24_Species.mxd')
        # shutil.copyfile(EBARUtils.resources_folder + '/EBAR.mxd', zip_folder + '/EBAR_ECCC_2022-23_Species.mxd')
        shutil.copyfile(EBARUtils.resources_folder + '/UsageType.lyr', zip_folder + '/UsageType.lyr')
        shutil.copyfile(EBARUtils.resources_folder + '/EcoshapeOverview.lyr', zip_folder + '/EcoshapeOverview.lyr')
        shutil.copyfile(EBARUtils.resources_folder + '/Ecoshape.lyr', zip_folder + '/Ecoshape.lyr')

        # create spatial zip
        EBARUtils.displayMessage(messages, 'Creating ZIP: https://gis.natureserve.ca/download/' +
                                 'EBAR_ECCC_2023-24_Species_All_Data.zip')
        EBARUtils.createZip(zip_folder,
                            EBARUtils.download_folder + '/EBAR_ECCC_2023-24_Species_All_Data', None)
        # EBARUtils.displayMessage(messages, 'Creating ZIP: https://gis.natureserve.ca/download/' +
        #                          'EBAR_ECCC_2022-23_Species_All_Data.zip')
        # EBARUtils.createZip(zip_folder,
        #                     EBARUtils.download_folder + '/EBAR_ECCC_2022-23_Species_All_Data.zip', None)

        # create pdf zip
        EBARUtils.displayMessage(messages, 'Creating ZIP: https://gis.natureserve.ca/download/' +
                                 'EBAR_ECCC_2023-24_Species_All_PDFs.zip')
        EBARUtils.createZip(zip_folder,
                            EBARUtils.download_folder + '/EBAR_ECCC_2023-24_Species_All_PDFs.zip','.pdf')
        # EBARUtils.displayMessage(messages, 'Creating ZIP: https://gis.natureserve.ca/download/' +
        #                          'EBAR_ECCC_2022-23_Species_All_PDFs.zip')
        # EBARUtils.createZip(zip_folder,
        #                     EBARUtils.download_folder + '/EBAR_ECCC_2022-23_Species_All_PDFs.zip','.pdf')

    def runPackageECCCPrioritySpeciesTool(self, parameters, messages):
        # start time
        start_time = datetime.datetime.now()
        EBARUtils.displayMessage(messages, 'Start time: ' + str(start_time))

        # settings
        #arcpy.gp.overwriteOutput = True

        # make variables for parms
        #EBARUtils.displayMessage(messages, 'Processing parameters')

        # generate metadata
        EBARUtils.displayMessage(messages, 'Generating metadata')
        md = arcpy.metadata.Metadata()
        md.tags = 'Species Range, NatureServe Canada, Ecosystem-based Automated Range'
        md.description = 'See EBARxxxxx.pdf for per-species map and additional metadata, RangeMap.csv ' + \
            'for species attributes for each ELEMENT_GLOBAL_ID (xxxxx), and ' + \
            'EBARMethods.pdf for additional details. <a href="https://explorer.natureserve.org/">Go to ' + \
            'NatureServe Explorer</a> for information about the species.'
        md.credits = 'Copyright NatureServe Canada ' + str(datetime.datetime.now().year)
        md.accessConstraints = 'Publicly shareable under CC BY 4.0 (<a href=' + \
            '"https://creativecommons.org/licenses/by/4.0/">https://creativecommons.org/licenses/by/4.0/</a>)'

        # use EBAR BIOTICS table if can't get taxon API
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/4', 'biotics_view')

        # loop all RangeMap records for a custom set of IDs
        arcpy.MakeTableView_management(EBARUtils.ebar_feature_service + '/11', 'range_map_view',
                                       'RangeMapID IN (3828,616,618,620,624,627,630,639,640,621,617,670,689,713,1087,747,869,1093,1096,1102,1103,1105,1112,1115,1131,1133,1134,1138,1139,1144,1147,1149,1184,1187,1261,1296,1729,1747,1136,865,708,1875,1880,2238,2307,2309,2313,2241,2324,2334,2339,2342,2340,2344,2237,2356,2357,2358,2359,2361,2363,2364,2365,2366,2367,2368,2369,2370,2360,2362,2381,2382,2383,2384,2385,2386,2387,2388,2389,2390,2393,2377,2376,2391,2398,2412,2413,2414,2415,2416,2417,2418,2419,2420,2423,2424,2425,2428,2429,2430,2431,2432,2433,2435,2436,2438,2439,2443,2444,2445,2446,2447,2448,2450,2452,2453,2409,2426,2421,2427,2434,2437,2460,2462,2461,2463,2465,2474,2475,2476,2478,2479,2480,2470,2471,2477,2487,2489,2469,2491,2497,2498,2499,2501,2502,2506,2512,2517,2521,2522,2554,2556,2561,2576,2599,1822,1283,2440,2551,2650,2651,2660,2675,2758,2907,2913,2918,2924,2933,2935,2936,2939,2940,2941,2942,2943,2944,2945,2947,2948,2949,2950,2951,2952,2953,2955,2954,2956,2984,3026,3027,3036,3037,3047,3052,3053,3055,3058,3059,3072,3084,3085,3087,3089,3092,3093,3094,3097,3098,3110,3116,3122,3123,3125,3126,3128,3131,3132,3133,3134,3138,3142,3147,3150,3157,3151,3171,3174,3181,3182,3184,3191,3193,3208,3215,3216,3217,3219,3221,3223,3222,3224,3234,3235,3236,3237,3241,3243,3245,3238,3185,3252,3254,3256,3257,3260,3261,3263,3264,3265,3275,3249,1278,3270,3284,3296,3297,3298,3158,3311,3313,3314,3359,3444,3445,3446,3456,3458,3459,3462,3468,3501,3503,3505,3506,3470,3528,3493,3588,2798,3662,3683,3710,3718,3733,3755,3564,3770,3784,3768,3274,3781,3791,3793,3795,3796,3797,3798,3799,3800,3801,3802,3803,3804,3806,3813,3815,3814,3816,3817,3818,3819,3829,3788,3831,3833,3834,3835,3836,3837,3839,3840,3842,3844,3845,3848,3841,3851,3832,3854,3856,3858,3867,3874,3892,3821,3993,3994,3995,3869,4019,4020,4023,3838,4040,4041,3850,4045,4047,4076,3853,3852,4097,4099,4100,4112,3764,4203,4205,4206,4212,4043,3847,3830,4265,4274,4275,4251,4254,4276,4280,4283,4281,4284,2442,2546,2648,3289,2825,3136,3220,3585,2964,3635,3639,3649,2887,3657,3242,3124,3278,3577,3276,3180,3677,3684,3685,3302,3251,3262,3190,3692,3703,3478,3392,3720,2665,3665,1797,3726,2959,3729,3730,3732,3734,3450,2849,3387,3287,3675,3300,3448,2904,3571,3479,3554,3481,3555,3559,3482,3500,3531,3483,3484,3572,3711,3507,3485,3508,3509,3486,3496,3574,3487,3488,3563,3497,3489,3490,3604,3492,3498,3704,3567,3575,3540,3499,3568,3570,3759,3762,3231,3706,1825,3794,3811,3812,4285,2513,2635,1756,1101,1740,1795,2490,2500,2503,2511,2514,2518,2523,2524,2526,2527,2528,2530,2531,2533,2535,2537,2539,2540,2542,2548,2555,2565,2567,2571,2572,2575,2577,2578,2579,2580,2581,2582,2583,2584,2586,2587,2588,2589,2590,2591,2607,2608,2563,2573,2574,2585,2566,2616,2559,2560,2656,2986,2989,2991,3051,3054,3056,3057,3065,3066,3070,3172,3195,3213,3197,3244,3258,3268,3271,3272,3286,3288,3291,3293,3589,3593,3595,3283,3779,4074,4210,4211,4277,4278,4279,2629,3152,3159,3192,3225,3226,3233,3239,3188,3246,3253,3330,3281,3353,3357,3358,3365,2120,3373,3377,3378,3379,3380,2819,3404,2260,3003,3004,2492,3534,3535,3536,3538,3541,3542,3545,3548,3549,3553,3582,3584,3586,3587,1495,3590,3592,3597,3598,3599,3600,597,3607,3608,3610,3615,3617,1637,2172,2815,3594,3650,2544,2150,3601,3282,1659,1934,326,3390,753,1124,3394,3472,3316,3317,3318,3319,3321,3322,3325,3327,3328,3329,3333,3334,3335,3339,3345,3346,3347,2639,3348,3349,3350,2170,3693,3694,3381,3383,3384,3385,3388,3682,3696,3697,3698,3699,3700,3701,3702,3376,2493,3712,3713,3280,3551,2823,3399,3401,2994,3391,2770,3715,3372,2317,2318,3719,3369,3395,2119,3396,3397,3398,3722,3723,3725,1928,3422,479,3351,3728,3405,3375,2816,3408,3473,3364,3409,3474,2773,487,3413,3416,3418,2190,311,2730,3424,2735,3427,3428,2739,3533,2740,3411,601,3543,3414,3415,3547,3420,2274,3002,3550,2704,3552,2969,1376,3031,2720,3163,3431,2742,3433,3609,842,3011,2776,2748,3337,2355,3439,2269,3440,3436,3441,3034,3442,3437,3438,2694,3465,2976,3606,3430,3476,3494,3432,3434,2155,2248,3354,1250,3352,1658,3539,3344,3332,298,2777,350,2778,1120,2695,1123,3032,2708,2700,2709,2712,2763,3743,3009,3014,3015,3106,3120,3464,3117,3105,3006,2674,3518,3751,2971,2975,3266,3013,3104,3240,3016,2482,3756,3763,3808,3792,3083,3820,3859,3860,3754,3861,3862,3863,3864,3865,3866,3870,3871,3873,3875,3876,3877,3878,3879,3880,3881,3882,3883,3884,3885,3886,3887,3888,3889,3890,3894,3895,3896,3897,3898,3899,3900,3901,3902,3903,3904,3906,3905,3908,3909,3910,3911,3912,3913,3914,3915,3916,3917,3918,3919,3921,3920,3922,3923,3924,3926,3925,3927,3929,3928,3931,3930,3932,3933,3934,3935,3936,3938,3937,3939,3940,3941,3942,3943,3944,3945,3946,3947,3948,3907,3949,3950,3951,3952,3953,3955,3954,3956,3957,3959,3958,3960,3962,3961,3964,3963,3965,3966,3968,3967,3969,3970,3972,3971,3973,3974,3975,3976,3977,3978,3979,3980,3982,3981,3983,3985,3984,3987,3988,3989,3986,3990,3991,3996,3998,3999,4000,4001,3997,4002,4003,4004,4005,4006,4007,4008,4009,4010,4011,4012,4013,4014,4015,4016,4017,4018,2766,4021,4022,4024,4025,4026,4027,4028,4029,4030,4031,4032,4033,4034,4035,4036,4037,4038,4039,4042,4044,4046,4048,4049,4050,4051,4052,4053,4054,4056,4055,4057,4058,4059,4060,4062,4063,4064,4065,4067,4068,4069,4070,4061,4071,4072,4073,4075,4078,4077,4079,4080,4082,4083,4085,4086,4087,4088,4089,4090,4091,4092,4093,4094,4095,4098,4101,4102,4103,4104,4105,4107,4106,4109,4108,4111,4113,4114,4110,4115,3668,4117,4118,4116,4119,4120,4122,4121,4123,4124,4125,4126,4127,4128,4129,4130,4131,4132,4133,4135,4134,4136,4137,4138,4139,4140,4141,4142,4144,4143,4145,4146,4147,4149,4148,4150,4151,4152,4154,4153,4155,4156,4157,4159,4160,4162,4161,4163,4164,4165,4166,4167,4168,4169,4170,4172,4173,4174,4175,4176,4177,4178,4179,4180,4181,4183,4182,4184,4185,4186,4187,4188,4189,4190,4191,4193,4192,4194,4195,4197,4198,4199,4200,4202,4204,4207,4208,4213,4215,4216,4214,4217,4218,4219,4220,4221,4222,4223,4224,4225,4226,4227,4229,4230,4228,4232,4233,4234,4235,4236,4237,4238,4239,4240,4241,4242,4243,4244,4245,4246,4247,4248,4249,4250,4252,4253,4255,4256,4257,4258,4259,4260,4261,4262,4263,4264,4266,4267,4268,4269,4270,4271,4272,4273)')
                                       #'RangeMapID IN (85,311,616,617,618,620,621,624,627,630,637,670,689,708,713,722,747,752,778,865,869,1093,1101,1102,1103,1105,1112,1115,1120,1123,1124,1131,1133,1134,1136,1138,1139,1144,1145,1147,1149,1184,1187,1278,1283,1341,1497,1503,1504,1507,1592,1644,1658,1707,1729,1740,1747,1781,1795,1822,1825,1871,1875,1876,1879,1880,1928,1929,1934,1941,1963,2076,2114,2116,2119,2120,2121,2122,2125,2126,2127,2131,2155,2161,2162,2170,2172,2175,2180,2182,2190,2191,2201,2208,2220,2237,2238,2241,2243,2248,2260,2267,2269,2274,2275,2287,2290,2293,2307,2309,2313,2316,2317,2318,2324,2334,2339,2342,2344,2351,2355,2356,2357,2358,2359,2360,2361,2362,2363,2364,2365,2366,2367,2368,2369,2370,2375,2376,2377,2381,2382,2383,2384,2385,2386,2387,2388,2389,2390,2391,2393,2398,2405,2409,2412,2413,2414,2415,2416,2417,2418,2419,2420,2421,2423,2424,2425,2426,2427,2428,2429,2430,2431,2432,2433,2434,2435,2436,2437,2438,2439,2440,2442,2443,2444,2445,2446,2447,2448,2450,2452,2453,2460,2461,2462,2463,2464,2465,2469,2470,2471,2474,2475,2476,2477,2478,2479,2480,2482,2487,2489,2490,2491,2492,2493,2497,2498,2499,2500,2501,2502,2503,2506,2511,2512,2513,2514,2517,2518,2519,2521,2522,2523,2524,2526,2527,2528,2530,2531,2533,2535,2536,2537,2539,2540,2542,2544,2546,2548,2550,2551,2554,2555,2556,2559,2560,2561,2563,2565,2566,2567,2571,2572,2573,2574,2575,2576,2577,2578,2579,2580,2581,2582,2583,2584,2585,2586,2587,2588,2589,2590,2591,2596,2597,2598,2599,2607,2608,2616,2619,2621,2628,2629,2631,2632,2634,2635,2638,2639,2640,2642,2648,2650,2651,2656,2657,2658,2660,2663,2664,2665,2668,2674,2693,2694,2695,2700,2704,2707,2708,2709,2712,2714,2715,2716,2717,2718,2719,2720,2723,2728,2729,2730,2733,2735,2738,2739,2740,2742,2743,2745,2748,2751,2757,2758,2759,2760,2761,2763,2764,2765,2766,2768,2770,2772,2773,2774,2775,2776,2777,2778,2780,2787,2795,2798,2814,2825,2826,2830,2832,2843,2847,2849,2851,2855,2867,2886,2887,2889,2890,2899,2900,2902,2904,2907,2913,2918,2924,2929,2930,2932,2933,2935,2936,2939,2940,2941,2942,2943,2944,2945,2947,2948,2949,2950,2951,2952,2953,2954,2955,2956,2959,2969,2970,2971,2972,2974,2975,2976,2977,2979,2980,2984,2985,2986,2989,2991,2993,2994,2997,3002,3003,3004,3006,3009,3010,3011,3013,3014,3015,3016,3018,3023,3025,3026,3027,3031,3032,3033,3034,3036,3037,3038,3041,3042,3047,3050,3051,3052,3053,3054,3055,3056,3057,3058,3059,3065,3066,3070,3072,3080,3082,3083,3084,3087,3089,3092,3093,3094,3097,3098,3104,3105,3106,3110,3112,3116,3117,3120,3122,3123,3124,3125,3126,3128,3131,3132,3133,3134,3135,3136,3137,3138,3142,3147,3150,3151,3152,3157,3158,3159,3162,3171,3172,3174,3176,3180,3181,3182,3184,3185,3188,3189,3190,3191,3192,3193,3195,3196,3197,3208,3213,3215,3216,3217,3219,3220,3221,3222,3223,3224,3225,3226,3228,3231,3233,3234,3235,3236,3237,3238,3239,3240,3241,3242,3243,3244,3245,3246,3248,3249,3251,3252,3253,3254,3256,3257,3258,3259,3260,3261,3262,3263,3264,3265,3267,3268,3269,3270,3271,3272,3273,3274,3275,3276,3277,3278,3279,3280,3281,3282)')
        # join BIOTICS_ELEMENT_NATIONAL to RangeMap
        arcpy.AddJoin_management('range_map_view', 'SpeciesID', EBARUtils.ebar_feature_service + '/4', 'SpeciesID',
                                 'KEEP_COMMON')
        # join Species to RangeMap
        arcpy.AddJoin_management('range_map_view', 'SpeciesID', EBARUtils.ebar_feature_service + '/19', 'SpeciesID',
                                 'KEEP_COMMON')
        processed = 0
        # use Python sorted (sql_clause ORDER BY doesn't work), which precludes use of EBARUtils.SearchCursor
        #where_clause = "L19Species.ECCC_PrioritySpecies = 'Yes'"

        # make zip folder
        zip_folder = EBARUtils.temp_folder + '/EBAR_ECCC_2023-24_Species_All_Data'
        #zip_folder = EBARUtils.temp_folder + '/EBAR_ECCC_2022-23_Species_All_Data'
        EBARUtils.createReplaceFolder(zip_folder)

        # copy static resources
        shutil.copyfile(EBARUtils.resources_folder + '/ReadmeSet.txt', zip_folder + '/Readme.txt')
        shutil.copyfile(EBARUtils.resources_folder + '/EBARMethods.pdf', zip_folder + '/EBARMethods.pdf')
        shutil.copyfile(EBARUtils.resources_folder + '/Jurisdiction.csv', zip_folder + '/Jurisdiction.csv')

        range_map_ids = []
        attributes_dict = {}
        row = None
        for row in sorted(arcpy.da.SearchCursor('range_map_view',
                          ['L4BIOTICS_ELEMENT_NATIONAL.CATEGORY',
                           'L4BIOTICS_ELEMENT_NATIONAL.TAX_GROUP',
                           'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_SCIENTIFIC_NAME',
                           'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_ENGL_NAME',
                           'L4BIOTICS_ELEMENT_NATIONAL.NATIONAL_FR_NAME',
                           'L4BIOTICS_ELEMENT_NATIONAL.ELEMENT_GLOBAL_ID',
                           'L4BIOTICS_ELEMENT_NATIONAL.GLOBAL_UNIQUE_IDENTIFIER',
                           'L11RangeMap.RangeMapScope',
                           'L11RangeMap.RangeMapID',
                           'L11RangeMap.IncludeInDownloadTable',
                           'L4BIOTICS_ELEMENT_NATIONAL.SpeciesID',
                           'L11RangeMap.DifferentiateUsageType'])):
            processed += 1

            # copy pdf 
            EBARUtils.displayMessage(messages, 'Range Map ID: ' + str(row[8]))
            element_global_id = str(row[5])
            if row[7] == 'N':
                element_global_id += 'N'
            shutil.copyfile(EBARUtils.download_folder + '/EBAR' + element_global_id + '.pdf',
                            zip_folder + '/EBAR' + element_global_id + '.pdf')

            # set range map attributes
            range_map_ids.append(str(row[8]))
            arcpy.SelectLayerByAttribute_management('biotics_view', 'NEW_SELECTION', 'SpeciesID = ' + str(row[10]))
            attributes_dict[str(row[8])] = EBARUtils.getTaxonAttributes(row[6], element_global_id, row[8],
                                                                        messages)

            # update ArcGIS Pro template
            EBARUtils.displayMessage(messages, 'Updating ArcGIS Pro template')
            differentiate_usage_type = False
            if row[11]:
                differentiate_usage_type = True
            EBARUtils.updateArcGISProTemplate(zip_folder, element_global_id, md, row[8], differentiate_usage_type)

        if row:
            self.processPackage(messages, range_map_ids, attributes_dict, zip_folder, md)
            del row

        EBARUtils.displayMessage(messages, 'Processed ' + str(processed) + ' RangeMaps')
        return


# controlling process
if __name__ == '__main__':
    peps = PackageECCCPrioritySpeciesTool()
    parameters = []
    peps.runPackageECCCPrioritySpeciesTool(parameters, None)
