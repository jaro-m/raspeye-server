#!/usr/bin/env python3

def preview_mode(conn, camera, cam_opt):
    import io, struct
    #global preview_lock
    conn.settimeout(3)#None for blocking socket
    preview_stream = io.BytesIO()
    camera.led = cam_opt['cam_led']
    connection = True
    while connection:
        camera.capture(preview_stream, 'jpeg', use_video_port=True, splitter_port=0, quality=85)
        flsize = preview_stream.tell()
        flen = struct.pack('<L', flsize)
        try:
            if conn.sendall(flen) != None:
                connection = False
                break
        except:
            connection = False
            break
        preview_stream.seek(0)
        try:
            if conn.sendall(preview_stream.read(flsize)) != None:
                connection = False
                break
        except:
            connection = False
            break
        preview_stream.seek(0)
        preview_stream.truncate()
    preview_stream.close()
    #conn.shutdown(socket.SHUT_WR)
    conn.close()
    #preview_lock.release()
    print(' <Preview> thread - connection closed')
    print('')
    return

if __name__ == '__main__':
    print("It's just a helper module for RaspEye.py")
