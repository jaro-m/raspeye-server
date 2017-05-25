# DIR_NAME = 'md-pictures'
#global camera#, cam_opt, raspeye_path
# running = False
import numpy as np
import datetime, os
import timelapse

class MotionDetected(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, message):
        self.message = message

import picamera.array
class MyMotionDetector(picamera.array.PiMotionAnalysis):
    #import numpy as np
    def __init__(self, camera, detected):
       super().__init__(camera)
       self.detected = detected

    def analyse(self, a):
        '''https://picamera.readthedocs.io/en/release-1.12/recipes2.html
        '''
        #global np
        #np = self.np

        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > 60).sum() > 10:
            #print('Motion detected!')
            #update_md_times(self.thefile)# <--SimpleMotionDetection instances method to add instant taking picture to a list of Timelapse jobs.
            print('Bam!')
            self.detected['detected'] = True
        else:
            #self.mdetected = False
            print('md')

class SimpleMotionDetection():
    '''
    '''
    def update_path(self):
        the_path = os.path.join(self.raspeye_path, self.DIR_NAME, self.theday) #datetime.date.isoformat()) #datetime.now().strftime("%Y-%m-%d"))
        if not os.path.isdir(the_path):
            os.makedirs(the_path, exist_ok=True)
        print('md path > ', the_path)
        self.thepath = the_path


    def __init__(self, camera, connection, camera_options, raspeye_path):
        import os
        self.camera = camera
        self.conn = connection
        self.cam_opt = camera_options
        self.raspeye_path = raspeye_path
        self.DIR_NAME = 'md-pictures'
        self.detected = {'detected': False}
        the_file = os.path.join(self.raspeye_path, 'md-timetable.txt')
        if not os.path.isfile(the_file):
            filehnd = open(the_file, 'w')
            filehnd.close()
        print('printing the_file path from md class:', the_file)
        self.theday = datetime.date.today().isoformat()
        self.thefile = the_file
        self.update_path()
        print('md__init__:', self.thepath)


    def update_md_times(self):
        #global thefile
        #raspeye_path = r_path
        '''writing the time to the time-table file'''
        filehnd = open(self.thefile, 'a')
        filehnd.write(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f\n"))
        filehnd.close()
        timelapse.timelapse_start(self.thepath, self.camera, self.cam_opt)
        return


    def start_md(self):
        import time#, picamera.array, datetime, os
        #import numpy as np
        #import timelapse
        #global raspeye_path
        print(self.raspeye_path)

        #global thefile#, raspeye_path #cam_opt#, camera#, raspeye_path, running
        #running = True

        #thefile = checking_thefile(raspeye_path)
        #print('printing thefile:', thefile)
        self.camera.resolution = (640, 480)
        self.camera.framerate = 30
        self.camera.start_recording('/dev/null', format='h264', motion_output=MyMotionDetector(self.camera, self.detected))
        print('md is recording from now on')
        while (not self.cam_opt['mo_det_exit']) and (not self.cam_opt['exit']):
            if self.detected['detected']:
                print('Bam!Bam!')
                self.detected['detected'] = False
                self.update_md_times()
            #print('---md recording---')
            if self.theday != datetime.date.today().isoformat():
                self.theday = datetime.date.today().isoformat()
                update_path()
        print('md is finishing...')
        self.camera.stop_recording()
        #running = False
        return

def mo_detect(camera, connection, cam_opt, raspeye_path):
    md_instance = SimpleMotionDetection(camera, connection, cam_opt, raspeye_path)
    md_instance.start_md()
    del(md_instance)
    return
if __name__ == '__main__':
        print('motion detection module for raspeye-srv.py')
