
import numpy as np
import datetime, time, os
import timelapse

class MotionDetected(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, message):
        self.message = message

import picamera.array
class MyMotionDetector(picamera.array.PiMotionAnalysis):

    def __init__(self, camera, detected):
       super().__init__(camera)
       self.detected = detected

    def analyse(self, a):
        '''https://picamera.readthedocs.io/en/release-1.12/recipes2.html
        '''
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > 60).sum() > 10:
            self.detected['detected'] = True
        else:#?#
            pass #--++==**ooGGWWMMWWGGoo**==++--

class SimpleMotionDetection():
    '''
    '''
    def update_path(self):
        the_path = os.path.join(self.raspeye_path, self.DIR_NAME, self.theday)
        if not os.path.isdir(the_path):
            os.makedirs(the_path, exist_ok=True)
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
        self.theday = datetime.date.today().isoformat()
        self.thefile = the_file
        self.update_path()
        self.timedelta = datetime.timedelta(seconds=1)
        self.lastpic = datetime.datetime.now()

    def update_md_times(self):
        '''writing the time to the time-table file'''
        filehnd = open(self.thefile, 'a')
        filehnd.write(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f\n"))
        filehnd.close()
        if datetime.datetime.now() >= self.lastpic + self.timedelta:
            self.lastpic = datetime.datetime.now()
            timelapse.timelapse_start(self.thepath, self.camera, self.cam_opt, md=True)
        return


    def start_md(self):
        #import time

        self.camera.resolution = (640, 480)
        self.camera.framerate = 30
        self.camera.start_recording('/dev/null', format='h264', motion_output=MyMotionDetector(self.camera, self.detected))
        while (not self.cam_opt['mo_det_exit']) and (not self.cam_opt['exit']):
            if self.detected['detected']:
                self.detected['detected'] = False
                self.update_md_times()
            if self.theday != datetime.date.today().isoformat():
                self.theday = datetime.date.today().isoformat()
                update_path()
        self.camera.stop_recording()
        return

def mo_detect(camera, connection, cam_opt, raspeye_path):
    md_instance = SimpleMotionDetection(camera, connection, cam_opt, raspeye_path)
    md_instance.start_md()
    del(md_instance)
    return
if __name__ == '__main__':
        print('motion detection module for raspeye-srv.py')
