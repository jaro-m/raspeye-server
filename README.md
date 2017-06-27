# RaspEye-Server

_RaspEye_ is a result of playing with Raspberry Pi Zero with a camera module for it. It is a project that has client- and server-side programs (in separate repositories).

[_Raspeye_](https://github.com/usrbit/raspeye) is a client.

This is the server.


### _raspeye-srv_
Its three main functions are:

- __Motion-detection__ - detecting motion using RPi camera and eventually sending notification to client/email/IM... (at the moment it detects motion and saves pictures to its directory) In future plans I'm going to implement different algorithms of motion detection.
- **Time lapse** - takes sequence of pictures.
- __Preview mode__ - just gives preview for the client.

The functions/modes work simultaneously.  
_Motion detection_ is going to work continuously with ability to terminate it and start it again.  
_Time lapse_ can be set up to start at a certain date and time.  
_Preview_ mode is limited to 1 client at the moment, but it will change in future.

The code will change a lot, it's just the beginning.
I might change everything (API to algorithms) and add lots of features.
I'm going to make a separate development branch so the code in the master branch should stay usable. The master branch should always have the tested code that should run on any Raspberry Pi.

To run the server you need to place the files in the same directory and start raspeye-srv.py with the port number like that:  
```
python3 raspeye.py 12345
```  
where 12345 is the port number the server is going to use (usually you need to set up port forwarding on your router).

As a client you can use _raspeye-guiz.py_ from the other repository.

---
To install it you need the files to be in the same directory:
- raspeye-srv.py,
- preview.py,
- motion_detection.py,
- timelapse.py,
- constants.py

The project is being created on a Raspberry Pi Zero v1.3 with 1st gen. camera module.
I use Python3 for the development.
