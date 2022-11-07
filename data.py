import math
import os
import sys
from dataclasses import dataclass, field

# If running windows
if os.name != 'nt':
    import cv2
from subprocess import Popen, PIPE, STDOUT


# Ok, so we need a way to store the connections from the esp ws_server and the client ws_server.
# It needs to be queryable.

class CameraManager:
    def __init__(self):
        # grab an actual camera as initial camera
        p = Popen('ls -1 /dev/video*', stdout=PIPE, stderr=STDOUT, shell=True)
        self.camera_num = p.communicate()[0].decode().split('\n')[2][-1]
        try:
            self.video = cv2.VideoCapture(int(self.camera_num), cv2.CAP_V4L2)
        except Exception as e:
            print(e)

        self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.video.set(cv2.CAP_PROP_FPS, 30.0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 1920.0)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080.0)

    def set_cam(self, num):
        try:
            self.video.release()
            p = Popen(["v4l2-ctl", f"--device=/dev/video{num}", "--all"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()
            if "brightness" in output.decode():
                video = cv2.VideoCapture(num, cv2.CAP_V4L2)
                video.set(cv2.CAP_PROP_FOURCC,
                          cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))  # depends on fourcc available camera
                video.set(cv2.CAP_PROP_FPS, 30.0)
                video.set(cv2.CAP_PROP_FRAME_WIDTH, 1920.0)  # supported widths: 1920, 1280, 960
                video.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080.0)  # supported heights: 1080, 720, 540
                video.set(cv2.CAP_PROP_FPS, 30.0)  # supported FPS: 30, 15
                print(f'camera set to {num}')
                self.video = video
                self.camera_num = num
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print(f'EXCEPTION: {e}')

    def get_camera(self):
        return self.video


# ProcessedMarker class
@dataclass
class ProcessedMarker:
    id: int
    x: float
    y: float
    pixels: tuple[int, int]
    theta: float = 0

    def __str__(self):
        return f'ID: {self.id}: ({self.x:.2f}, {self.y:.2f}, {self.theta:.2f})'


@dataclass
class DrawingOptions:
    obstacle_presets: list = field(
        default_factory=lambda: ['01A', '01B', '02A', '02B', '10A', '10B', '12A', '12B', '20A', '20B', '21A', '21B'])
    otv_start_loc: int = 0
    mission_loc: int = 1
    randomization: str = '01A'
    otv_start_dir: float = -(math.pi / 2)
    draw_dest: bool = False
    draw_obstacles: bool = False
    draw_arrows: bool = True
    draw_text: bool = True
    draw_coordinate: bool = False
    aruco_markers: dict[int, ProcessedMarker] = field(default_factory=dict)
    first: bool = True
    H: list = field(default_factory=list)
    inverse_matrix: list = field(default_factory=list)

    # self.randomization = self.obstacle_presets[random.randrange(0, 12)]


dr_op: DrawingOptions = DrawingOptions()

team_types: dict = {
    0: "CRASH_SITE",
    1: "DATA",
    2: "MATERIAL",
    3: "FIRE",
    4: "WATER",
}

fake_esp_data: list = [
    {'name': 'Forrest\'s Team', 'mission': 'Data',
     'aruco': {'num': 2, 'visible': True, 'x': 1, 'y': 2, 'theta': 3.14 / 2}},
    {'name': 'Gary\'s Team', 'mission': 'Water',
     'aruco': {'num': 3, 'visible': False, 'x': None, 'y': None, 'theta': None}},
    {'name': 'Yo mama\'s Team (boom roasted)', 'mission': 'get shredded',
     'aruco': {'num': 4, 'visible': True, 'x': 1, 'y': 2, 'theta': 3.14 / 2}}
]

esp_data: list = []

local = 'local' in sys.argv
if not local:
    camera: CameraManager = CameraManager()