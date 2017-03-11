#!/usr/bin/env python3

import io, sys, json, socket, struct, time, picamera, threading
#from timeit import default_timer as timer

try:
    my_port = int(sys.argv[1])
except:
    print("No port number provided")
    sys.exit()

#------------------------------------------
#setting up variables/constants/values/...

global camera, conn, preview_lock

#cam_mode = ('still', 'video')
cam_res_maxval = {2592: 1944, 1920: 1080}
cam_shtr_spd_maxval = 6000000
cam_iso_val = (0, 100, 200, 320, 400, 500, 640, 800)
cam_exp_mode_val = ('off', 'auto', 'night', 'nightpreview',
'backlight','spotlight', 'sports', 'snow', 'beach', 'verylong',
'fixedfps', 'antishake', 'fireworks')
exit_val = ('yes', 'no')
action_val = ('preview', 'mo_detect', 'timelapse')

donotexit = True
camera = picamera.PiCamera()
preview_lock = threading.Lock()

#------------------------------------------
#Functions definitions start here
def settingup_defaults():
    try:
        camopt = open('raspeye.json', 'r')
        cam_opt = json.load(camopt)
        camopt.close()
    except:
        #print('Setting up standard values')
        cam_opt = {
        'action': 'preview',
        'cam_res': (1296, 730),
        'cam_shtr_spd': 0,
        'cam_iso': 0,
        'cam_exp_mode': 'auto',
        'exit': 'no',
        'cam_led': 0}
    return cam_opt

def settingstofile(settings):
    filehnd = open(json_file, 'w')
    json.dump(settings, filehnd)
    filehnd.close()
    return

def checking_cmdstr(cmdstr):
    res = None
    if cmdstr == None or cmdstr == '':
        print('CMDSTR could not be received')
        return 'failed'
    else:
        cmdstr = str(cmdstr).split(',')
    for cmd in cmdstr:
        cmd = cmd.split(':')
        if len(cmd) > 1:
            cmd0 = cmd[0].strip()[1:-1]
            cmd1 = cmd[1].strip()
            if cmd1.startswith('"'):
                cmd1 = cmd1[1:-1]
        else:
            print('Wrong data', cmd)
            continue
        if cmd0 in cam_opt:
            if cmd0 == 'cam_res':
                if cmd1.startswith("'"):
                    cmd1 = cmd1[1:-1]
                    cmd1 = cmd1.split('x')
                try:
                    width = int(cmd1[0].strip())
                    height = int(cmd1[1].strip())
                    if width <= 1920:
                        if height <= 1080:
                            cam_opt[cmd0] = (width, height)
                    elif width <= 2592:
                        if height <= 1944:
                            cam_opt[cmd0] = (width, height)
                except:
                    pass
            elif cmd0 == 'cam_shtr_spd':
                try:
                    cmd1 = int(cmd1)
                    if cmd1 < cam_shtr_spd_maxval:
                        cam_opt[cmd0] = cmd1
                except:
                    pass
            elif cmd0 == 'cam_iso':
                try:
                    cmd1 = int(cmd1)
                except:
                    pass
                if cmd1 in cam_iso_val:
                    cam_opt[cmd0] = cmd1
            elif cmd0 == 'cam_exp_mode':
                if cmd1 in cam_exp_mode_val:
                    cam_opt[cmd0] = cmd1
            elif cmd0 == 'cam_led':
                if cmd1 == '1' or cmd1 == '0':
                    cam_opt[cmd0] = int(cmd1)
            elif cmd0 == 'exit':
                if cmd1 in exit_val:
                    cam_opt['exit'] = cmd1
            elif cmd0 == 'action':
                if cmd1 in action_val:
                    res = cmd1
            else:
                pass
    return res

def preview_mode(conn, camera):
    #global conn, camera, preview_lock
    conn.settimeout(None)
    preview_stream = io.BytesIO()
    camera.led = cam_opt['cam_led']
    connection = True
    while connection:
        camera.capture(preview_stream, 'jpeg', use_video_port=True, splitter_port=0, quality=85)
        flsize = preview_stream.tell()
        flen = struct.pack('<L', flsize)
        try:
            if conn.sendall(flen) != None:
                connection = False
                break
        except:
            connection = False
            break
        preview_stream.seek(0)
        try:
            if conn.sendall(preview_stream.read(flsize)) != None:
                connection = False
                break
        except:
            connection = False
            break
        preview_stream.seek(0)
        preview_stream.truncate()
    preview_stream.close()
    #conn.shutdown(socket.SHUT_WR)
    conn.close()
    preview_lock.release()
    print('preview connection closed')
    print('')
    return

def mo_detect():
    pass

def timelapse():
    pass

def update_opts(conn):
    pass
    return

#------------------------------------
#Starting sockets
my_ip = '0.0.0.0'
server_socket = socket.socket()
try:
    server_socket.bind((my_ip, my_port))
except:
    print('Address:', my_ip, 'already in use!')
    sys.exit()
server_socket.listen(0)
print('Server is now running')
#Sockets are running now

#------------------------------------
#Main loop
cam_opt = settingup_defaults()
while donotexit:
    print('Listening...')
    conn, clnaddr = server_socket.accept()
    print('')
    print('Accepted connection from:', clnaddr)
    try:
        actionNo = conn.recv(4)
        actionNo = struct.unpack('<L', actionNo)[0]
    except:
        conn.close()
        continue
    if actionNo == 10:
        print('Motion Detection Mode')
        mo_detect(conn, camera)
        continue

    elif actionNo == 20:
        print('Time Lapse Mode')
        timelapse(conn, camera)
        continue

    elif actionNo == 30:
        print('Preview Mode')
        if preview_lock.acquire(5) == True:
            #print('starting previewing thread')
            preview_thread = threading.Thread(target=preview_mode, args=(conn, camera))
            preview_thread.start()
        else:
            conn.close()

    elif actionNo == 40:
        print('Updating options')
        update_opts()

server_socket.close()
sys.exit()
