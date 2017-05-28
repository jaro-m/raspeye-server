#!/usr/bin/env python3

import datetime, copy, shutil, os
class Timelapse():
    '''
    '''
    def __init__(self, raspeye_path, camera, cam_opt, md):
        self.lock = True
        self.raspeye_path = raspeye_path
        self.camera = camera
        self.cam_opt = cam_opt
        self.cam_opt_copy = copy.copy(cam_opt)
        self.onepic = md
        if not self.onepic:
            the_path = os.path.join(self.raspeye_path, 'timelapse')
            if not os.path.isdir(the_path):
                os.makedirs(the_path, exist_ok=True)
            self.the_path = the_path
            self.cam_opt['running']['tl_active'] = self
        else:
            #the_path = os.path.join(self.raspeye_path, 'md-pictures')
            #if not os.path.isdir(the_path):
            #    os.makedirs(the_path, exist_ok=True)
            self.cam_opt['running']['tl_active'] = self
            self.the_path = raspeye_path

        #self.running = {}#False#nothing uses it at the moment
        self.time_res = datetime.timedelta(microseconds=10000)
        self.status = [[], []]
        self.filename = None
        if os.path.isfile('timelapse.txt'):
            self.filename = 'timelapse.txt'
        else:
            try:
                fh = open('timelapse.txt', 'w')
                fh.write('Time Lapse status file,\n')
            except OSError as err:
                print("Error occurred during creation 'timelapse.txt':\n", err)
                #self.filename = None
            else:
                fh.close()
        if not self.onepic:
            self.calculate_times()
            #self.lock = False
        print('tl initialized')


    def calculate_times(self):#
        '''creating time table for taking pictures'''
        cur_time = datetime.datetime.today()
        t_delta = datetime.timedelta(seconds=self.cam_opt_copy['tl_delay'])
        cntr = 0
        while cntr < self.cam_opt_copy['tl_nop']:
            self.status[0].append((cur_time + datetime.timedelta(seconds=self.cam_opt_copy['tl_delay']*cntr), self.the_path))
            cntr += 1

    def quickpic(self):
        '''checking for sufficient space on the disk'''
        disk_space = shutil.disk_usage(self.raspeye_path)
        if disk_space[2]//1048576 < 200:# leave at least 200MB of free disk space (should I leave more/less?)
            self.status[1].append('Free space on disk <= 200MB')
            self.cam_opt['tl_exit'] = True
        else:
            current_pic_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f.jpg")
            self.camera.capture(os.path.join(self.the_path, current_pic_name), use_video_port=True, splitter_port=0, quality=85)
            print('The picture has been taken')

    def start_now(self):
        '''The method starts the actual time lapse process.
        '''
        if self.onepic: #motion detection module needs a pic
            self.quickpic()
        self.lock = False

        # standard timelapse procedure below

        if len(self.status[0]) != len(self.status[1]):
            for take in range(self.cam_opt['tl_nop'] - len(self.status[1])):
                '''checking for sufficient space on the disk'''
                disk_space = shutil.disk_usage(self.the_path)
                if disk_space[2]//1048576 < 200:# leave at least 200MB of free disk space
                    self.status[1].append('Free space on disk <= 200MB')
                    self.cam_opt['tl_exit'] = True
                    break

                current_pic_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f.jpg")
                self.camera.capture(os.path.join(self.status[0][take][1], current_pic_name), use_video_port=True, splitter_port=0, quality=85)
                self.status[1].append(current_pic_name)
                print('A pictures have been taken! (',take+1,')')

                if self.cam_opt['tl_exit'] == True or self.cam_opt['exit'] == True:
                    print('Received <exit> signal! (TL)')
                    break

                '''calculating the time of the next picture'''
                if take < self.cam_opt['tl_nop']-1:
                    next_pic = self.status[0][take+1][0]
                    np_delta = abs(datetime.datetime.today() - next_pic)
                    old_npdelta = np_delta
                    while abs(datetime.datetime.today() - next_pic) > self.time_res:
                        np_delta = abs(datetime.datetime.today() - next_pic)
                        if np_delta > old_npdelta:
                            break
                        old_npdelta = np_delta
                        if self.onepic:
                            current_pic_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f.jpg")
                            self.camera.capture(os.path.join(self.the_path, current_pic_name), use_video_port=True, splitter_port=0, quality=85)
                        if self.cam_opt['tl_exit'] == True or self.cam_opt['exit'] == True:
                            print('Received <exit> signal! (TL)')
                            break

        '''After time lapse is finished I want the <status> to be written to disk.'''
        if not self.onepic:
            status = self.get_status()
            if status != None and self.filename != None:
                try:
                    filehnd = open(os.path.join(self.the_path, self.filename), 'a') #datetime.datetime.now().strftime("tl-status-%H.%M.%S.txt")), 'w')
                except OSError as err:
                    print("Can't Open a file! Error:", err)
                else:
                    try:
                        filehnd.write(status)
                    except (OSError, TypeError) as err:
                        print(status)
                        print("Error message for writing to a file:", err)
                    finally:
                        filehnd.close()
        #self.running = False#nothing uses it at the moment
        if 'tl_active' in self.cam_opt['running']:
            #ind = self.cam_opt['running'].index('tl_active')
            #self.cam_opt_orig['running'].pop(ind)
            del self.cam_opt['running']['tl_active']
        return

    def update_opts(self, cam_opt):
        '''this method is for future features (probably it won't be needed)'''
        self.cam_opt_copy = copy.copy(cam_opt)
        return

    def get_status(self):
        return str(self.status)
        if self.running == False:
            return
        # tmp_list = []
        # for item in range(len(self.status[0])):
        #     tmp_list.append((str(self.status[0][item][0].strftime("%H.%M.%S_%Y-%m-%d")), self.status[0][item][1]))
        # str_status = [tmp_list, self.status[1]]
        # return str_status

    def is_running(self):
        return self.running

    def add_jobs(self, tl_args):
        pass #I'll sort it out really soon (I want just one instance of TL to be running)

    def take1picture(self, the_path):
        self.onepic = True
        self.the_path = the_path

    def getlockstat(self):
        return self.lock

def timelapse_start(path, camera, cam_opt, md=False):
    print('md =', md)
    timelapse_instance = Timelapse(path, camera, cam_opt, md)
    timelapse_instance.start_now()
    return

if __name__ == '__main__':
    print("It's a module for rapeye-srv.py")
