# Vision-System-Python

A new vision system written in Python. The development of this Vision System is heavily based on
the prior versions of the Vision System, which were written in C++.

# Installation Instructions

(Written 9/6/2023, Forrest Milner)

1. Ensure the target computer is running the latest LTS version (22 at time of writing) of Ubuntu. Most likely you will need to put the latest
   version of Ubuntu on a flash drive and boot from it and install. https://ubuntu.com/tutorials/install-ubuntu-desktop#1-overview
This also might entail updating the BIOS of the computer
    a) You might need to update the BIOS of the computer. Do so by searching for the computers model and downloading the bios exe file from dell. Then load onto flash drive, and select update bios flash in the f12 menu.
    b) You should install using the minimal version of Ubuntu.
    c) Set the computer name to "visionsystem" for consistency with other vision systems.
2. Run ```sudo apt update``` to please the Ubuntu gods.
3. Make sure git is installed. If not, run ```sudo apt install git```
4. clone from the git repository into the home directory.
    ```shell
    sudo git clone https://github.com/umdenes100/Vision-System-Python.git
    ```
5. cd into folder
    ```shell
   cd Vision-System-Python
   ```
6. Change permissions of the installer scripts.
    ```shell
   sudo chmod +x installdependencies.sh
   sudo chmod +x install-model-listener.sh
   ```
7. Execute installation script.
    ```shell
   ./installdependencies.sh
   ```
8. Install ML Model Downloader
   ```shell
   ./install-model-listener.sh
   ```
9. Then set the Wi-Fi stuff. Under Network -> Wired turn on the connection. Then click settings, go to IPv4.

The IPv4 method should be Manual. Then set the addresses. The address is 192.168.1.2 The Netmask is 255.255.255.0, The
Gateway is 192.168.1.1

The ArUco marker 0 goes in @ 0,0 spot (lower left). They then ascend clockwise. So ID=1 is in the upper left.

(All other content is not updated.)

![Vision System Diagram](images/VisionSystemDiagram.PNG "Vision System Diagram")

## Communication

This is the "server-side" application for the vision system that communicates with both the
[front-end application](https://github.com/umdenes100/VisionSystemRemoteClient) and the
[WiFi Modules (ESP8266)](https://github.com/umdenes100/WifiFirmware).

### Front-end Communcation

The front-end communication works over **TCP 8080** and **TCP 9000**.

The *image server* is the connection over TCP port 8080 and serves the JPEG images coming
from the video feed. The front-end handles these images and displays them when a user
is connected properly. This connection is a one-way connection, meaning the back-end is
not expecting any communication *back* over port 8080.

The *message server* is the connection over TCP port 9000 and acts as the message communication
back and forth between the front-end and this back-end. This is a two-way communication channel
where the back-end will send things like debug messages and mission calls to the front-end and
the front-end will send other pieces of information back.

### WiFi Communication

The OTV uses the ESP8266 modules to communicate over UDP port 7755. Check out the reference
at the bottom of this README if you don't know the difference between TCP and UDP communication.

The structure of the packets are the following:

```
[seq_byte][func_call][message]
```

**Function Calls:**

- 0 = PING
- 2 = Enes100.begin()
- 4 = Enes100.updateLocation()
- 6 = Enes100.mission()
- 8 = Enes100.print() or Enes100.println()

*NOTE: the sequence numbers are not really used*

## Files

The important files will be listed and summed up below. Check out [NOTES.md](NOTES.md) for more information
and Gary's notes on everything about the Vision System (from the PC to OpenCV to Websocket connections).

### main.py

The entry point to the Vision System. If you are in terminal, go into the dev environment by running
`cd ~/dev/Vision-System-Python` and run `python3 main.py` to start the program. Using the terminal
is the best way to debug as we can add print statements and all that jazz.

If you just want to run the Vision System for normal use, there should be a desktop application
that runs this program. The application should have a little arcade icon and be called "Vision System".

### vs_gui.py

This file includes functions for the functionality behind the GUI for the main window, using **mainwindow.ui**
as the design file for the GUI. The changes on the gui (such as changing the camera settings) are
passed as system commands to change camera settings or passed to a data structure as drawing settings
for **vs_opencv.py** to use.

### vs_opencv.py

This file includes functions for capturing camera frames and passing them to the image server.
This is where the drawings for the video feed are updated using a data structure that **vs_gui.py** writes to
when switches on the GUI menu are changed.

This file depends on **arena.py**, **aruco_marker.py**, and **processed_marker.py**

### vs_comm.py

This is the biggest part of the Vision System code-wise. Connections to and from the Vision System via
TCP ports 8080 and 9000 as well as UDP port 7755 are handled in the functions in this file.

### vs_ws.py

This file has functions for writing to and receiving from a websocket. I decided to separate these
functions from **vs_comm.py** becuase they are long and specific to the websocket server. More details
and my notes are in [NOTES.md](NOTES.md) for websockets.

### vs_mission.py

This contains one big function to return the correct response when a mission() call was called
over UDP 7755.

### mainwindow.ui

This is the GUI interface file for the Vision System. The development of this GUI utility was
done using **Qt 5 Designer**. One could write program to completely design the GUI interface instead
of using this nice utility, but the utility was very nice and useful.

## Contributors

- [Gary](https://github.com/itsecgary)
- [Eric](https://github.com/ephan1068)
- [Forrest](https://github.com/ForrestFire0)

## Resources & References

[TCP vs UDP](https://www.lifesize.com/en/blog/tcp-vs-udp/)
https://github.com/Pithikos/python-websocket-server/blob/56af8aeed025465e70133f19f96db18113e50a91/websocket_server/websocket_server.py#L186
https://github.com/arduino/ArduinoCore-sam/issues/88

