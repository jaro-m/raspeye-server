#!/usr/bin/env python3

import os
import sys
import json
import socket
import struct
import threading
import picamera
import picamera.array
import copy
import datetime
import logging

import constants
import preview
import timelapse
import motion_detection
#from timeit import default_timer as timer

try:
    my_port = int(sys.argv[1])
except IndexError:
    print("No port number provided!")
    sys.exit()

raspeye_path = os.path.dirname(os.path.abspath(sys.argv[0]))
#print('Starting from the path:', raspeye_path)

#configuring and starting logging
logger = logging.getLogger("RE-main")
logger.setLevel(logging.INFO)
log_fh = logging.FileHandler("raspeye.log")
log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_fh.setFormatter(log_formatter)
logger.addHandler(log_fh)
logger.info("---START---")

try:
    camera = picamera.PiCamera()
except picamera.exc.PiCameraMMALError as err:
    logger.exception("Creating PiCamera instance error!")
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
        logger.exception("socket.bind error")
        print('Address:', my_ip, end='')
        print(', Error message:', '"', end='')
        print(err, end='')
        print('"')
        sys.exit()
    server_socket.listen(3)
    logger.info("Server is running")
    print('Server is running now')
    return server_socket

def listening2soc(srvsoc):
    """Establishing connection/creating a socket

    Input: srvsoc - server socket object
    Output: conn - client socket object
            actionNo - a number as a command
    """
    logger.info('Listening...')
    conn, clnaddr = srvsoc.accept()
    logger.info(('Accepted connection from:', clnaddr[0]))
    conn.settimeout(3)#<None> for blocking socket
    try:
        actionNo = conn.recv(4)
    except socket.timeout as err:
        logger.exception('Connection timeout')
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

    def _validate_time(t):# needs improving/extending <---soon obsolete
        """Helper function for validating_cam_opt

        Input: t - string object
        Output: returns False if conversion to 'datetime' object gives error
                otherwise returns 'datetime' object
        """
        #try:
        date0, time0 = t.split(' ')
        if '/' in date0:
            day0, month0, year0 = date0.split('/')
        elif '-' in date0:
            day0, month0, year0 = date0.split('-')
        else:
            logger.error("time validation error")
            return False
        hour0, minute0 = time0.split(':')
        year0 = int(year0)
        month0 = int(month0)
        day0 = int(day0)
        hour0 = int(hour0)
        minute0 = int(minute0)
        thetime0 = (year0, month0, day0, hour0, minute0)
        thetime = datetime.datetime(thetime0[0], thetime0[1], thetime0[2], thetime0[3], thetime0[4])
        #except:
        #    print("srv/exception!")
        #    return False
        #else:
        logger.info("time validation OK")
        return thetime

    global cam_opt

    # print('---Before:') # for debugging
    # for itm in cam_opt_tmp:
    #     print(itm, cam_opt_tmp[itm])
    # print('---')
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
                tmpval = _validate_time(cam_opt_tmp[key_])
                if tmpval != 0:
                    cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'tl_exit':
            cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'md_exit':
            cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'pr_exit':
            cam_opt[key_] = cam_opt_tmp[key_]
        elif key_ == 'tl_camres':
            try:
                width = cam_opt_tmp[key_][0]
                height = cam_opt_tmp[key_][1]
                if isinstance(width, int) and isinstance(height, int):
                    if (width < 2592) and (height > 1944):
                        cam_opt[key_] = cam_opt_tmp[key_]
            except:
                logger.exception('wrong camera resolution info(TL)')
        elif key_ == 'pr_camres':
            try:
                width = cam_opt_tmp[key_][0]
                height = cam_opt_tmp[key_][1]
                if isinstance(width, int) and isinstance(height, int):
                    if (width < 2592) and (height > 1944):
                        cam_opt[key_] = cam_opt_tmp[key_]
            except:
                logger.exception('wrong camera resolution info(PR)')
        elif key_ == 'cam_res':
            try:
                width = cam_opt_tmp[key_][0]
                height = cam_opt_tmp[key_][1]
                if isinstance(width, int) and isinstance(height, int):
                    if (width < 2592) and (height > 1944):
                        cam_opt[key_] = cam_opt_tmp[key_]
            except:
                logger.exception('wrong camera resolution info')
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
    # print('---')
    logger.info("CAM_OPT validation OK")
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
            logger.exception("CAM_OPT not updated. Socket timeout")
            return
    logger.info('All data received. CAM_OPT updated')
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
            logger.error('CAM_OPT sending, connection error')
            conn.settimeout(None)
            return
        bytes_sent = conn.sendall(optstr)
    except socket.timeout as err:
        logger.exception("CAM_OPT sending, socket timeout")
    else:
        if bytes_sent != None:
            logger.error(('Sending CAM_OPT, bytes sent:', bytes_sent, 'out of', filesize))
            conn.settimeout(None)
            return
        logger.info('CAM_OPT sending: all OK')
    conn.settimeout(None)
    return


    #-----------------------------------------

    cam_opt = validating_cam_opt(cam_opt_tmp)
    camopts_changed = True# I don't use it ATM
    return


#The main loop starts here ------------

srvsoc = start_sockets()
cam_opt = settingup_defaults()

donotexit = True# only for the while loop below
while donotexit:

    conn, actionNo = listening2soc(srvsoc)
    if actionNo == 0:
        logger.info("Exit signal received")
        donotexit = False
        cam_opt['md_exit'] = 1
        cam_opt['pr_exit'] = 1
        cam_opt['tl_exit'] = 1
        cam_opt['exit'] = 1
        #continue

    elif actionNo == 10:
        logger.info("Received 10 MD")
        if 'md_active' in cam_opt['running']:
            cam_opt['md_exit'] = True
        modet_mod = motion_detection.SimpleMotionDetection(args=(camera, conn, cam_opt, raspeye_path))
        logger.info("SRV starting MD")
        modet_mod.start()
        #continue

    elif actionNo == 20:
        logger.info("Received 20 TL")
        if 'tl_active' in cam_opt['running']:
            cam_opt['tl_req'] = 1
        else:
            timelapse_thread = timelapse.Timelapse(args=(raspeye_path, camera, cam_opt))
            logger.info("SRV starting TL")
            timelapse_thread.start()
        #continue

    elif actionNo == 30:
        logger.info("Received 30 PR")
        preview_thread = threading.Thread(name="PR-thread", target=preview.preview_mode, args=(conn, camera, cam_opt))
        logger.info("SRV starting PR")
        preview_thread.start()

    elif actionNo == 40:
        logger.info("Received 40 rcv cam_opt")
        receive_opts()

    elif actionNo == 50:
        logger.info("Received 50 snd cam_opt")
        send_opts()

    if cam_opt['exit']:
        donotexit = False

logger.info('SRV preparing for exit...')
while len(cam_opt['running']):
    cam_opt['tl_exit'] = 1
    cam_opt['md_exit'] = 1
    cam_opt['pr_exit'] = 1

srvsoc.close()
logger.info("Socket closed")
sys.exit()
