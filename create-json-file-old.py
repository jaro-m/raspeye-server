import json, sys

cam_opt = {
'action': 'preview',
'cam_res': '540x405',
'cam_shtr_spd': 0,
'cam_iso': 0,
'cam_exp_mode': 'auto',
'cam_led': 0,
'exit': 'no'}

fname = 'raspeye.json'

#print(cam_opt)
thefile = open(fname, 'w')
json.dump(cam_opt, thefile)
thefile.close()
print('Saved to', fname)
print('---------')
camopt = open(fname, 'r')
copt = json.load(camopt)
print(copt)
print(type(copt))
camopt.close()
sys.exit()
