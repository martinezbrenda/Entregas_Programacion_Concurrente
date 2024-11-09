import pygame
import sys
import random

class GameUI:
    def __init__(self, client):
        self.client = client
        self.game_state = 'start_screen'  # Possible states: 'start_screen', 'game', 'game_over'

        # Initialize Pygame
        pygame.init()
        self.WIDTH, self.HEIGHT = 400, 400
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("The Floor")
        self.CELL_SIZE = self.WIDTH // 4
        self.font = pygame.font.Font(None, 24)
        self.buttons = []
        self.player_colors = {}

        self.running = True

    def run(self):
        while self.running:
            self.handle_events()
            self.update_display()

        # Clean up Pygame and exit
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.client.sock.close()
            elif event.type == pygame.KEYDOWN:
                if self.game_state == 'start_screen':
                    if event.key == pygame.K_RETURN:
                        self.game_state = 'game'  # Start the game
                        if self.client.connected:
                            # Notify the server
                            self.client.send_message({"action": "start_game"})
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.client.sock.close()
                elif self.game_state == 'game_over':
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.client.sock.close()
                    elif event.key == pygame.K_RETURN:
                        # Restart the game (implement restarting logic if needed)
                        self.game_state = 'start_screen'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == 'game':
                    if self.client.game_state.get("turn") == self.client.player_id:
                        pos = event.pos
                        for button, opponent_id in self.buttons:
                            if button.is_clicked(pos):
                                print(f"Button clicked for opponent {opponent_id}")
                                # Send a challenge action to the server
                                self.client.send_message({"action": "challenge", "target": opponent_id})
                                break


    def update_display(self):
        if self.game_state == 'start_screen':
            self.display_start_screen()
        elif self.game_state == 'game':
            # Check if the game is over
            if self.client.game_state.get("game_over"):
                self.game_state = 'game_over'
                self.winner_id = self.client.game_state.get("winner")
                self.display_game_over_screen()
            else:
                self.display_game_screen()
        elif self.game_state == 'game_over':
            self.display_game_over_screen()

    def display_start_screen(self):
        self.screen.fill((0, 0, 0))  # Black background

        # Game title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("The Floor", True, (255, 255, 255))
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2, self.HEIGHT // 3))

        # Start instructions
        instruction_font = pygame.font.Font(None, 36)
        instruction_text = instruction_font.render("Press ENTER to Start", True, (255, 255, 255))
        self.screen.blit(instruction_text, (self.WIDTH // 2 - instruction_text.get_width() // 2, self.HEIGHT // 2))

        # Additional instructions
        info_text = instruction_font.render("Press ESC to Quit", True, (255, 255, 255))
        self.screen.blit(info_text, (self.WIDTH // 2 - info_text.get_width() // 2, self.HEIGHT // 2 + 40))

        pygame.display.flip()

    def display_game_screen(self):
        self.screen.fill((255, 255, 255))
        self.buttons = []  # Clear previous buttons

        # Render grid and territories
        if self.client.game_state and "players" in self.client.game_state:
            for player in self.client.game_state["players"].values():
                if not player.get("active", True):
                    continue  # Skip inactive players
                player_id = player["id"]
                color = self.get_player_color(player_id)
                for (x, y) in player["territories"]:
                    pygame.draw.rect(
                        self.screen,
                        color,
                        (x * self.CELL_SIZE, y * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                    )
                    text = self.font.render(f"P{player_id}", True, (0, 0, 0))
                    self.screen.blit(text, (x * self.CELL_SIZE + 5, y * self.CELL_SIZE + 5))
                    if player.get("is_cpu", False):
                        cpu_label = self.font.render("CPU", True, (255, 0, 0))
                        self.screen.blit(cpu_label, (x * self.CELL_SIZE + 5, y * self.CELL_SIZE + 25))

            # Highlight adjacent squares for challenge
            if self.client.game_state.get("turn") == self.client.player_id:
                player = self.client.game_state["players"][self.client.player_id]
                adjacent_positions = self.get_adjacent_positions(player["territories"])
                for pos in adjacent_positions:
                    x, y = pos
                    # Check if the position is occupied by an opponent
                    for opponent_id, opponent in self.client.game_state["players"].items():
                        if opponent_id != self.client.player_id and pos in opponent["territories"]:
                            # Draw a button over this square
                            button = Button(
                                x * self.CELL_SIZE,
                                y * self.CELL_SIZE,
                                self.CELL_SIZE,
                                self.CELL_SIZE,
                                (0, 0, 0, 50),  # Semi-transparent black overlay
                                text=f"P{opponent_id}",
                                text_color=(255, 255, 255)
                            )
                            button.draw(self.screen)
                            self.buttons.append((button, opponent_id))
                            break  # Break to avoid duplicate buttons

                # Display turn information
                turn = self.client.game_state.get("turn")
                if turn == self.client.player_id:
                    turn_text = self.font.render("Your Turn", True, (0, 255, 0))
                elif turn is not None and self.client.game_state["players"][turn].get("is_cpu", False):
                    turn_text = self.font.render(f"CPU Player {turn}'s Turn", True, (255, 0, 0))
                elif turn is not None:
                    turn_text = self.font.render(f"Player {turn}'s Turn", True, (0, 0, 0))
                else:
                    turn_text = self.font.render("Waiting for players...", True, (0, 0, 0))
                self.screen.blit(turn_text, (10, self.HEIGHT - 30))

        pygame.display.flip()


    def display_game_over_screen(self):
            self.screen.fill((0, 0, 0))  # Black background

            # Game over text
            title_font = pygame.font.Font(None, 48)
            title_text = title_font.render("Game Over", True, (255, 0, 0))
            self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2, self.HEIGHT // 3))

            # Display winner information
            winner_text = f"Player {self.winner_id} Wins!"
            winner_font = pygame.font.Font(None, 36)
            winner_render = winner_font.render(winner_text, True, (255, 255, 255))
            self.screen.blit(winner_render, (self.WIDTH // 2 - winner_render.get_width() // 2, self.HEIGHT // 2))

            # Restart instructions
            instruction_font = pygame.font.Font(None, 24)
            instruction_text = instruction_font.render("Press ENTER to Restart or ESC to Quit", True, (255, 255, 255))
            self.screen.blit(instruction_text, (self.WIDTH // 2 - instruction_text.get_width() // 2, self.HEIGHT // 2 + 40))

            pygame.display.flip()

    def get_adjacent_positions(self, territories):
        adjacent_positions = set()
        for (x, y) in territories:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 4 and 0 <= ny < 4:
                    adjacent_positions.add((nx, ny))
        return adjacent_positions
    
    def get_player_color(self, player_id):
        # If the player already has a color, return it
        if player_id in self.player_colors:
            return self.player_colors[player_id]
        else:
            # Generate a random color
            color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            self.player_colors[player_id] = color
            return color
    
    def restart_game(self):
        # Reset client state
        self.client.send_message({"action": "start_game"})
        self.game_state = 'game'
        self.player_colors.clear()


class Button:
    def __init__(self, x, y, width, height, color, text='', font_size=24, text_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.text_color = text_color
         # Create a surface for the button
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surface.fill(self.color)

    def draw(self, surface):
         # Draw the button's surface onto the main surface
        surface.blit(self.surface, (self.rect.x, self.rect.y))
        if self.text != '':
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        clicked = self.rect.collidepoint(pos)
        print(f"Button at {self.rect.topleft} clicked: {clicked}")
        return clicked

