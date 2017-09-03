#!/usr/bin/env python3

import shutil
from threading import Thread
from time import sleep

class RPeye_Background(Thread):
    '''It controls background jobs.
        At the moment it checks for free space and controls the camera module LED.
    '''

    def __init__(self,
                 group=None,
                 target=None,
                 name="BG-thread",
                 args=(),
                 kwargs=None,
                 verbose=None):
        super().__init__()
        """3 arguments are needed.
            input:
                - raspeye_path = the path to the program's path
                - camera = picamera.PiCamera() instance
                - cam_opt = a dictionary which controls the main program
                    and its modules behaviour, it's also used for communication
                    with Raspeye client.
                    In this case it controls camera's LED
        """

        self.path, self.camera, self.cam_opt = args
        if self.cam_opt['disk_full']:
            self.cam_opt['tl_exit'] = 1
        self.cam_opt['running']['bg_active'] = 1

    def run(self):

        while True:

            if self.cam_opt['exit'] == 1:
                break

            """Checks whether there is at least 200MB free space on the disk"""
            disk_space = shutil.disk_usage(self.path)
            if disk_space[2] // 1048576 < 200:
                self.cam_opt['disk_full'] = 1
            
            self.camera.led = self.cam_opt['cam_led']

            sleep(2)

        if 'bg_active' in self.cam_opt['running']:
            del self.cam_opt['running']['tl_active']
        return
