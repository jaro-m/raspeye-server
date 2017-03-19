import json, sys

cam_opt = {
'tl_now': 0,
'tl_delay': 1,
'tl_nop': 1,
'tl_starts': 0,
'tl_ends': 0,
'tl_camres': (640, 480),
'tl_exit': False,
'mo_det_exit': False,
'preview_exit': False,
'cam_res': (540, 405),
'cam_shtr_spd': 0,
'cam_iso': 0,
'cam_exp_mode': 'auto',
'cam_led': 0,
'exit': 'no',
'running': []}

fname = 'raspeye.json'

thefile = open(fname, 'w')
json.dump(cam_opt, thefile)
thefile.close()
print('Saved to', fname)
