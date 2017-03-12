CAM_OPT_KEYS = {'tl_now', 'tl_apart', 'tl_nop', 'tl_start', 'tl_ends',
'tl_camres', 'cam_res', 'cam_shtr_spd', 'cam_iso', 'cam_exp_mode',
'cam_led', 'exit', 'running'}

TL_NOW_VAL = {0, 1, True, False}
CAM_RES_MAXVAL = {2592: 1944, 1920: 1080}
CAM_SHTR_SPD_MAXVAL = 6000000
CAM_ISO_VAL = (0, 100, 200, 320, 400, 500, 640, 800)
CAM_EXP_MODE_VAL = ('off', 'auto', 'night', 'nightpreview',
'backlight','spotlight', 'sports', 'snow', 'beach', 'verylong',
'fixedfps', 'antishake', 'fireworks')
CAM_LED_VAL = {0, 1, True, False}
EXIT_VAL = ('yes', 'no', 'quit', 'exit')
#ACTION_VAL = ('preview', 'mo_detect', 'timelapse')
