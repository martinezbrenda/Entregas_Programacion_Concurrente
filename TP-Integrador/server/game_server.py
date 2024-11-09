import socket
import threading
import pickle
import random

class GameServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []  # Real players' connections
        self.cpu_player_ids = []  # NPC player IDs
        self.max_players = 16  # Total grid size (4x4)
        self.game_state = {
            "players": {},
            "territories": {},
            "turn": None,
            "game_over": False,
            "winner": None,
        }
        self.lock = threading.RLock()  # A reentrant lock must be released by the thread that acquired it. Once a
                                        #thread has acquired a reentrant lock, the same thread may acquire it
                                        #again without blocking; the thread must release it once for each time it
                                        #has acquired it.

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.host, self.port))
            server.listen()
            print(f"Server running on {self.host}:{self.port}")
            self.create_cpu_players()
            while True:
                conn, addr = server.accept()
                print(f"Client connected: {addr}")
                threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()
    
    def create_cpu_players(self):
        with self.lock:
            while len(self.game_state["players"]) < self.max_players:
                player_id = len(self.game_state["players"])
                self.game_state["players"][player_id] = {
                    "id": player_id,
                    "territories": [(player_id % 4, player_id // 4)],
                    "score": 0,
                    "is_cpu": True,
                    "active": True,  # CPUs are always active
                }
                self.cpu_player_ids.append(player_id)
                print(f"CPU Player {player_id} added.")
            self.notify_clients()

    def add_cpu_player(self, player_id=None):
        with self.lock:
            if player_id is None:
                player_id = len(self.game_state["players"])
            self.game_state["players"][player_id] = {
                "id": player_id,
                "territories": [(player_id % 4, player_id // 4)],
                "score": 0,
                "is_cpu": True,
                "active": True,
            }
            self.cpu_player_ids.append(player_id)
            print(f"CPU Player {player_id} added to replace disconnected player.")

    def handle_client(self, conn):
        try:
            with self.lock:
                if self.cpu_player_ids:
                    # Replace a CPU player with a human player
                    player_id = self.cpu_player_ids.pop(0)
                    self.clients.append(conn)
                    self.game_state["players"][player_id]["is_cpu"] = False
                    self.game_state["players"][player_id]["active"] = False  # Set to inactive until they start
                    print(f"CPU Player {player_id} replaced with human player.")
                else:
                    # Add a new player if there's space
                    player_id = len(self.game_state["players"])
                    if player_id >= self.max_players:
                        conn.close()
                        return
                    self.clients.append(conn)
                    self.game_state["players"][player_id] = {
                        "id": player_id,
                        "territories": [(player_id % 4, player_id // 4)],
                        "score": 0,
                        "is_cpu": False,
                        "active": False,  # New flag indicating if the player has started the game
                    }
                # Send player_id to client
                conn.sendall(pickle.dumps({"action": "assign_id", "player_id": player_id}))
                if self.game_state["turn"] is None:
                    self.game_state["turn"] = player_id
                self.notify_clients()

            while True:
                data = conn.recv(4096)
                if not data:
                    print(f"Player {player_id} disconnected.")
                    break
                message = pickle.loads(data)
                self.process_message(player_id, message)
        except Exception as e:
            print(f"Error with client {player_id}: {e}")
        finally:
            with self.lock:
                if conn in self.clients:
                    self.clients.remove(conn)
                if player_id in self.game_state["players"]:
                    del self.game_state["players"][player_id]
                print(f"Player {player_id} disconnected and removed from game.")
                if len(self.game_state["players"]) < self.max_players:
                    # Add a CPU player to replace the disconnected player
                    self.add_cpu_player(player_id)
                if self.game_state["turn"] == player_id:
                    self.next_turn()
                self.notify_clients()
            conn.close()

    def cpu_turn(self, player_id):
         # Acquire lock only when accessing shared resources
        with self.lock:
            if player_id not in self.game_state["players"]:
                print(f"CPU Player {player_id} does not exist.")
                return
            cpu_player = self.game_state["players"][player_id]
            if not cpu_player["territories"]:
                print(f"CPU Player {player_id} has no territories.")
                return
            # Make a copy of the player's territories to use outside the lock
            cpu_territories = list(cpu_player["territories"])
        
        # Find adjacent opponents to challenge
        opponent_id = self.find_opponent(player_id, cpu_territories)
        if opponent_id is not None:
            print(f"CPU Player {player_id} challenges Player {opponent_id}")
            self.handle_challenge(player_id, opponent_id)
        else:
            print(f"CPU Player {player_id} has no opponents to challenge.")
        
        # Move to next player's turn
        self.next_turn()
        self.notify_clients()

    def find_opponent(self, player_id, cpu_territories):
        with self.lock:
            opponents = self.game_state["players"]
        
        for territory in cpu_territories:
            x, y = territory
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 4 and 0 <= ny < 4:
                    with self.lock:
                        for opponent_id, opponent in opponents.items():
                            if (opponent_id != player_id and
                                opponent["active"] and
                                (nx, ny) in opponent["territories"]):
                                if not opponent.get("is_cpu", False):
                                    return opponent_id  # Prioritize human players
                                else:
                                    return opponent_id
        return None


    def process_message(self, player_id, message):
        with self.lock:
            if message["action"] == "start_game":
                self.game_state["players"][player_id]["active"] = True
                print(f"Player {player_id} has started the game.")
                 # Reset game state if necessary
                if self.game_state.get("game_over"):
                    self.reset_game()
            elif message["action"] == "challenge":
                print(f"Server received challenge from Player {player_id} to Player {message['target']}")
                print(self.game_state["players"][player_id])
                if self.game_state["players"][player_id]["active"]:
                    print("Player is active. Handling challenge.")
                    target_id = message["target"]
                    self.handle_challenge(player_id, target_id)
                    self.next_turn()
                else:
                    print(f"Player {player_id} tried to challenge but is not active yet.")
            self.notify_clients()

    def handle_challenge(self, player_id, target_id):
        with self.lock:
            print(f"Handling challenge from Player {player_id} to Player {target_id}")

            if player_id not in self.game_state["players"] or target_id not in self.game_state["players"]:
                print("Challenge invalid: one of the players does not exist.")
                return

            challenger = self.game_state["players"][player_id]
            target = self.game_state["players"][target_id]
            print(f"Challenger territories: {challenger['territories']}")
            print(f"Target territories: {target['territories']}")

            # Check if the target is adjacent
            if not self.is_adjacent(challenger["territories"], target["territories"]):
                print(f"Player {player_id} cannot challenge Player {target_id}: Not adjacent.")
                return

            print("Players are adjacent. Proceeding with challenge.")

            # Simulate challenge result aca cambiar para que muestre el territorio que gano
            challenger_correct = random.choice([True, False])
            target_correct = random.choice([True, False])
            print(f"Challenger correct: {challenger_correct}, Target correct: {target_correct}")

            if challenger_correct and not target_correct:
                # Challenger wins
                if target["territories"]:
                    gained_territory = target["territories"].pop()
                    challenger["territories"].append(gained_territory)
                    challenger["score"] += 10
                    print(f"Player {player_id} gained territory from Player {target_id}")
                if not target["territories"]:
                    print(f"Player {target_id} is eliminated")
                    target["active"] = False
            elif target_correct and not challenger_correct:
                # Target wins
                if challenger["territories"]:
                    lost_territory = challenger["territories"].pop()
                    target["territories"].append(lost_territory)
                    target["score"] += 10
                    print(f"Player {target_id} gained territory from Player {player_id}")
                if not challenger["territories"]:
                    print(f"Player {player_id} is eliminated")
                    challenger["active"] = False
            else:
                # Tie, no territory changes hands
                print(f"No territory changes hands.")

            # Check if the game is over
            game_over = self.check_game_over()
        # Notify clients outside the lock
        self.notify_clients()
        if game_over:
            return  # Stop further processing if the game is over

    
    def next_turn(self):
        cpu_player_id = None
        with self.lock:
            active_player_ids = [pid for pid, pdata in self.game_state["players"].items() if pdata["active"]]
            if not active_player_ids:
                self.game_state["turn"] = None
                print("No active players remaining.")
                return
            current_turn = self.game_state.get("turn")
            if current_turn not in active_player_ids:
                self.game_state["turn"] = active_player_ids[0]
            else:
                current_index = active_player_ids.index(current_turn)
                next_index = (current_index + 1) % len(active_player_ids)
                self.game_state["turn"] = active_player_ids[next_index]
            next_player = self.game_state["players"][self.game_state["turn"]]
            print(f"It's now Player {self.game_state['turn']}'s turn.")
            if next_player.get("is_cpu", False):
                cpu_player_id = self.game_state["turn"]
        # Start CPU turn outside the lock
        if cpu_player_id is not None:
            threading.Thread(target=self.cpu_turn, args=(cpu_player_id,), daemon=True).start()


    def notify_clients(self):
        data = pickle.dumps({"action": "update_game_state", "game_state": self.game_state})
        for conn in self.clients:
            try:
                conn.sendall(data)
            except Exception as e:
                print(f"Error sending data to client: {e}")

    # This method checks if any territory of player A is adjacent to any territory of player B.
    def is_adjacent(self, territories_a, territories_b):
        for (x1, y1) in territories_a:
            for (x2, y2) in territories_b:
                if abs(x1 - x2) + abs(y1 - y2) == 1:
                    return True
        return False
    
    def check_game_over(self):
        with self.lock:
            active_players = [player for player in self.game_state["players"].values() if player["active"]]
            if len(active_players) == 1:
                winner = active_players[0]
                print(f"Game over! Player {winner['id']} has won the game.")
                self.game_state["game_over"] = True
                self.game_state["winner"] = winner["id"]
                self.notify_clients()
                return True  # Indicate that the game is over
            return False
        
    def reset_game(self):
        print("Resetting the game...")
        # Reset territories and scores for all players
        for player_id, player in self.game_state["players"].items():
            player["territories"] = [(player_id % 4, player_id // 4)]
            player["score"] = 0
            player["active"] = True
        self.game_state["turn"] = None
        self.game_state["game_over"] = False
        self.game_state["winner"] = None
        self.next_turn()  # Start the game with the first player's turn
        self.notify_clients()
