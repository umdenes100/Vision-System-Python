import json
import logging
import sys
import threading
import time

from websocket_server import WebsocketServer

from components.communications import client_server, esp_server
from components.communications.ping import ping

ws_server: WebsocketServer
jetson_client = None

local = 'local' in sys.argv


# Called for every client connecting (after handshake)
def new_client(client, server: WebsocketServer):
    client_server.send_console_message(
        f'The Jetson (IP: {client["address"][0]}) connected, ready for prediction requests!')
    if len(ws_server.clients) > 1:
        client_server.send_console_message(
            f"There are more than one jetsons connected! {str(len(ws_server.clients))} jetsons connected to the vision system")


# Called for every client disconnecting
def client_left(client, _):
    if client is not None:
        client_server.send_console_message(f'The Jetson disconnected...')


# Called when a Wi-Fi client sends a message
def message_received(client, server: WebsocketServer, message):
    if client is None:
        logging.debug(f'Unknown Jetson sent a message - {message}')
        return

    try:
        message = json.loads(message)
        if message is None:
            client_server.send_console_message(f'Jetson sent an invalid message. (Empty message)')
            return
    except json.JSONDecodeError:
        logging.debug(f'Invalid JSON: {message}')
        client_server.send_console_message(f'Jetson sent an invalid message. Bad JSON.')
        return

    if message['op'] == 'prediction_results':
        if 'teamName' not in message:
            client_server.send_console_message(f'Jetson tried to send prediction results without a team name.')
            return
        if 'error' in message:
            client_server.send_console_message(
                f"Error from Jetson when processing request from {message['teamName']}: {message['error']}")
            return
        if 'prediction' not in message:
            client_server.send_console_message(f'Jetson tried to send prediction results without a prediction.')
            return

        # Send the prediction to the esp
        esp_server.send_prediction(message['teamName'], message['prediction'])
        client_server.send_console_message(
            f"ML prediction from team {message['teamName']} finished in {message['executionTime']:.2f} seconds. Result (prediction: {message['prediction']}) sent to the teams wifi module.")


def request_prediction(team_name, ESPIP, model_index):
    # Find the client with the given team name
    for client in ws_server.clients:
        # if >1 jetson is connected, it doesn't matter which is sent request (as long as connected jetsons have models)
        ws_server.send_message(client, json.dumps({'op': 'prediction_request', 'ESPIP': ESPIP, 'team_name': team_name, 'model_index': model_index}))
        return True
    return False


# noinspection PyTypeChecker
def start_server():
    global ws_server
    ws_server = None
    try:
        if local:
            if 'host' in sys.argv:
                ws_server = WebsocketServer(port=7756, host=sys.argv[sys.argv.index('host') + 1])
            else:
                ws_server = WebsocketServer(port=7756)
        else:
            ws_server = WebsocketServer(host='192.168.1.2', port=7756)
    except OSError as e:
        if e.errno == 98:
            logging.error('Program is already running on this computer. Please close other instance.')
            exit(1)
    try:
        if ws_server is None:
            logging.error(
                'jetson_server -> ws_server is None. Did you make sure to set the network up correctly? (Assign static IP on wired connection) See readme.md')
            return
    except NameError:
        logging.error(
            'client_server -> ws_server is not defined. Did you make sure to set the network up correctly? (Assign static IP on wired connection) See readme.md')
        return
    ws_server.set_fn_new_client(new_client)
    ws_server.set_fn_client_left(client_left)
    ws_server.set_fn_message_received(message_received)
    logging.debug(f'Starting client jetson_server on port {ws_server.port:d}')
    threading.Thread(target=ws_server.run_forever, name='Jetson WS Server').start()

    # # We will ping all esp clients to make sure they haven't disconnected. Sadly, when ESP clients power off
    # # unexpectedly, they do not fire the disconnect callback.
    # def check_connection():
    #     while True:
    #         for client in ws_server.clients:
    #             if not ping(client['address'][0]):
    #                 logging.debug(f'Client {client["address"][0]} is not responding to ping. Disconnecting.')
    #                 ignorable_disconnects.add(client['address'][0])
    #                 # noinspection PyProtectedMember
    #                 ws_server._terminate_client_handler(client['handler'])
    #         time.sleep(1)
    #
    # threading.Thread(target=check_connection, daemon=True, name='Jetson Check Connection').start()
