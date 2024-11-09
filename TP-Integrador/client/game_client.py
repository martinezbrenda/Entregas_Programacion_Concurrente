import socket
import threading
import pickle

class GameClient:
    def __init__(self, server_host='127.0.0.1', server_port=1234):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_state = {}
        self.player_id = None
        self.connected = False
        self.receiving_thread = None

    def connect(self):
        try:
            self.sock.connect((self.server_host, self.server_port))
            self.connected = True
            self.receiving_thread = threading.Thread(target=self.receive_updates, daemon=True)
            self.receiving_thread.start()
            print("Connected to the server.")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.connected = False

    def receive_updates(self):
        while self.connected:
            print(f"Received game state update: {self.game_state}")
            try:
                data = self.sock.recv(4096)
                if data:
                    message = pickle.loads(data)
                    action = message.get("action")
                    if action == "assign_id":
                        self.player_id = message["player_id"]
                        print(f"Assigned player ID: {self.player_id}")
                    elif action == "update_game_state":
                        self.game_state = message.get("game_state", {})
                    elif action == "player_activated":
                        self.active = True
                        print("You are now active in the game.")
                    else:
                        print("Received unknown action from server.")
                else:
                    # Connection closed by the server
                    print("Disconnected from server.")
                    self.connected = False
                    break
            except Exception as e:
                print(f"Error receiving data: {e}")
                self.connected = False
                break

    def send_message(self, message):
        try:
            if self.connected:
                self.sock.sendall(pickle.dumps(message))
        except Exception as e:
            print(f"Error sending message: {e}")
            self.connected = False
