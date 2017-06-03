#!/usr/bin/env python3

import socket
#def preview_mode(conn, camera, cam_opt):
def preview_mode(conn, camera, cam_opt):
    import io, struct
    #global camera #preview_lock #not implemented ATM
    #print(cam_opt)
    conn.settimeout(3)#None for blocking socket
    preview_stream = io.BytesIO()
    camera.led = cam_opt['cam_led']
    connection = True
    while connection:
        camera.capture(preview_stream, 'jpeg', use_video_port=True, splitter_port=2, quality=85)
        flsize = preview_stream.tell()
        flen = struct.pack('<L', flsize)
        try:
            if conn.sendall(flen) != None:
                connection = False
                break
        except BrokenPipeError: #socket.timeout: #BrokenPipeError
            connection = False
            break
        preview_stream.seek(0)
        try:
            if conn.sendall(preview_stream.read(flsize)) != None:
                connection = False
                break
        except socket.timeout:
            connection = False
            break
        preview_stream.seek(0)
        preview_stream.truncate()
        if cam_opt['pr_exit'] or cam_opt['exit']:
            print('Received <exit> signal! (PRV)')
            break
            #connection = False
    preview_stream.close()
    #conn.shutdown(socket.SHUT_WR) #client is shutting down the socket
    conn.close()
    #preview_lock.release()
    print(' <Preview> thread - connection closed')
    print('')
    return

if __name__ == '__main__':
    print("It's just a helper module for raspeye-srv.py")
