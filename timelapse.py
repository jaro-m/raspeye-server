#!/usr/bin/env python3

import datetime, copy, shutil, os, picamera, json
class Timelapse():
    '''Time lapse class used to controll taking pictures for 'time lapse' effect.
        It only takes pictures at given time/frequency/number...
        To have a proper 'time lapse' effect it the pictures have to be convert
        into a video (it's not yet implemented)
    '''
    def __init__(self, raspeye_path, camera, cam_opt, md):
        """At least 3 arguments are needed, the 4th is used by motion detecting module.
            input:
                - raspeye_path = the path to the program's path
                - camera = picamera.PiCamera() instance
                - cam_opt = a dictionary which controls the main program
                    and its modules behaviour, it's also used for communication
                    with Raspeye client.
                - md = boolean, True when other modules use this class to take a picture
        """
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
            self.status = [] # a list of tuples (datetime-object, a_path_as_a_string)
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
        '''Creating times table for taking pictures.
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

        def _merge_times_lists(list1, list2):
            """Merging lists of tuples. Each tuple contain:
                    (datetime-object, path_to_a_directory), as
                    (datetime-object, string)
                input:
                    2 lists of the same type (but may be of different length)
                output:
                    returns a new list
                    sorted according to the time in datetime-object in those lists
            """

            #merging lists (new and old jobs)
            tmp_lst = []
            for item1 in list1:
                cntr = 0
                if list2 != []:
                    for item2 in list2:
                        if item1[0] > item2[0]:
                            cntr += 1
                            tmp_lst.append(item2)
                        elif item1[0] == item2[0]:
                            cntr += 1
                            tmp_lst.append(item1)
                            tmp_lst.append(item2)
                            break
                        else:
                            tmp_lst.append(item1)
                            break
                    else:
                        tmp_lst.append(item1)
                    list2 = list2[cntr:]
                else:
                    tmp_lst.append(item1)

            #if the list2 is not empty then append it to list1
            if list2 != []:
                print("list2 is not empty yet")
                tmp_lst.extend(list2)

            print("Printing the merged list...") # just for testing
            print(len(tmp_lst))
            for el in tmp_lst:
                print(el)
            return tmp_lst

        def _create_times_list():
            """Creates a list of tuples (datetime-object, a_path_to_a_directory)
                    It uses self.cam_opt values:
                    'tl_now', 'tl_nop', 'tl_starts', 'tl_delay' and 'tl_path'
                input:
                    none
                output:
                    a list
            """

            if self.cam_opt['tl_path'] != '':
                the_path = os.path.join(self.raspeye_pth, 'timelapse', self.cam_opt['tl_path'])
            else:
                the_path = os.path.join(self.the_path, str(datetime.datetime.today()))
            if not os.path.isdir(the_path):
                os.makedirs(the_path, exist_ok=True)

            if len(self.status) == 0:
                if self.cam_opt['tl_starts'] == 0:
                    # if self.cam_opt['tl_now'] == 0:
                    #     self.cam_opt['tl_exit'] = 1
                    #     return
                    start_time = datetime.datetime.today()
                else:
                    start_time = _validate_time(self.cam_opt['tl_starts'])
                    if not start_time:
                        print("invalid 'tl_starts' time")
                        return
            else:
                if self.cam_opt['tl_starts'] == 0:
                    start_time = datetime.datetime.today() + self.time_res
                else:
                    start_time = _validate_time(self.cam_opt['tl_starts'])
                    if start_time == 0:
                        return

            temp_list = []
            t_delta = datetime.timedelta(seconds=self.cam_opt['tl_delay'])
            cntr = 0
            while cntr < self.cam_opt['tl_nop']:
                temp_list.append((start_time + t_delta * cntr, the_path))
                cntr += 1

            #if len(self.status) != 0:

            print("printing 'self.status':")
            for el in self.status:
                print(el[0], "---------")

            print('')
            print("printing 'temp_list':")
            for el in temp_list:
                print("---------", el[0])
            print('')

            if self.status:
                return _merge_times_lists(self.status, temp_list)
            else:
                return temp_list

        self.status = _create_times_list()

    def start_now(self):
        '''The main method, starts the actual time lapse process.
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
            if self.onepic:
                spl_port = 3
            else:
                spl_port = 0

            current_pic_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f.jpg")
            print("the pic", current_pic_name, "will sit in:", tl_path)
            print("is there such a directory there?:", os.path.isdir(tl_path))
            self.camera.capture(os.path.join(tl_path, current_pic_name),
                                    use_video_port=True,
                                    splitter_port=spl_port,
                                    quality=85)
            if self.onepic:
                print('[TL] A picture has been taken! (MD)')
            else:
                print('[TL] A picture has been taken!')
            return

        #the code below is executed by motion detecting module (separate thread)
        if self.onepic: #if motion detection module needs a pic this will provide it
            _take_picture(self.the_path)
            return

        #the code below is executed for taking several pictures (time lapse mode)
        while self.jobs_added:
            self.jobs_added = False

            #eliminating entries with the time that's passed
            cn = 0
            for el in self.status:
                if el[0] < datetime.datetime.today():
                    cn += 1
                else:
                    break
            self.status = self.status[cn:]
            status_copy = copy.copy(self.status)

            num_of_pic_to_take = len(self.status)
            print("number of pictures to take:", num_of_pic_to_take)
            for take in range(num_of_pic_to_take):

                print("Next pic:", take+1)

                #calculating the time of the next picture, it'll be explained later
                if take < num_of_pic_to_take-1:
                    next_pic = self.status[take+1][0]
                else:
                    next_pic = self.status[-1][0]

                while next_pic - datetime.datetime.today() > self.time_res:
                    if self.cam_opt['tl_exit'] or self.cam_opt['exit']:
                        break
                    if self.cam_opt['tl_req']:
                        break

                if self.cam_opt['tl_exit'] or self.cam_opt['exit']:
                    print('[TL] Received <exit> signal!')
                    break
                if self.cam_opt['tl_req']:
                    self.cam_opt['tl_req'] = 0
                    self.jobs_added = 1
                    self.status = status_copy
                    self._calculate_times()
                    status_copy = copy.copy(self.status)
                    break

                _take_picture(self.status[take][1])
                status_copy = status_copy[take+1:]

        if 'tl_active' in self.cam_opt['running']:
            del self.cam_opt['running']['tl_active']
            self.cam_opt['tl_exit'] = 0

        print("Time lapse's done")
        return

    def get_status(self):
        """Swapping datetime objects with strings.
        """
        tmp_list = []
        for item in range(len(self.status)):
            tmp_list.append((str(self.status[item][0].strftime("%H.%M.%S_%Y-%m-%d")),
                            self.status[item][1]))
        return tmp_list


def timelapse_start(path, camera, cam_opt, md=False): #It's used by threading, it will be redesigned in future
    """Starting threading.
    """
    timelapse_instance = Timelapse(path, camera, cam_opt, md)
    timelapse_instance.start_now()
    print("it's really done now!")
    return

if __name__ == '__main__':
    print("It's a module for rapeye-srv.py")
