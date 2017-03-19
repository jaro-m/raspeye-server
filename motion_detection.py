def mo_detect(camera, cam_opt):
    import picamera.array, datetime, os
    import numpy as np
    from time import sleep
    #global cam_opt

    def checking_thefile():
        if not os.path.isfile('md-times.txt'):
            thefile = open('md-times.txt', 'w')
            thefile.close()
            return

    def update_md_times():
        thefile = open('md-times.txt', 'a')
        thefile.write(datetime.datetime.now().strftime("%H.%M.%S_%Y-%m-%d \n"))
        thefile.close()
        #print('mo_detect event time saved')
        return

    class MyMotionDetector(picamera.array.PiMotionAnalysis):
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
                #print('Motion detected!')
                update_md_times()

    checking_thefile()
    camera.resolution = (640, 480)
    camera.framerate = 30
    while not cam_opt['mo_det_exit']:
        # camera.start_recording('/dev/null', format='h264', splitter_port=1, motion_output=MyMotionDetector(camera))
        camera.start_recording('/dev/null', format='h264', motion_output=MyMotionDetector(camera))
        # camera.wait_recording(1, splitter_port=1)
        #camera.wait_recording(1)
        sleep(1)
        print(datetime.datetime.now().strftime("%H.%M.%S_%Y-%m-%d \n"))
        if cam_opt['exit'] == True or cam_opt['exit'] == 'yes':
            break
    # camera.stop_recording(splitter_port=1)
    camera.stop_recording()
    return

if __name__ == '__main__':
    import picamera
    with picamera.PiCamera() as camera:
        global cam_opt
        cam_opt = {}
        cam_opt['mo_det_exit'] = False
        mo_detect(camera)
