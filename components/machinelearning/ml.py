import time
import json
import os
import numpy as np
import cv2
import threading
from time import sleep
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn.functional as F
import queue

from components.machinelearning.util import preprocess

ml_processor = None

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def start_ml():
    global ml_processor
    ml_processor = MLProcessor()

class MLProcessor:

    model_dir = '~/Vision-System-Python/components/machinelearning/models/'

    def enqueue(self, message):
        ip = message['ESPIP'][0]
        team_name = message['team_name']
        model_index = message["model_index"]
        self.task_queue.put({
            'team_name': team_name,
            'ip': ip,
            'model_index' : model_index
        })

    def handler(self, image, team_name, model_index):
        model_fi = None
        for entry in os.scandir(self.model_dir):
            if entry.name.startswith(team_name) and int(entry.name.split('_')[1]) == model_index:
                model_fi = entry.name
                break

            if model_fi is None:
                print("model file not found" )
                raise Exception(f"Cound not find model for team: {team_name} with model index: {model_index}; Available models: {', '.join([entry.name for entry in os.scandir(model_dir)])}")
            
            num_str = model_fi.split('_')[-1] # get last segment "#.pth"
            num_str = os.path.splitext(num_str)[0] # get rid of ".pth"
            dim = int(num_str)
            
        self.model.fc = torch.nn.Linear(512, dim)
        self.model = self.model.to(torch.device('cpu')) 

        print(f"using model {model_fi}...")
        self.model.load_state_dict(torch.load(self.model_dir + model_fi))

        self.model.eval()
        output = self.model(image)
        output = F.softmax(output, dim=1).detach().cpu().numpy().flatten()

        return output.argmax()

    def processor(self):
        request = self.task_queue.get(block=True, timeout=None)

        ip = request["ip"]
        team_name = request["team_name"]
        model_index = request["model_index"]
        print(f'Handling message from team {team_name}' )

        start = time.perf_counter()
        try:
            cap = cv2.VideoCapture('http://' + ip + "/cam.jpg")
            if cap.isOpened():
                ret, frame = cap.read()
            else:
                print("failed capture" )
                raise Exception("Could not get image from WiFiCam (cv2)")
            
            print('Entering preprocess...' )
            picture = preprocess(frame)
            results = self.handler(picture, team_name, model_index)
        except Exception as e:
            print('FAILED!!!!')
            print(str(e))
            return

        print('Results: ' + str(results) )
        send = time.perf_counter() - start

    def __init__(self):
        self.task_queue = queue.Queue()
        self.model = torchvision.models.resnet18(pretrained=True)

        threading.Thread(name='task queue handler', args=(), target=self.processor).start()
        self.run()