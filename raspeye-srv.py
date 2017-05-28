#!/usr/bin/env python3

import sys, json, socket, struct, picamera, threading, picamera.array, os# time
import constants, preview, timelapse, motion_detection
#from timeit import default_timer as timer

try:
    my_port = int(sys.argv[1])
except IndexError:
    print("No port number provided!")
    sys.exit()

raspeye_path = os.path.dirname(os.path.abspath(sys.argv[0]))
print('Starting from the path:', raspeye_path)


try:
    camera = picamera.PiCamera()
except picamera.exc.PiCameraMMALError as err:
    print("Camera is in use!:", err)
    sys.exit()

def start_sockets():
    """Initialization
    """
    my_ip = '0.0.0.0'
    server_socket = socket.socket()
    try:
        server_socket.bind((my_ip, my_port))
    except OSError as err:
        print('Address:', my_ip, end='')
        print(', Error string:', '"', end='')
        print(err, end='')
        print('"')
        sys.exit()
    server_socket.listen(3)
    print('Server is now running')
    return server_socket

def listening2soc(srvsoc):
    """Establishing connection/creating a socket

    Input: srvsoc - server socket object
    Output: conn - client socket object
            actionNo - a number as a command
    """
    print('')
    print('Listening...')
    conn, clnaddr = srvsoc.accept()
    print('')
    print('Accepted connection from:', clnaddr[0])
    conn.settimeout(3)#<None> for blocking socket
    actionNo = conn.recv(4)
    actionNo = struct.unpack('<L', actionNo)[0]
    return conn, actionNo

def settingup_defaults():
    """Setting up the cam_opt (dictionary with settings)

    Input: None
    Output: cam_opt - dictionary with all the settings/options/states)
    """
    global raspeye_path
    filepath = (os.path.join(raspeye_path, 'raspeye.json'))
    if os.path.isfile(filepath):
        filehnd = open(filepath, 'r')
        cam_opt = json.load(filehnd)
        filehnd.close()
    else:
        cam_opt = constants.CAM_OPT_DEFAULTS
        filehnd = open(os.path.join(raspeye_path, 'raspeye.json'), 'w')
        json.dump(cam_opt, filehnd)
        filehnd.close()

    return cam_opt

#def settingstofile(settings):
#    filehnd = open('raspeye.json', 'w')
#    json.dump(settings, filehnd)
#    filehnd.close()
#    return

def validating_cam_opt(cam_opt_tmp):
    """The function to validate cam_opt variable (dictionary)

    Input: cam_opt_tmp - a dictionary to be checked
    Output: returns the same object if all was OK otherwise leaves out all 'bad' bits
    """

    def validate_time(t):# needs improving/extending <---soon obsolete
        """Helper function for validating_cam_opt

        Input: t - string object
        Output: returns False if conversion to 'datetime' object gives error
                otherwise returns 'datetime' object (True)
        """
        try:
            date0, time0 = t.split(' ')
            if '/' in date0:
                 year0, month0, day0 = date0.split('/')
            elif '-' in date0:
                year0, month0, day0 = date0.split('-')
            else:
                return None
            hour0, minute0 = time0.split(':')
            year0 = int(year0)
            month0 = int(month0)
            day0 = int(day0)
            hour0 = int(hour0)
            minute0 = int(minute0)
            thetime0 = (year0, month0, day0, hour0, minute0)
            thetime = datetime.datetime(thetime0[0], thetime0[1], thetime0[2], thetime0[3], thetime0[4])
        except:
            return False
        else:
            return thetime

    global cam_opt
    keys2del = []
    for _key in cam_opt_tmp.keys():
        if _key not in constants.CAM_OPT_KEYS:
            #del cam_opt_tmp[_key]
            keys2del.append(_key)
    for itm in keys2del:
        del cam_opt_tmp[itm]
    for key_ in constants.CAM_OPT_KEYS:
        if key_ not in cam_opt_tmp:
            cam_opt_tmp[key_] = cam_opt[key_]
        else:
            if key_ == 'tl_now':
                if cam_opt_tmp[key_] not in constants.TL_NOW_VAL:
                    cam_opt_tmp[key_] = cam_opt[key_]
            elif key_ == 'tl_delay':
                if not isinstance(cam_opt_tmp[key_], int):
                    cam_opt_tmp[key_] = cam_opt[key_]
            elif key_ == 'tl_nop':
                if not isinstance(cam_opt_tmp[key_], int):
                    cam_opt_tmp[key_] = cam_opt[key_]
            elif key_ == 'tl_starts':
                if cam_opt_tmp[key_] != 0:
                    if not validate_time(cam_opt_tmp[key_]):
                        cam_opt_tmp[key_] = 0
            elif key_ == 'tl_ends':
                if cam_opt_tmp[key_] != 0:
                    if not validate_time(cam_opt_tmp[key_]):
                        cam_opt_tmp[key_] = 0
            elif key_ == 'tl_camres':
                try:
                    width = cam_opt_tmp[key_][0]
                    height = cam_opt_tmp[key_][1]
                    if not isinstance(width, int):
                        cam_opt_tmp[key_] = cam_opt[key_]
                    if not isinstance(height, int):
                        cam_opt_tmp[key_] = cam_opt[key_]
                    if width > 2592:
                        cam_opt_tmp[key_] = cam_opt[key_]
                    elif height > 1944:
                        cam_opt_tmp[key_] = cam_opt[key_]
                except:
                    cam_opt_tmp[key_] = cam_opt[key_]
            elif key_ == 'preview_camres':
                try:
                    width = cam_opt_tmp[key_][0]
                    height = cam_opt_tmp[key_][1]
                    if not isinstance(width, int):
                        cam_opt_tmp[key_] = cam_opt[key_]
                    if not isinstance(height, int):
                        cam_opt_tmp[key_] = cam_opt[key_]
                    if width > 2592:
                        cam_opt_tmp[key_] = cam_opt[key_]
                    elif height > 1944:
                        cam_opt_tmp[key_] = cam_opt[key_]
                except:
                    cam_opt_tmp[key_] = cam_opt[key_]
            elif key_ == 'cam_res':
                try:
                    width = cam_opt_tmp[key_][0]
                    height = cam_opt_tmp[key_][1]
                    if not isinstance(width, int):
                        cam_opt_tmp[key_] = cam_opt[key_]
                    if not isinstance(height, int):
                        cam_opt_tmp[key_] = cam_opt[key_]
                    if width > 2592:
                        cam_opt_tmp[key_] = cam_opt[key_]
                    elif height > 1944:
                        cam_opt_tmp[key_] = cam_opt[key_]
                except:
                    cam_opt_tmp[key_] = cam_opt[key_]
            elif key_ == 'cam_shtr_spd':
                if isinstance(cam_opt_tmp[key_], int):
                    if cam_opt_tmp[key_] > constants.CAM_SHTR_SPD_MAXVAL:
                        #cam_opt_tmp[key_] = constants.CAM_SHTR_SPD_MAXVAL
                        cam_opt_tmp[key_] = cam_opt[key_]
                else:
                    #cam_opt_tmp[key_] = 0
                    cam_opt_tmp[key_] = cam_opt[key_]
            elif key_ == 'cam_iso':
                if cam_opt_tmp[key_] not in constants.CAM_ISO_VAL:
                    #cam_opt_tmp[key_] = 0
                    cam_opt_tmp[key_] = cam_opt[key_]
            elif key_ == 'cam_exp_mode':
                if cam_opt_tmp[key_] not in constants.CAM_EXP_MODE_VAL:
                    #cam_opt_tmp[key_] = 'auto'
                    cam_opt_tmp[key_] = cam_opt[key_]
            elif key_ == 'cam_led':
                if cam_opt_tmp[key_] not in constants.CAM_LED_VAL:
                    #cam_opt_tmp[key_] = 0
                    cam_opt_tmp[key_] = cam_opt[key_]
            elif key_ == 'exit':
                if cam_opt_tmp[key_] not in constants.EXIT_VAL:
                    cam_opt_tmp[key_] = cam_opt[key_]
    return cam_opt_tmp

def update_opts(conn):
    """Downloads new commands/options and set them up in cam_opt var

    Input: conn - socket object to make a connection
    Output: None (the function make changes to cam_opt 'on the fly')
    """
    global cam_opt, camopts_changed
    length = conn.recv(4)
    length = struct.unpack('<L', length)[0]
    data_temp = b''
    data_toread = length
    chunk = 4096
    while data_toread != 0:
        try:
            if data_toread >= chunk:
                datain = conn.recv(chunk)
                data_toread -= len(datain)
            else:
                datain = conn.recv(data_toread)
                data_toread -= len(datain)
            data_temp += datain
        except socket.timeout as err:
            print("CAM_OPT hasn't been updated. Socket error:", err)
            return
    print('All data received')
    cam_opt_s = str(data_temp)[2:-1]
    cam_opt_tmp = json.loads(cam_opt_s)
    #the code below is only for debugging and will be deleted soon
    print('')
    print('Printing received data:')
    for itm in cam_opt_tmp.items():
        print(itm)
    #-----------------------------------------

    cam_opt = validating_cam_opt(cam_opt_tmp)
    camopts_changed = True# I don't use it ATM
    return


#The end of functions' definitions-----
#The main loop starts here ------------

srvsoc = start_sockets()
cam_opt = settingup_defaults()

donotexit = True# only for the while loop below
while donotexit:

    conn, actionNo = listening2soc(srvsoc)
    if actionNo == 0:
        donotexit = False
        cam_opt['mo_det_exit'] = 1
        cam_opt['preview_exit'] = 1
        cam_opt['tl_exit'] = 1
        cam_opt['exit'] = 1
        continue

    elif actionNo == 10:
        if 'md_active' in cam_opt['running']:
            print('Motion Detection is already running!')
            continue

        print('')
        print('<Motion Detection> Mode is starting')# motion detection will be started with the server
        print('')
        if 'md_active' in cam_opt['running']:
            self.cam_opt['md_exit'] = True
        else:
            modet_mod = threading.Thread(target=motion_detection.mo_detect, args=(camera, conn, cam_opt, raspeye_path))
            modet_mod.start()
        continue

    elif actionNo == 20:
        print('')
        print('<Time Lapse> Mode is starting')# time lapse need more work, but it should work
        print('')
        if 'tl_active' in cam_opt['running']:
            tl_instance = cam_opt['running']['tl_active']
            while tl_instance.getlockstat():
                pass
            tl_instance.add_jobs(self.thepath)
        else:
            timelapse_thread = threading.Thread(target=timelapse.timelapse_start, args=(raspeye_path, camera, cam_opt))
            timelapse_thread.start()
        continue

    elif actionNo == 30:
        print('')
        print('<Preview> Mode is starting')#preview works fine
        print('')
        preview_thread = threading.Thread(target=preview.preview_mode, args=(conn, camera, cam_opt))
        preview_thread.start()

    elif actionNo == 40:
        print('')
        print('Updating options')
        print('')
        update_opts(conn)

    if cam_opt['exit'] == 'yes' or cam_opt['exit'] == True:
        donotexit = False

print('preparing for exit...')
srvsoc.close()
sys.exit()
