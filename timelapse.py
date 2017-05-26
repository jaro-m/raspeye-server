#!/usr/bin/env python3

import datetime, copy, shutil, os
class Timelapse():
    '''
    '''
    def __init__(self, the_path, camera, cam_opt):
        #import copy, datetime
        self.the_path = the_path
        self.camera = camera
        self.cam_opt_orig = cam_opt
        self.cam_opt = copy.copy(cam_opt)
        self.running = False#nothing uses it at the moment
        self.time_res = datetime.timedelta(microseconds=10000)
        self.status = [[], []]
        if os.path.isfile('timelapse.txt'):
            self.filename = 'timelapse.txt'
        else:
            try:
                fh = open('timelapse.txt', 'w')
                fh.write('Time Lapse status file,\n')
            except OSError as err:
                print('Error occurred', err)
                self.filename = None
            else:
                fh.close()
        self.calculate_times()

    def calculate_times(self):
        '''creating time table for taking pictures'''
        cur_time = datetime.datetime.today()
        t_delta = datetime.timedelta(seconds=self.cam_opt['tl_delay'])
        #time_table = [cur_time]
        cntr = 0
        while cntr < self.cam_opt['tl_nop']:
            self.status[0].append((cur_time + datetime.timedelta(seconds=self.cam_opt['tl_delay']*cntr), self.the_path))
            cntr += 1
        #print('tl status is:', self.status)

    def start_now(self):
        '''The method starts the time lapse process.
        '''
        #import datetime, time, shutil, os#,  sys
        #print('  --md->tl->', self.the_path)#, motiond)
        self.running = True
        if 'tl_active' not in self.cam_opt_orig['running']:
            #self.cam_opt_orig['running'] = self.cam_opt_orig['running'].append('tl_active')
            self.cam_opt_orig['running'].append('tl_active')

        '''main loop'''
        for take in range(self.cam_opt['tl_nop']):

            '''checking for sufficient space on the disk'''
            disk_space = shutil.disk_usage(self.the_path)
            if disk_space[2]//1048576 < 200:# leave at least 200MB of free disk space
                self.cam_opt['tl_exit'] = True
                break

            current_pic_name = datetime.datetime.now().strftime("%H.%M.%S_%Y-%m-%d.jpg")
            self.camera.capture(os.path.join(self.the_path, current_pic_name), use_video_port=True, splitter_port=0, quality=85)
            self.status[1].append(current_pic_name)
            print(take+1, 'pictures have been taken!')
            if self.cam_opt['tl_exit'] == True or self.cam_opt['exit'] == True:
                break
            #print('time lapse in progress...')

            '''calculating the time of the next picture'''
            if take < self.cam_opt['tl_nop']-1:
                next_pic = self.status[0][take+1]
                np_delta = abs(datetime.datetime.today() - next_pic)
                old_npdelta = np_delta
                while abs(datetime.datetime.today() - next_pic) > self.time_res:
                    np_delta = abs(datetime.datetime.today() - next_pic)
                    if np_delta > old_npdelta:
                        break
                    old_npdelta = np_delta
                    if self.cam_opt['tl_exit'] == True or self.cam_opt['exit'] == True:
                        break
                    #time.sleep(delay - cam_opt['cam_shtr_spd'])
        #print('Time lapse has finished!')

        '''After time lapse is finished I want the <status> to be written to disk.'''
        status = self.get_status()
        if status != None and self.filename != None:
            try:
                filehnd = open(os.path.join(self.the_path, self.filename), 'a') #datetime.datetime.now().strftime("tl-status-%H.%M.%S.txt")), 'w')
                #filehnd = open(self.the_path, 'w')
            except OSError as err:
                print("Can't Open a file! Error:", err)
            else:
                try:
                    #st = str(status[0]) + str(status[1])
                    filehnd.write(status)
                except (OSError, TypeError) as err:
                    print(status)
                    print("Error string for writing file:", err)
                finally:
                    filehnd.close()
        self.running = False#nothing uses it at the moment
        if 'tl_active' in self.cam_opt_orig['running']:
            #self.cam_opt_orig['running'] = self.cam_opt_orig['running'].pop('tl_active')
            ind = self.cam_opt_orig['running'].index('tl_active')
            self.cam_opt_orig['running'].pop(ind)
        return

    def update_opts(self, cam_opt):
        '''this method is for future features'''
        self.cam_opt = copy.copy(cam_opt)
        return

    def get_status(self):
        if self.running == False:
            return
        #str_status = ()
        tmp_list = []
        for item in range(len(self.status[0])):
            tmp_list.append((str(self.status[0][item][0].strftime("%H.%M.%S_%Y-%m-%d")), self.status[0][item][1]))
        str_status = [tmp_list, self.status[1]]
        return str_status

    def is_running(self):
        return self.running

    def add_jobs(self, tl_args):
        pass

def timelapse_start(path, camera, cam_opt):
    #import threading
    timelapse_instance = Timelapse(path, camera, cam_opt)
    timelapse_instance.start_now()
    #del(timelapse_instance)
    return
    #calculate_times()
if __name__ == '__main__':
    print("It's a module for rapeye-srv.py")
