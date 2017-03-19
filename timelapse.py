#!/usr/bin/env python3

#Needs a lot modifications and even more testing

def timelapse_mode(camera, cam_opt):
    import os, sys, datetime, time, shutil
    #from picamera import PiCamera

    global tl_finished#, cam_opt#, camera
    tl_finished = False
    folder = '/home/pi/Downloads/timelapse/'

    # try:
    #     camopt = open(fname, 'r')
    #     cam_opt = json.load(camopt)
    #     camopt.close()
    # except:
    #     cam_opt = {
    #     'tl_now': 0,
    #     'tl_delay': 1,
    #     'tl_nop': 1,
    #     'tl_starts': None,
    #     'tl_ends': None,
    #     'tl_camres': None,
    #     'tl_exit': 0,
    #     'cam_res': (540, 405),
    #     'cam_shtr_spd': 0,
    #     'cam_iso': 0,
    #     'cam_exp_mode': 'auto',
    #     'cam_led': 0,
    #     'exit': 'no',
    #     'running': []}
    number_of_taken_pictures = 0

    # camera = PiCamera()
    # camera.resolution = (1024, 768)
    # camera.led = False
    # camera.shutter_speed = 0
    # camera.iso = 0
    # camera.exposure_mode = 'auto'

    def check_dates(cam_opt):
        #global cam_opt
        if cam_opt['tl_starts'] > cam_opt['tl_ends']:
            tempval = cam_opt['tl_start']
            cam_opt['tl_starts'] = cam_opt['tl_ends']
            cam_opt['tl_ends'] = tempval
            return

    def prepare_thetime(thetime):
        if not isinstance(thetime, int):
            # try:
            date0, time0 = thetime.split(' ')
            if '/' in date0:
                year0, month0, day0 = date0.split('/')
            elif '-' in date0:
                year0, month0, day0 = date0.split('-')
            else:
                return None
            hour0, minute0 = time0.split(':')
            # except:
            #     return None
            year0 = int(year0)
            month0 = int(month0)
            day0 = int(day0)
            hour0 = int(hour0)
            minute0 = int(minute0)
            thetime0 = (year0, month0, day0, hour0, minute0)
            # thetime1 = (int(x) for x in thetime0)
            # print('thetime0:', thetime0)
            return thetime0
        else:
            return None

    def calculate_times():
        curtime = datetime.datetime.today()
        thestart = prepare_thetime(cam_opt['tl_starts'])
        theend = prepare_thetime(cam_opt['tl_ends'])
        print('thestart:', thestart, 'theend:', theend)
        if thestart == None:
            starttime = curtime
            #tostart = 0
        else:
            starttime = datetime.datetime(thestart[0], thestart[1], thestart[2], thestart[3], thestart[4])
            # starttime = datetime.datetime(thestart)
            if (starttime - curtime).total_seconds() < 0:
                starttime = curtime
        if theend == None:
            delay = int(cam_opt['tl_delay'])
            timedelta_now = datetime.timedelta(seconds = (cam_opt['tl_nop'] * delay))
            endtime = curtime + timedelta_now
        else:
            endtime = datetime.datetime(theend[0], theend[1], theend[2], theend[3], theend[4])
            # endtime = datetime.datetime(theend[0], theend[1], theend[2], theend[3], theend[4])
            if (endtime - curtime).total_seconds() < 0:
                cam_opt['tl_nop'] = 0
                return (0,0)
            timespan = round((endtime - starttime).total_seconds())
            delay = timespan//cam_opt['tl_nop']
        print('times1:', curtime - starttime, curtime - endtime)
        print('times2:', starttime - curtime, endtime - curtime)
        tostart = starttime - curtime
        tostart = round(tostart.total_seconds())
        if cam_opt['tl_now'] == 0:
            if tostart > 0:
                right_time = round(tostart.total_seconds())
            else:
                right_time = 0
        else:
            right_time = 0
        toend = round((endtime - curtime).total_seconds())
        print('toend:', toend, toend//cam_opt['tl_nop'])
        print('right_time:', right_time, 'delay:', delay)
        return (right_time, delay)

    def check_rtime(thetime):
        #global right_time
        curtime = datetime.datetime.today()
        thestart = prepare_thetime(thetime)
        starttime = datetime.datetime(thestart[0], thestart[1], thestart[2], thestart[3], thestart[4])
        # starttime = datetime.datetime(thestart)
        tostart = starttime - curtime
        if tostart < 0:
            return 0
        return round(tostart.total_seconds())

    def get_values1():
        return cam_opt['tl_now'], cam_opt['tl_delay'], cam_opt['tl_nop']

    def get_values2():
        return cam_opt['tl_starts'], cam_opt['tl_ends']

    check_dates(cam_opt)
    #if calculate_times() != None:
    try:
        right_time, delay = calculate_times()
    except:
        print('Wrong input! Time lapse will not start')
        return
    #else:
    #    tl_finished = True
    #    return

    while right_time > 0:
        print(right_time, 'before start')
        time.sleep(0.5)
        right_time = check_rtime(cam_opt['tl_starts'])

    counter = 0
    for take in range(cam_opt['tl_nop']):
        disk_space = shutil.disk_usage(folder)
        if disk_space[2]//1048576 < 200:# leave at least 200MB of free disk space
            cam_opt['tl_exit'] = True
            break
        if delay >= cam_opt['cam_shtr_spd']:
            camera.capture(folder + datetime.datetime.now().strftime("%H.%M.%S_%Y-%m-%d.jpg"), use_video_port=True, splitter_port=0, quality=85)
            print(counter, 'Picture has been taken!')
            counter += 1
            if cam_opt['tl_exit'] == True or cam_opt['exit'] == True or cam_opt['exit'] == 'yes':
                break
            print('time lapse in progress...')
            time.sleep(delay - cam_opt['cam_shtr_spd'])
        else:
            camera.capture(folder + datetime.datetime.now().strftime("%H.%M.%S_%Y-%m-%d.jpg"), use_video_port=True, splitter_port=0, quality=85)
            print('delay < cam_shtr_spd')
            pass
    print('Time lapse has finished!')
    tl_finished = True
    return


    #calculate_times()
if __name__ == '__main__':
    print("It's a module for Rapeye")
    # from picamera import PiCamera # It was for testing
    # camera = PiCamera()           #
    # timelapse_mode(camera)        #
