#!/usr/bin/env python3

import datetime
import shutil
import os
import json
#import picamera

class Timelapse():
    '''It controls taking pictures for 'time lapse' effect.
        It only takes pictures at given time/frequency/number...
        To have a proper 'time lapse' effect the pictures have to be converted
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
        """set up the path for time lapse directory.
        """
        the_path = os.path.join(self.raspeye_path, 'timelapse')
        #if not os.path.isdir(the_path):
        #    os.makedirs(the_path, exist_ok=True)
        return the_path

    def _save_file(self, f2w, thename): # not used at the moment (it'll be redesigned)
        """
        """
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
        """Tries to use datetime method from datetime module.
            If success, then returns the object, 0 otherwise.
        """
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
        """Takes picture and save it"""

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
            The created list and the path, where the pictures will be saved
            are put in a dictionary with keys: 'sequence' and 'path'
            At the end the dictionary is added to self.tasks list
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

        # creating tasks dictionary and adding the data
        #  temp_list as 'sequence' and the path as 'path'
        ## temp_list = [temp_list, the_path] - old way (changed)
        temp_tasks = {}
        temp_tasks['sequence'] = temp_list
        temp_tasks['path'] = the_path

        # appending to the self.tasks
        self.tasks.append(temp_tasks)
        return

    def get_theearliest(self):
        """Finds the time of the first picture in the lists
            Returns a tuple, the time object and the path where the picture should be saved.
        """
        if self.tasks == []:
            return 0, 0
        path = ''
        pic_time = None
        for task in self.tasks:
            if task['sequence']:
                if pic_time is None or task['sequence'][0] < pic_time:
                    pic_time = task['sequence'][0]
                    path = task['path']
        if pic_time is None:
            return 0, 0
        return pic_time, path

    def get_next_ones(self):
        """Looks for the times with the difference of the value self.time_res.
            Returns the list of tuples (time, path).
        """
        thelist = []
        first_pic, its_path = self.get_theearliest()
        if first_pic == 0:
            return 0
        tmp_dict = {}
        tmp_dict['time'] = first_pic
        tmp_dict['path'] = its_path
        thelist.append(tmp_dict)
        for task in self.tasks:
            if not task['sequence']:
                #if the 'sequence' is empty the task can be deleted
                continue
            for job in thelist:
                if task['sequence'][0] == job['time']:
                    break
            else:
                if task['sequence'][0] - first_pic < self.time_res:
                    thelist.append({'time': task['sequence'][0], 'path': task[path]})
        return thelist

    def get_thelast(self):
        """Finds the time of the last picture of all running time lapse sequences.
            Returns a tuple (time object, path)
        """
        if self.tasks == []:
            return 0, 0
        pic_time = None
        pic_path = None
        for task in self.tasks:
            if task['sequence']:
                if pic_time is None or task['sequence'][-1] > pic_time:
                    pic_time = task['sequence'][-1]
                    pic_path = task['path']
        if pic_time is None:
            return 0, 0
        return {'time': pic_time, 'path': pic_path}

    def start_now(self):
        '''The main method, starts the actual time lapse process.
        '''
        self.get_time_list()
        last_pic = self.get_thelast()
        print("Time lapse should be finished at {!s} and saved to {}".format(last_pic['time'], last_pic['path']))

        # entering the main loop
        while True:
            #self.jobs_added = False

            the_queue = self.get_next_ones()
            if not the_queue:
                break
            #num_of_pic_to_take = len(the_queue)

            while the_queue[0]['time'] - datetime.datetime.today() > self.time_res:
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
                last_pic = self.get_thelast()
                print("Time lapse should be finished at {!s} and saved to {}".format(last_pic['time'], last_pic['path']))
                continue
            else:
                for pic in the_queue:
                    # taking the picture
                    self._take_picture(pic['path'])

                    # and deleting the entry in the tasks list
                    ind = 0 # for loop doesn't provide the index, I should have used iter
                    for task in self.tasks:
                        if task['path'] == pic['path']: # finding the list with the path = pic[1]
                            del self.tasks[ind]['sequence'][0]
                            break
                        ind += 1
            
            # checking whether there's enough free space left on the disk
            self.check_disk_space()

            # checking for empty list
            for e in self.tasks:
                if e['sequence']:
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
    """Creates a TimeLapse instance and starts it.
    """
    timelapse_instance = Timelapse(path, camera, cam_opt)
    timelapse_instance.start_now()
    return

if __name__ == '__main__':
    print("It's a module for rapeye-srv.py")
