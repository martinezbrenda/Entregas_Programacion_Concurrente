from game_server import GameServer

def main():
    server = GameServer('127.0.0.1', 1234)
    server.start()

if __name__ == "__main__":
    main()
