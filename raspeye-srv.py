#!/usr/bin/env python3

import sys, json, socket, struct, picamera, threading, picamera.array, os, copy # time
import constants, preview, timelapse, motion_detection
#from timeit import default_timer as timer

try:
    my_port = int(sys.argv[1])
except IndexError:
    print("No port number provided!")
    sys.exit()

raspeye_path = os.path.dirname(os.path.abspath(sys.argv[0]))
#print('Starting from the path:', raspeye_path)


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
        print(', Error message:', '"', end='')
        print(err, end='')
        print('"')
        sys.exit()
    server_socket.listen(3)
    print('Server is running now')
    return server_socket

def listening2soc(srvsoc):
    """Establishing connection/creating a socket

    Input: srvsoc - server socket object
    Output: conn - client socket object
            actionNo - a number as a command
    """
    #print('')
    #print('Listening...')
    conn, clnaddr = srvsoc.accept()
    #print('')
    #print('Accepted connection from:', clnaddr[0])
    conn.settimeout(3)#<None> for blocking socket
    try:
        actionNo = conn.recv(4)
    except socket.timeout as err:
        print('Error:', err)
        return
    else:
        actionNo = struct.unpack('<L', actionNo)[0]
    return conn, actionNo

def settingup_defaults():
    """Setting up the cam_opt (a dictionary with settings)

    Input: None
    Output: cam_opt - dictionary with all the settings/options/states)
    """
    return constants.CAM_OPT_DEFAULTS #cam_opt

def validating_cam_opt(cam_opt_tmp):
    """The function to validate cam_opt variable (dictionary) <--due to change very soon

    Input: cam_opt_tmp - a dictionary to be checked
    Output: returns the same object if all was OK otherwise leaves out all 'bad' bits
    """

    def validate_time(t):# needs improving/extending <---soon obsolete
        """Helper function for validating_cam_opt

        Input: t - string object
        Output: returns False if conversion to 'datetime' object gives error
                otherwise returns 'datetime' object
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

    # print('---Before:') # for debugging
    # for itm in cam_opt_tmp:
    #     print(itm, cam_opt_tmp[itm])
    if 'running' in cam_opt_tmp: # client can't change it directly!
        del cam_opt_tmp['running'] #it's used directly only on server-side

    '''deleting unrecognized keys'''
    for _key in cam_opt_tmp.keys():
        if _key not in constants.CAM_OPT_KEYS:
            del cam_opt_tmp[_key]

    for key_ in cam_opt_tmp:

        if key_ == 'tl_now':
            if cam_opt_tmp[key_] in constants.TL_NOW_VAL:
                cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'tl_delay':
            if isinstance(cam_opt_tmp[key_], int):
                cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'tl_nop':
            if isinstance(cam_opt_tmp[key_], int):
                cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'tl_starts':
            if cam_opt_tmp[key_] != 0:
                if not validate_time(cam_opt_tmp[key_]):
                    cam_opt[key_] = 0
        elif key_ == 'tl_ends':
            if cam_opt_tmp[key_] != 0:
                if not validate_time(cam_opt_tmp[key_]):
                    cam_opt[key_] = 0
        elif key_ == 'tl_exit':
            #if cam_opt_tmp[key_] in constants.EXIT_VAL:
            cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'md_exit':
            #if cam_opt_tmp[key_] in constants.EXIT_VAL:
            cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'pr_exit':
            #if cam_opt_tmp[key_] in constants.EXIT_VAL:
            cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'tl_camres':
            try:
                width = cam_opt_tmp[key_][0]
                height = cam_opt_tmp[key_][1]
                if isinstance(width, int) and isinstance(height, int):
                    if (width < 2592) and (height > 1944):
                        cam_opt[key_] = cam_opt_tmp[key_]
            except:
                print('Given wrong camera resolution (TL)')
        elif key_ == 'pr_camres':
            try:
                width = cam_opt_tmp[key_][0]
                height = cam_opt_tmp[key_][1]
                if isinstance(width, int) and isinstance(height, int):
                    if (width < 2592) and (height > 1944):
                        cam_opt[key_] = cam_opt_tmp[key_]
            except:
                print('Given wrong camera resolution (PR)')
        elif key_ == 'cam_res':
            try:
                width = cam_opt_tmp[key_][0]
                height = cam_opt_tmp[key_][1]
                if isinstance(width, int) and isinstance(height, int):
                    if (width < 2592) and (height > 1944):
                        cam_opt[key_] = cam_opt_tmp[key_]
            except:
                print('Given wrong camera resolution')
        elif key_ == 'cam_shtr_spd':
            if isinstance(cam_opt_tmp[key_], int):
                if cam_opt_tmp[key_] > constants.CAM_SHTR_SPD_MAXVAL:
                    cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'cam_iso':
            if cam_opt_tmp[key_] in constants.CAM_ISO_VAL:
                cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'cam_exp_mode':
            if cam_opt_tmp[key_] in constants.CAM_EXP_MODE_VAL:
                cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'cam_led':
            if cam_opt_tmp[key_] in constants.CAM_LED_VAL:
                cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'exit':
            if cam_opt_tmp[key_] in constants.EXIT_VAL:
                cam_opt[key_] = cam_opt_tmp[key_]
    # print('---After:') # for debugging
    # for itm in cam_opt:
    #     print(itm, cam_opt[itm])
    return

def receive_opts():
    """Downloads new commands/options and set them up in cam_opt var

    Input: conn - socket object to make a connection
    Output: None (the function make changes to cam_opt 'on the fly')
    """
    global conn
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
    #print('All data received. Data updated')
    cam_opt_s = str(data_temp)[2:-1]
    cam_opt_tmp = json.loads(cam_opt_s)
    validating_cam_opt(cam_opt_tmp)

def send_opts():
    '''Sends program options/state to the client
    '''
    global conn, cam_opt
    conn.settimeout(3)#None
    cam_opt_s = json.dumps(cam_opt)
    optstr = cam_opt_s.encode(encoding='UTF-8')
    flsize = len(optstr)
    flen = struct.pack('<L', flsize)
    try:
        if conn.sendall(flen) != None:
            print('Connection error')
            conn.settimeout(None)
            return
        bytes_sent = conn.sendall(optstr)
    except socket.timeout as err:
        print('Error while sending data to the client:', err)
    else:
        if bytes_sent != None:
            print('Sending CAM_OPT failure, bytes sent:', bytes_sent, 'out of', filesize)
            conn.settimeout(None)
            return
        #print('All data has been sent.')
    conn.settimeout(None)
    return


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
        cam_opt['md_exit'] = 1
        cam_opt['pr_exit'] = 1
        cam_opt['tl_exit'] = 1
        cam_opt['exit'] = 1
        continue

    elif actionNo == 10:
        # print('')
        # print('<Motion Detection> is starting')# motion detection will be started with the server
        # print('')
        if 'md_active' in cam_opt['running']:
            cam_opt['md_exit'] = True
        modet_mod = threading.Thread(target=motion_detection.mo_detect, args=(camera, conn, cam_opt, raspeye_path))
        modet_mod.start()
        continue

    elif actionNo == 20:
        # print('')
        # print('<Time Lapse> is starting')# time lapse need more work, but it should work
        # print('')
        #for _key in cam_opt:
        #    print(_key,':', cam_opt[_key])
        if 'tl_active' in cam_opt['running']:
            cam_opt['tl_exit'] = True
        else:
            timelapse_thread = threading.Thread(target=timelapse.timelapse_start, args=(raspeye_path, camera, cam_opt))
            timelapse_thread.start()
        continue

    elif actionNo == 30:
        # print('')
        # print('<Preview> is starting')#preview works fine
        # print('')
        preview_thread = threading.Thread(target=preview.preview_mode, args=(conn, camera, cam_opt))
        preview_thread.start()

    elif actionNo == 40:
        # print('')
        # print('Updating options')
        # print('')
        receive_opts()

    elif actionNo == 50:
        # print('')
        # print('Sending Raspeye status to the client')
        # print('')
        send_opts()

    if cam_opt['exit']:
        donotexit = False

print('preparing for exit...')
while len(cam_opt['running']) > 0:
    cam_opt['tl_exit'] = True
    cam_opt['md_exit'] = True
    cam_opt['pr_exit'] = True

srvsoc.close()
sys.exit()
