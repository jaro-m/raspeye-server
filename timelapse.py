#!/usr/bin/env python3

import datetime
import shutil
import os
import json
#import picamera

class Timelapse():
    '''Time lapse class used to controll taking pictures for 'time lapse' effect.
        It only takes pictures at given time/frequency/number...
        To have a proper 'time lapse' effect it the pictures have to be convert
        into a video (it's not yet implemented)
    '''

    def __init__(self, raspeye_path, camera, cam_opt):
        """At least 3 arguments are needed, the 4th is used by motion detecting module.
            input:
                - raspeye_path = the path to the program's path
                - camera = picamera.PiCamera() instance
                - cam_opt = a dictionary which controls the main program
                    and its modules behaviour, it's also used for communication
                    with Raspeye client.
        """
        self.raspeye_path = raspeye_path
        self.camera = camera
        self.cam_opt = cam_opt
        if self.cam_opt['disk_full']:
            self.cam_opt['tl_exit'] = 1
        self.cam_opt['running']['tl_active'] = 1
        self.time_res = datetime.timedelta(microseconds=10000)
        self.tasks = []
        self.the_path = self._set_thepath()

    def _set_thepath(self):
        """set up the path for time lapse directory and timelapse.txt file.
        """
        the_path = os.path.join(self.raspeye_path, 'timelapse')
        #if not os.path.isdir(the_path):
        #    os.makedirs(the_path, exist_ok=True)
        return the_path

    def _save_file(self, f2w, thename): # not used at the moment (it'll be redesigned)
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

    def _validate_time(self, t):
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
            print("exception occured")
            return 0
        else:
            if datetime.datetime.today() < thetime - self.time_res:
                return thetime
            else:
                return 0

    def check_disk_space(self):
        """Checks whether there is at least 200MB free space on the disk"""

        disk_space = shutil.disk_usage(self.the_path)
        if disk_space[2]//1048576 < 200:
            print('NOT ENOUGH SPACE ON DISK (<200MB)! SAVING PICTURES HAS STOPPED!')
            self.cam_opt['disk_full'] = 1
            self.cam_opt['tl_exit'] = 1
            return
    
    def _take_picture(self, tl_path):
        """take picture and save it"""

        current_pic_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f.jpg")
        self.camera.capture(os.path.join(tl_path, current_pic_name),
                                use_video_port=True,
                                splitter_port=0,
                                quality=85)

        print('[TL] A picture has been taken!')
        return

    def get_time_list(self):
        """Creates a list of datetime objects form values in self.cam_opt.
            ('tl_nop', 'tl_delay', 'tl_starts' and eventually 'tl_now')
            The created list is the first element of another list, the second element
            in the list is the path, where the pictures will be saved.
        """

        # setting up the path
        if self.cam_opt['tl_path'] != '':
            the_path = os.path.join(self.raspeye_path, 'timelapse', self.cam_opt['tl_path'])
        else:
            the_path = os.path.join(self.raspeye_path, 'timelapse', str(datetime.datetime.today()))

        # creating the ditrectory if one doesn't exist
        if not os.path.isdir(the_path):
            os.makedirs(the_path, exist_ok=True)

        # finding the time of the first picture in the sequence (start_time)
        if self.cam_opt['tl_starts'] == 0:
            if self.cam_opt['tl_now'] == True:
                start_time = datetime.datetime.today()
            else:
                return
        else:
            start_time = self._validate_time(self.cam_opt['tl_starts'])
            if not start_time:
                print("invalid 'tl_starts' time")
                return

        # creating the list
        temp_list = []
        t_delta = datetime.timedelta(seconds=self.cam_opt['tl_delay'])
        cntr = 0
        while cntr < self.cam_opt['tl_nop']:
            temp_list.append(start_time + t_delta * cntr)
            cntr += 1

        # adding the path
        temp_list = [temp_list, the_path]

        # appending to the self.tasks
        self.tasks.append(temp_list)
        return

    def get_theearliest(self):
        if self.tasks == []:
            return 0, 0
        path = ''
        pic_time = None
        for task in self.tasks:
            if task[0]:
                if pic_time is None or task[0][0] < pic_time:
                    pic_time = task[0][0]
                    path = task[1]
        if pic_time is None:
            return 0, 0
        return pic_time, path

    def get_next_ones(self):
        thelist = []
        first_pic, its_path = self.get_theearliest()
        if first_pic == 0:
            return 0
        thelist.append((first_pic, its_path))
        #del self.tasks[task_no][0][0]
        for task in self.tasks:
            if not task[0]:
                continue
            for t in thelist:
                if task[0][0] == t[0]:
                    break
            else:
                if task[0][0] - first_pic < self.time_res:
                    thelist.append((task[0][0], task[1]))
        return thelist

    # def _get_next_ones(self):
    #     thelist = []
    #     first_pic, task_no = self.get_theearliest()
    #     if first_pic == 0:
    #         return 0
    #     thelist.append((first_pic, task_no))
    #     del self.tasks[task_no][0][0]
    #     while True:
    #         next_one, next_task = self.get_theearliest()
    #         if not next_one:
    #             break
    #         if next_one - first_pic < self.time_res:
    #             thelist.append((next_one, next_task))
    #             del self.tasks[next_task][0][0]
    #         else:
    #             break
    #     return thelist

    def get_thelast(self):
        if self.tasks == []:
            return 0, 0
        index = 0
        counter = 0
        pic_time = None
        for task in self.tasks:
            if task[0]:
                if pic_time is None or task[0][-1] > pic_time:
                    pic_time = task[0][-1]
                    index = counter
            counter += 1
        if pic_time is None:
            return 0, 0
        return pic_time, index

    # def put_back(self, lst):
    #     lst.reverse()
    #     for item in lst:
    #         self.tasks[item[1]][0].insert(0, item[0])

    def start_now(self):
        '''The main method, starts the actual time lapse process.
        '''
        self.get_time_list()
        formatR = self.get_thelast()[0]
        #print(formatR)
        print("Time lapse should be finished at {!s}".format(formatR))

        # entering the main loop
        while True:
            #self.jobs_added = False

            the_queue = self.get_next_ones()
            if not the_queue:
                break
            #num_of_pic_to_take = len(the_queue)

            while the_queue[0][0] - datetime.datetime.today() > self.time_res:
                if self.cam_opt['tl_exit'] or self.cam_opt['exit']:
                    break
                if self.cam_opt['tl_req']:
                    break

            if self.cam_opt['tl_exit'] or self.cam_opt['exit']:
                # print('[TL] Received <exit> signal!')
                break
            elif self.cam_opt['tl_req']:
                self.cam_opt['tl_req'] = 0
                #self.put_back(the_queue)
                self.get_time_list()
                formatR = self.get_thelast()[0]
                print("Time lapse should be finished at {!s}".format(formatR))
                continue
            else:
                for pic in the_queue:
                    # taking the picture
                    self._take_picture(pic[1])

                    # and deleting the entry in the tasks list
                    ind = 0
                    for task in self.tasks:
                        if task[1] == pic[1]:
                            del self.tasks[ind][0][0]
                            break
                        ind += 1
            
            # checking whether there's enough free space left on the disk
            self.check_disk_space()

            # checking for empty list
            for e in self.tasks:
                if e[0]:
                    break
            else: # if all pictures have been taken then finish
                break # getting out of the main while loop

        if 'tl_active' in self.cam_opt['running']:
            del self.cam_opt['running']['tl_active']
            self.cam_opt['tl_exit'] = 0

        print("Time lapse's done")
        return

    @property
    def get_tasks(self):
        result = []
        for task in self.tasks:
            tmp_lst = []
            for tm in task[0]:
                prn = tm.strftime("%Y/%m/%d %H.%M.%S,%f")
                #print(prn)
                tmp_lst.append(prn)
            result.append((tmp_lst, task[1]))
        return result

def timelapse_start(path, camera, cam_opt, md=False): #It's used by threading, it will be redesigned in future
    """Starting threading.
    """
    timelapse_instance = Timelapse(path, camera, cam_opt)
    timelapse_instance.start_now()
    return

if __name__ == '__main__':
    print("It's a module for rapeye-srv.py")
