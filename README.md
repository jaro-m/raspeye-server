# RaspEye-Server

_RaspEye_ is a result of playing with Raspberry Pi Zero. It is a project that has client- and server-side programs (in separate repositories).

[_Raspeye_](https://github.com/usrbit/raspeye) is a client (it will be developed in future, but at the moment I'm planning to use _RaspEye-srv_ as a back-end for my webapp that I'm developing working on my web front-end skills) that connects to the server and is going to send tasks to server. Also it can receive the preview of the RPi camera.


Anyway this project is not to build a ready to use application and bugs-free, but it's aim is to play with many different areas of programming and try new solutions and ways to make things to work in a different way. It's only one of the targets is to deliver fully functional application and also I care about nice features of it. This project (at least at the present state of developement) can eventually be treated as inspiration and examples of ways certain things work (for example how to recording a video and taking pictures simultaneously or how to simply passing arguments between different parts of code, even from different scripts/files)

There's a lot features yet still to come.

### _raspeye-srv_
It's the server/back-end of the project. Its three main functions are:

- __Motion-detection__ - detecting motion using RPi camera and eventually sending notification to client/email/IM... (at the moment it detects motion and saves pictures to its directory, I'm working on a webapp that will use this feature)
- **Time lapse** - takes sequence of pictures (it's a simple solution at the moment, but works).
- __Preview mode__ - just sends picture to the client 'live' (nothing special, it does the job good enough).

The functions/modes work simultaneously, independently of other modes.  
_Motion detection_ is going to work continuously with ability to terminate it or start it again.  
_Time lapse_ can be set up to start/end at a certain date/time.  
_Preview_ mode is limited to 1 client at the moment, but it will change in future.

The code will change a lot, it's just the beginning.
I have just realised the way client 'talks' to server has to change to improve client-server communication.  
A lot will change and it needs many improvements, but server works. There's a mechanism to deal with the connection errors or other problems so basically server should be on and ready for requests all the time.

To run the server you need to place the files in the same directory and start raspeye-srv.py with the port number like that:  
```
_python3 raspeye.py 12345_
```  
where 12345 is the port number the server is going to use (usually you need to set up port forwarding on your router). And yes - I am  developing it using _Python3_. Although you can test it __I don't recommend to run it__ if you don't know what you're doing (development of this project is in early stage!)

Soon I'll describe how to talk to the server (before I'll be able to finish the client) for curious ones, I'm just in process of changing it.

---
I know it's not easy to test/run it at the moment (especially without the client), but to install it you need the files to be in the same directory:
- raspeye-srv.py,
- preview.py,
- motion_detection.py,
- timelapse.py,
- constants.py

I'll give more details how to run the server soon. I will slowly start working more on the client than the server, but the hole project still needs a lot of work.

The project is being created on a Raspberry Pi Zero v1.3 with 1st gen. camera module.
I promise I'll do the commits more frequently.

I'll provide more info about the project soon (how to install, dependencies, what works and what doesn't and what you can expect in the future)

(Do you think asyncio would be better than threading?)