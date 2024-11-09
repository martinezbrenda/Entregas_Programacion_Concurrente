from game_client import GameClient
from ui import GameUI

def main():
    # Initialize the network client
    client = GameClient('127.0.0.1', 1234)
    client.connect()

    # Initialize the game UI
    ui = GameUI(client)
    ui.run()

if __name__ == "__main__":
    main()