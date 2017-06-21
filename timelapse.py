#!/usr/bin/env python3

import datetime, copy, shutil, os, picamera, json
class Timelapse():
    '''
    '''
    def __init__(self, raspeye_path, camera, cam_opt, md):
        self.raspeye_path = raspeye_path
        self.camera = camera
        self.cam_opt = cam_opt
        #self.cam_opt_copy = copy.copy(cam_opt) #I think I'll need it'
        self.onepic = md
        if self.onepic:
            self.the_path = raspeye_path
        else:
            if 'tl_active' in self.cam_opt['running']:
                self.cam_opt['tl_exit'] = True
                #return
            else:
                self.cam_opt['running']['tl_active'] = 1
                the_path = os.path.join(self.raspeye_path, 'timelapse')
                if not os.path.isdir(the_path):
                    os.makedirs(the_path, exist_ok=True)
                self.the_path = the_path
                self.filename = os.path.join(self.the_path, 'timelapse.txt')
                if not os.path.isfile(self.filename):
                    try:
                        fh = open(self.filename, 'w')
                    except OSError as err:
                        print("[TL] Error occurred during creation of 'timelapse.txt':\n", err)
                    else:
                        fh.close()
                self.time_res = datetime.timedelta(microseconds=10000)
                self.status = [[], []]
                self.filename = None
                self._calculate_times()
                jobs_added = True


    def _calculate_times(self):#
        '''Creating time table for taking pictures.
            It includes creation the paths for pictures (it might be useful later on,
             especially when jobs will be added to the same file)
        '''
        the_path = os.path.join(self.the_path, datetime.datetime.today())
        if not os.path.isdir(the_path):
            os.makedirs(the_path, exist_ok=True)
        if len(self.status) == 0:
            if self.cam_opt['tl_starts'] = 0:
                start_time = datetime.datetime.today()
            else:
                start_time = self.cam_opt['tl_starts']
            status_tmp = self.status
        else:
            status_tmp = [[], []] #It's 2 lists in a list (it could be just a list) to make it easier/shorter for now
            t_delta = datetime.timedelta(seconds=self.cam_opt['tl_delay'])
            cntr = 0
            while cntr < self.cam_opt['tl_nop']:
                status_tmp[0].append((start_time + datetime.timedelta(seconds=self.cam_opt['tl_delay']*cntr), the_path))
                cntr += 1
            
            #merging lists (new and old jobs)
            place = 0
            for time_ in self.status[0]:
                if len(status_tmp[0]) > 0:
                    if time_ > status_tmp[0]:
                        if status_tmp[0] - datetime.datetime.today() > self.time_res:
                            self.status[0].insert(place, (status_tmp[0], the_path))
                        del status_tmp[0]
                    place += 1
                else:
                    break
            if len(status_tmp[0]) > 0:
                for time_ in status_tmp: # .extend() can't be used as the paths need to be added
                    if status_tmp[0] - datetime.datetime.today() > self.time_res:
                        self.status[0].append((time_, the_path))
            del status_tmp

    def start_now(self):
        '''The method starts the actual time lapse process.
        '''
        #the code below is executed by motion detecting module (separate thread)
        if self.onepic: #if motion detection module needs a pic this will provide it
            '''checking for sufficient space on the disk'''
            disk_space = shutil.disk_usage(self.the_path)
            if disk_space[2]//1048576 < 200:# leave at least 200MB of free disk space
                #self.status[1].append('Free space on disk <= 200MB')
                return
            current_pic_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f.jpg")
            self.camera.capture(os.path.join(self.the_path, current_pic_name), use_video_port=True, splitter_port=3, quality=85)
            print('[TL] A picture has been taken! (MD)')
            return

        if self.cam_opt['tl_exit']: # for testing
            print('[TL] Finishing now')
            if 'tl_active' in self.cam_opt['running']:
                del self.cam_opt['running']['tl_active']
            self.cam_opt['tl_exit'] = 0
            return

        #the code below is executed for taking several pictures (time lapse mode)
        if len(self.status[0]) != len(self.status[1]):#I started preparing it for combine time lapse (when 2 or more jobs have been added)
            #picstotake = len(self.status[1])
            picstotake = self.cam_opt['tl_nop'] - len(self.status[1])
            startfrom = len(self.status[1])
            while jobs_added:
                jobs_added = False
                #for take in range(self.cam_opt['tl_nop'] - picstotake):
                for take in range(startfrom, picstotake):

                    if self.cam_opt['tl_exit'] or self.cam_opt['exit']:
                        print('[TL] Received <exit> signal!')
                        break

                    '''checking for sufficient space on the disk'''
                    disk_space = shutil.disk_usage(self.the_path)
                    if disk_space[2]//1048576 < 200:# leave at least 200MB of free disk space
                        #self.status[1].append('Free space on disk <= 200MB')
                        print('NOT ENOUGH SPACE ON DISK (<200MB)! SAVING PICTURES HAS STOPPED!')
                        break

                    current_pic_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f.jpg")
                    self.camera.capture(os.path.join(self.status[0][take][1], current_pic_name), use_video_port=True, splitter_port=0, quality=85)
                    self.status[1].append(current_pic_name)
                    print('[TL] A pictures have been taken! (',take+1,')')

                    '''calculating the time of the next picture, I explain it later'''
                    if take < self.cam_opt['tl_nop']-1:
                        next_pic = self.status[0][take+1][0]
                        np_delta = abs(datetime.datetime.today() - next_pic)
                        old_npdelta = np_delta
                        while abs(datetime.datetime.today() - next_pic) > self.time_res:
                            np_delta = abs(datetime.datetime.today() - next_pic)
                            if np_delta > old_npdelta:
                                break
                            old_npdelta = np_delta
                            if self.cam_opt['tl_exit'] or self.cam_opt['exit']:
                                break
                            if jobs_added:
                                self._calculate_times()
                                break

        '''After time lapse is finished I want the <status> to be written to disk.'''
        if not self.onepic:
            status = self.get_status()
            if status != None and self.filename != None:
                try:
                    filehnd = open(self.filename, 'a') #datetime.datetime.now().strftime("tl-status-%H.%M.%S.txt")), 'w')
                except OSError as err:
                    print("[TL] Can't Open the file! Error:", err)
                else:
                    #try:
                        #filehnd.write(status)
                    json.dump(status, filehnd)
                    #except (OSError, TypeError) as err:
                        #print(status)
                        #print("Error message for writing to a file:", err)
                    #finally:
                    filehnd.close()
            if 'tl_active' in self.cam_opt['running']:
                del self.cam_opt['running']['tl_active']
                self.cam_opt['tl_exit'] = 0
        return

    # def update_opts(self, cam_opt): #It might be needed for future features
    #     '''this method is for future features (probably it won't be needed)'''
    #     self.cam_opt_copy = copy.copy(cam_opt)
    #     return

    def get_status(self):
        tmp_list = []
        for item in range(len(self.status[0])):
            tmp_list.append((str(self.status[0][item][0].strftime("%H.%M.%S_%Y-%m-%d")), self.status[0][item][1]))
        str_status = str([tmp_list, self.status[1]])
        return str_status

    def is_running(self): #unused
        return self.running

    def add_jobs(self, the_path):
        pass #I'll sort it out really soon (I want just one instance of TL to be running)
        jobs_added = True
        self.the_path = the_path

def timelapse_start(path, camera, cam_opt, md=False): #It's used by threading, it will be redesigned in future
    timelapse_instance = Timelapse(path, camera, cam_opt, md)
    timelapse_instance.start_now()
    return

if __name__ == '__main__':
    print("It's a module for rapeye-srv.py")
