# raspeye-server

RaspEye is a result of playing with Raspberry Pi Zero. It is a project that has client- and server-side programs (in separate repositories).
Raspeye is a client (soon on github) that connects to the server and is going to send tasks to server. Also it can receive the preview of the RPi camera.
Raspeye-srv is the server. Its 3 main functions are:
- Motion-detection (It should be on github soon) - detecting motion using RPi camera and eventually sending notification to client/email/IM...
- Time lapse (needs more testing) is going to take sequence of pictures.
- Preview mode is just sending picture to the client 'live'.
The function/modes are going to work simultaneously, independently of other modes.

