#!/usr/bin/env python3

import datetime, copy, shutil, os, picamera, json
class Timelapse():
    '''
    '''
    def __init__(self, raspeye_path, camera, cam_opt, md):
        self.raspeye_path = raspeye_path
        self.camera = camera
        self.cam_opt = cam_opt
        if self.cam_opt['disk_full']:
            self.cam_opt['tl_exit'] = 1
        #self.cam_opt_copy = copy.copy(cam_opt) #I think I'll need it'
        self.onepic = md
        if self.onepic:
            self.the_path = raspeye_path
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
                    print("[TL] Error occurred during creation of 'timelapse.txt' file:\n", err)
                else:
                    fh.close()
            self.time_res = datetime.timedelta(microseconds=10000)
            self.status = []
            self.filename = None
            self._calculate_times()
            self.jobs_added = True

    def _save_file(self, f2w, thename):
        if f2w != None:
            if not os.path.isdir(os.path.dirname(thename)): #self.filename != None:
                os.makedirs(os.path.dirname(thename), exist_ok=True)
            try:
                filehnd = open(thename, 'a') #datetime.datetime.now().strftime("tl-status-%H.%M.%S.txt")), 'w')
            except OSError as err:
                print("[TL] Can't Open the file! Error:", err)
                return
            else:
                #try:
                    #filehnd.write(status)
                json.dump(f2w, filehnd)
                #except (OSError, TypeError) as err:
                    #print(status)
                    #print("Error message for writing to a file:", err)
                #finally:
                filehnd.close()
        return

    def _calculate_times(self):
        '''Creating time table for taking pictures.
            It includes creation the paths for pictures (it might be useful later on,
             especially when jobs will be added to the same file)
        '''

        def _validate_time(t):
            try:
                date0, time0 = t.split(' ')
                if '/' in date0:
                    day0, month0, year0 = date0.split('/')
                elif '-' in date0:
                    day0, month0, year0 = date0.split('-')
                else:
                    return 0
                hour0, minute0 = time0.split(':')
                year0 = int(year0)
                month0 = int(month0)
                day0 = int(day0)
                hour0 = int(hour0)
                minute0 = int(minute0)
                thetime0 = (year0, month0, day0, hour0, minute0)
                thetime = datetime.datetime(thetime0[0], thetime0[1], thetime0[2], thetime0[3], thetime0[4])
            except:
                return 0
            else:
                if thetime > datetime.datetime.today():
                    return thetime
                else:
                    return 0

        print('calculating times')
        if self.cam_opt['tl_path'] != '':
            the_path = os.path.join(self.raspeye_pth, 'timelapse', self.cam_opt['tl_path'])
        else:
            the_path = os.path.join(self.the_path, str(datetime.datetime.today()))
        if not os.path.isdir(the_path):
            os.makedirs(the_path, exist_ok=True)

        if len(self.status) == 0:
            if self.cam_opt['tl_starts'] == 0:
                if self.cam_opt['tl_now'] == 0:
                    self.cam_opt['tl_exit'] = 1
                    return
                start_time = datetime.datetime.today()
            else:
                start_time = _validate_time(self.cam_opt['tl_starts'])
                if start_time == 0:
                    print("invalid 'tl_starts' time")
                    return
            print("tl_starts:", start_time)
            #status_tmp = self.status[0]
        else:
            if self.cam_opt['tl_starts'] == 0:
                start_time = datetime.datetime.today() + self.time_res
            else:
                start_time = _validate_time(self.cam_opt['tl_starts'])
                if start_time == 0:
                    return

        status_tmp = []
        t_delta = datetime.timedelta(seconds=self.cam_opt['tl_delay'])
        cntr = 0
        while cntr < self.cam_opt['tl_nop']:
            status_tmp.append((start_time + t_delta * cntr, the_path))
            cntr += 1

        if len(self.status) != 0:

            print("printing 'status_tmp':")
            for el in status_tmp:
                print(el)

            print('')
            print("printing 'self.status':")
            for el in self.status:
                print(el[0])
            print('')



            #merging lists (new and old jobs)
            tmp_list = []
            for time_ in self.status:
                cntr = 0
                for time_tmp in status_tmp:
                    #print("checking", time_[0], "and", time_tmp[0])

                    if time_[0] > time_tmp[0]:
                        cntr += 1
                        #if status_tmp[0][0] - datetime.datetime.today() > self.time_res:
                        tmp_list.append(time_tmp) #, the_path))
                    else:
                        status_tmp = status_tmp[cntr:]
                        break
                tmp_list.append(time_)

            self.status = copy.copy(tmp_list)
        else:
            self.status = copy.copy(status_tmp)

        if status_tmp != []:
            for time_tmp in status_tmp:
                self.status.append(time_tmp)

        print(len(self.status))
        for el in self.status:
            print(el[0])
        return

    def start_now(self):
        '''The method starts the actual time lapse process.
        '''
        def _take_picture(tl_path):


            #checking for sufficient space on the disk
            disk_space = shutil.disk_usage(self.the_path)
            if disk_space[2]//1048576 < 200:# leave at least 200MB of free disk space
                #self.status[1].append('Free space on disk <= 200MB')
                print('NOT ENOUGH SPACE ON DISK (<200MB)! SAVING PICTURES HAS STOPPED!')
                self.cam_opt['disk_full'] = 1
                self.cam_opt['tl_exit'] = 1
                return

            #taking a picture
            current_pic_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f.jpg")
            self.camera.capture(os.path.join(tl_path, current_pic_name),
                                use_video_port=True,
                                splitter_port=0,
                                quality=85)
            print('[TL] A picture has been taken!')
            return

        #the code below is executed by motion detecting module (separate thread)
        if self.onepic: #if motion detection module needs a pic this will provide it

            #checking for sufficient space on the disk
            disk_space = shutil.disk_usage(self.the_path)
            if disk_space[2]//1048576 < 200: # leave at least 200MB of free disk space
                self.cam_opt['disk_full'] = 1
                self.cam_opt['tl_exit'] = 1
                return
            current_pic_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f.jpg")
            self.camera.capture(os.path.join(self.the_path,
                                            current_pic_name),
                                            use_video_port=True,
                                            splitter_port=3,
                                            quality=85)
            print('[TL] A picture has been taken! (MD)')
            return



        # for key, val in self.cam_opt.items(): # testing
        #     print(key, val)

        if self.cam_opt['tl_exit']: # for testing
            print('[TL] Finishing now')
            if 'tl_active' in self.cam_opt['running']:
                del self.cam_opt['running']['tl_active']
            self.cam_opt['tl_exit'] = 0
            return

        #the code below is executed for taking several pictures (time lapse mode)
        while self.jobs_added:
            self.jobs_added = False
            print('in a while loop')
            #for take in range(self.cam_opt['tl_nop'] - picstotake):
            num_of_pic_to_take = len (self.status)
            for take in range(0, num_of_pic_to_take):
                print('in a for loop')
                if self.cam_opt['tl_exit'] or self.cam_opt['exit']:
                    print('[TL] Received <exit> signal!')
                    break

                if self.cam_opt['tl_now']:
                    _take_picture(self.status[take][1])
                    continue

                #calculating the time of the next picture, it'll be explained later
                if take < self.cam_opt['tl_nop']-1:
                    next_pic = self.status[take+1][0]
                else:
                    next_pic = self.status[-1][0]
                np_delta = abs(datetime.datetime.today() - next_pic)
                old_npdelta = np_delta
                print('entering second while loop')
                while abs(datetime.datetime.today() - next_pic) > self.time_res:
                    #print("to next picture:", np_delta)
                    np_delta = abs(datetime.datetime.today() - next_pic)
                    if np_delta > old_npdelta:
                        break
                    old_npdelta = np_delta
                    if self.cam_opt['tl_exit'] or self.cam_opt['exit']:
                        break
                    if self.cam_opt['tl_req']:
                        self.job_added = 1
                        self.cam_opt['tl_req'] = 0
                        self._calculate_times()
                        break
                print('...taking a pic...')
                _take_picture(self.status[take][1])


        '''After time lapse is finished I want the <status> to be written to disk.'''
        if not self.onepic:
            status = self.get_status()
            #self._save_file(status)

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
        for item in range(len(self.status)):
            tmp_list.append((str(self.status[item][0].strftime("%H.%M.%S_%Y-%m-%d")), self.status[item][1]))
        #str_status = str([tmp_list, self.status[1]])
        return tmp_list

    def is_running(self): #unused
        return self.running
    
    #def add_jobs(self, the_path): #BAD IDEA!
    #    pass #I'll sort it out really soon (I want just one instance of TL to be running)
    #    self.jobs_added = True
    #    self.the_path = the_path

def timelapse_start(path, camera, cam_opt, md=False): #It's used by threading, it will be redesigned in future
    timelapse_instance = Timelapse(path, camera, cam_opt, md)
    timelapse_instance.start_now()
    return

if __name__ == '__main__':
    print("It's a module for rapeye-srv.py")
