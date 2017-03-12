import json, sys

cam_opt = {
'tl_now': 0,
'tl_delay': 1,
'tl_nop': 1,
'tl_starts': 0,
'tl_ends': 0,
'tl_camres': (640, 480),
'cam_res': (540, 405),
'cam_shtr_spd': 0,
'cam_iso': 0,
'cam_exp_mode': 'auto',
'cam_led': 0,
'exit': 'no',
'running': []}

fname = 'test.json'

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

# print('')
# cam_opt_s = str(cam_opt)#[1:-1]
# print('printing cam_opt_s:')
# # for elm in cam_opt_s:
# #     print(elm)
# print('-----------------------')
#
# cam_opt_ser = json.dumps(cam_opt)
# print('printing serialized object:')
# # for elm in cam_opt_ser:
# #     print(elm)
#
# cam_opt_deser = json.loads(cam_opt_ser)
# print('printing deserialized object:')
# for elm in cam_opt_deser.items():
#     print(elm)
#
# # cmdstr = cam_opt_s.encode(encoding='UTF-8')
