# RaspEye-Server

_RaspEye_ is a result of playing with Raspberry Pi Zero. It is a project that has client- and server-side programs (in separate repositories).

[_Raspeye_](https://github.com/usrbit/raspeye) is a client (it will be developed in future, but at the moment I'm planning to use _RaspEye-srv_ as a back-end for my webapp that I'm developing working on my web front-end skills) that connects to the server and is going to send tasks to server. Also it can receive the preview of the RPi camera.

### _raspeye-srv_
It's the server/back-end of the project. Its three main functions are:

- __Motion-detection__ - detecting motion using RPi camera and eventually sending notification to client/email/IM... (at the moment it detects motion, I'm working on an webapp that will use this feature)
- **Time lapse** - takes sequence of pictures (It's there, but needs a lot of improvements).
- __Preview mode__ - just sends picture to the client 'live' (It's simple, but it's the most stable from all the modules at the moment).

The functions/modes work simultaneously, independently of other modes.  
_Motion detection_ is going to work continuously with ability to terminate it or start it again.  
_Time lapse_ can be set up to start/end at a certain date/time.  
_Preview_ mode is limited to 1 client at the moment, but it will change in future.

The code will change a lot, it's just the beginning.
I have just realised the way client 'talks' to server has to change to improve client-server communication.  
A lot will change and it needs many improvements, but server works. There's a mechanism to deal with the connection errors or other problems so basically server should be on and ready for requests all the time.

To run the server you need to place the files in the same directory and start raspeye-srv.py with the port number like that:  
```python3 raspeye.py 12345
```  
where 12345 is the port number the server is going to use (usually you need to set up port forwarding on your router). And yes - I am  developing it using _Python3_. Although you can test it __I don't recommend to run it__ if you don't know what you're doing (development of this project is in early stage!)
