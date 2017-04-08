# raspeye-server

RaspEye is a result of playing with Raspberry Pi Zero. It is a project that has client- and server-side programs (in separate repositories).
Raspeye is a client (soon on github) that connects to the server and is going to send tasks to server. Also it can receive the preview of the RPi camera.

Raspeye-srv is the server. Its 3 main functions are:
- Motion-detection - detecting motion using RPi camera and eventually sending notification to client/email/IM... (at the moment it detects motion)
- Time lapse - is going to take sequence of pictures (It's there, but needs a lot of improvements).
- Preview mode is just sending picture to the client 'live' (It's simple, but it's the most stable from all the modules, its features going to be extended soon).

The functions/modes are going to work simultaneously, independently of other modes.
Motion detection is going to work continuously with ability to terminate it or start it again.
Time lapse can be set up to start at a certain date/time.
Preview mode is limited to 1 client at the moment, but it will change in future.

The code will change a lot, it's just the beginning.
I have just realised the 'API' will have to change to improve client-server communication.
A lot will change in near future, but the basis, the foundation has already been made.
The next bigger job will be on client side (probably GUI enabling better control over the server)

All my work is free software and I'm just trying to figure out which of those licenses would be the best for us.