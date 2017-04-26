def mo_detect(camera, cam_opt):
    import picamera.array, datetime, os
    import numpy as np

    def checking_thefile():
        if not os.path.isfile('md-times.txt'):
            thefile = open('md-times.txt', 'w')
            thefile.close()
            return

    def update_md_times():
        thefile = open('md-times.txt', 'a')
        thefile.write(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f\n"))
        thefile.close()
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
    camera.start_recording('/dev/null', format='h264', motion_output=MyMotionDetector(camera))
    while (not cam_opt['mo_det_exit']) and (not cam_opt['exit']):
        pass
    camera.stop_recording()
    return

if __name__ == '__main__':
        print('motion detection module for raspeye-srv.py')