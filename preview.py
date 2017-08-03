#!/usr/bin/env python3

import socket
import io
import struct
import logging

logger = logging.getLogger("RE-main.PR")

def preview_mode(conn, camera, cam_opt):
    """displays the preview.
        It still uses pygame.
    """
    #import io, struct
    if not 'pr_active' in cam_opt['running']:
        cam_opt['running']['pr_active'] = 1
    else:
        del cam_opt['running']['pr_active']
        cam_opt['pr_exit'] = 0
        return

    logger.info('[PR] Preview is starting...')
    conn.settimeout(3)#None for blocking socket
    preview_stream = io.BytesIO()
    camera.led = cam_opt['cam_led']
    connection = True
    while connection:
        if cam_opt['pr_exit'] or cam_opt['exit']:
            logger.info('[PR] Received <exit> signal!')
            break
        camera.capture(preview_stream, 'jpeg', use_video_port=True, splitter_port=2, quality=85)
        flsize = preview_stream.tell()
        flen = struct.pack('<L', flsize)
        try:
            if conn.sendall(flen) != None:
                connection = False
                break
        except (BrokenPipeError, socket.timeout) as err:
            logger.exception("Socket error")
            connection = False
            break
        preview_stream.seek(0)
        try:
            if conn.sendall(preview_stream.read(flsize)) != None:
                connection = False
                break
        except socket.timeout:
            logger.exception("Socket error")
            connection = False
            break
        preview_stream.seek(0)
        preview_stream.truncate()
            #connection = False
    preview_stream.close()
    conn.close()
    if 'pr_active' in cam_opt['running']:
        del cam_opt['running']['pr_active']
    cam_opt['pr_exit'] = 0
    logger.info("PR stopped")
    return

if __name__ == '__main__':
    print("It's a module for rapeye-srv.py\nStart raspeye-srv.py!")
