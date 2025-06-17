import pygame
import random
import math

"""
Escape the Maze
---------------
A game where the player navigates a maze, avoids dangers, and collects rewards.
Created by Martijn de Jonge for the Python Programming MOOC 2025.
"""

pygame.init()

# Constants
TILE_SIZE = 40
WIDTH = 20
HEIGHT = 15
SCREEN_WIDTH = WIDTH * TILE_SIZE
SCREEN_HEIGHT = HEIGHT * TILE_SIZE
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (180, 180, 180)
DARK_GREY = (90, 90, 90)

# Load and scale images 
robot_img = pygame.image.load("robot.png")
robot_img = pygame.transform.scale(robot_img, (TILE_SIZE, TILE_SIZE))

monster_img = pygame.image.load("monster.png")
monster_img = pygame.transform.scale(monster_img, (TILE_SIZE, TILE_SIZE))

coin_img = pygame.image.load("coin.png")
coin_img = pygame.transform.scale(coin_img, (TILE_SIZE, TILE_SIZE))

door_img = pygame.image.load("door.png")
door_img = pygame.transform.scale(door_img, (TILE_SIZE, TILE_SIZE))


class Robot:
    def __init__(self):
        self.position = [1, 1]  # Grid position (tiles)
        self.pixel_position = [self.position[0] * TILE_SIZE, self.position[1] * TILE_SIZE]  # Smooth pixel position
        self.coins_collected = 0
        self.speed = 4  # Pixels per frame
        self.moving = False
        self.move_dir = (0, 0)  # (dx, dy)

    def move(self, dx, dy, game_map):
        if self.moving:
            return  # Don't allow new move while still moving

        new_x = self.position[0] + dx
        new_y = self.position[1] + dy

        if 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT:
            tile = game_map[new_y][new_x]

            if tile == "W":
                return  # Can't move into wall

            if tile == "D" and self.coins_collected < 4:
                return  # Can't exit without enough coins

            # Move accepted
            self.position = [new_x, new_y]
            self.moving = True
            self.move_dir = (dx, dy)

            if tile == "C":
                self.coins_collected += 1
                game_map[new_y][new_x] = "."

    def update(self):
        if not self.moving:
            return

        target_x = self.position[0] * TILE_SIZE
        target_y = self.position[1] * TILE_SIZE

        if self.pixel_position[0] < target_x:
            self.pixel_position[0] += self.speed
            if self.pixel_position[0] > target_x:
                self.pixel_position[0] = target_x
        if self.pixel_position[0] > target_x:
            self.pixel_position[0] -= self.speed
            if self.pixel_position[0] < target_x:
                self.pixel_position[0] = target_x

        if self.pixel_position[1] < target_y:
            self.pixel_position[1] += self.speed
            if self.pixel_position[1] > target_y:
                self.pixel_position[1] = target_y
        if self.pixel_position[1] > target_y:
            self.pixel_position[1] -= self.speed
            if self.pixel_position[1] < target_y:
                self.pixel_position[1] = target_y

        # Arrived at target?
        if self.pixel_position[0] == target_x and self.pixel_position[1] == target_y:
            self.moving = False


class Monster:
    def __init__(self):
        self.position = [7, 7]  # Grid position
        self.pixel_position = [self.position[0] * TILE_SIZE, self.position[1] * TILE_SIZE]
        self.speed = 3 # Pixels per frame 
        self.moving = False
        self.move_dir = (0, 0)
        self.target_position = self.position.copy()

    def move(self, game_map, player_pos):
        if self.moving:
            return

        distance = abs(player_pos[0] - self.position[0]) + abs(player_pos[1] - self.position[1])
        
        if distance <= 5:
            # Move directly toward the player if within 5 tiles, avoiding walls
            if self.position[0] < player_pos[0] and game_map[self.position[1]][self.position[0] + 1] != "W":
                self.start_move(1, 0)
            elif self.position[0] > player_pos[0] and game_map[self.position[1]][self.position[0] - 1] != "W":
                self.start_move(-1, 0)
            elif self.position[1] < player_pos[1] and game_map[self.position[1] + 1][self.position[0]] != "W":
                self.start_move(0, 1)
            elif self.position[1] > player_pos[1] and game_map[self.position[1] - 1][self.position[0]] != "W":
                self.start_move(0, -1)
        else:
            # Build list of possible directions generally towards the player
            directions = []
            if self.position[0] < player_pos[0]:
                directions.append((1, 0)) # move right
            if self.position[0] > player_pos[0]:
                directions.append((-1, 0)) # move left
            if self.position[1] < player_pos[1]:
                directions.append((0, 1)) # move down
            if self.position[1] > player_pos[1]:
                directions.append((0, -1)) # move up

            # Shuffle directions to add unpredictability
            random.shuffle(directions)

            # Try to move in a valid shuffled direction
            for dx, dy in directions:
                new_x = self.position[0] + dx
                new_y = self.position[1] + dy
                if 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT and game_map[new_y][new_x] != "W":
                    self.start_move(dx, dy)
                    return

            random_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(random_dirs)
            for dx, dy in random_dirs:
                new_x = self.position[0] + dx
                new_y = self.position[1] + dy
                if 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT and game_map[new_y][new_x] != "W":
                    self.start_move(dx, dy)
                    return

    def start_move(self, dx, dy):
        self.moving = True
        self.move_dir = (dx, dy)
        self.target_position = [self.position[0] + dx, self.position[1] + dy]

    def update(self):
        if not self.moving:
            return

        target_pixel_x = self.target_position[0] * TILE_SIZE
        target_pixel_y = self.target_position[1] * TILE_SIZE

        if self.pixel_position[0] < target_pixel_x:
            self.pixel_position[0] += self.speed
            if self.pixel_position[0] > target_pixel_x:
                self.pixel_position[0] = target_pixel_x
        if self.pixel_position[0] > target_pixel_x:
            self.pixel_position[0] -= self.speed
            if self.pixel_position[0] < target_pixel_x:
                self.pixel_position[0] = target_pixel_x

        if self.pixel_position[1] < target_pixel_y:
            self.pixel_position[1] += self.speed
            if self.pixel_position[1] > target_pixel_y:
                self.pixel_position[1] = target_pixel_y
        if self.pixel_position[1] > target_pixel_y:
            self.pixel_position[1] -= self.speed
            if self.pixel_position[1] < target_pixel_y:
                self.pixel_position[1] = target_pixel_y

        if self.pixel_position[0] == target_pixel_x and self.pixel_position[1] == target_pixel_y:
            self.position = self.target_position.copy()
            self.moving = False


class Gameplay:
    def __init__(self):
        # Initialize the Pygame window and core game objects
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("-= Maze Runner: The Great Escape =-")
        self.clock = pygame.time.Clock()
        self.robot = Robot()
        self.monster = Monster()
        self.start_time = pygame.time.get_ticks()
        self.running = True

        # Define the game map (W = wall, . = empty, D = door)
        self.game_map = [
            list("WWWWWWWWWWWWWWWWWWWW"),
            list("W..................W"),
            list("W.WWW.W.WWWW.WWWW.WW"),
            list("W.W...W.....W......W"),
            list("W.WWWWW.WWW.W.WWW.WW"),
            list("W...W...W...W.W....W"),
            list("WWW.W.WWW.WWW.W.WWWW"),
            list("W...W.....W....W...W"),
            list("W.W.WWWWW.W.WWWWWW.W"),
            list("W.W.....W.W.W......W"),
            list("W.WWWWW.W.W.W.WWWWWW"),
            list("W.....W.W.W.W.W....W"),
            list("WWW.W.W.W.W.W.W.WWWW"),
            list("W..................D"),
            list("WWWWWWWWWWWWWWWWWWWW")
        ]

        # Place random coins (C) in empty tiles (".") excluding walls (W) and the door (D)
        self.place_random_coins()

    def place_random_coins(self):
        # Randomly place coins in empty tiles
        coin_count = 10  # Number of coins to place
        available_tiles = []
    
        # Collect all empty tiles (".") where coins can be placed
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.game_map[y][x] == ".":
                    available_tiles.append((x, y))
        
        # Randomly choose tiles to place coins
        random.shuffle(available_tiles)
        for i in range(min(coin_count, len(available_tiles))):
            x, y = available_tiles[i]
            self.game_map[y][x] = "C"  # Place a coin



    def draw_brick(self, x, y):
        # Draw a brick tile (wall) at the specified grid position
        pygame.draw.rect(self.screen, GREY, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # Draw brick details (lines) for a textured look
        pygame.draw.line(self.screen, DARK_GREY, (x*TILE_SIZE, y*TILE_SIZE + TILE_SIZE//3),
                         (x*TILE_SIZE + TILE_SIZE, y*TILE_SIZE + TILE_SIZE//3), 2)
        pygame.draw.line(self.screen, DARK_GREY, (x*TILE_SIZE, y*TILE_SIZE + 2*TILE_SIZE//3),
                         (x*TILE_SIZE + TILE_SIZE, y*TILE_SIZE + 2*TILE_SIZE//3), 2)
        pygame.draw.line(self.screen, DARK_GREY, (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE),
                         (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//3), 2)
        pygame.draw.line(self.screen, DARK_GREY, (x*TILE_SIZE + TILE_SIZE//4, y*TILE_SIZE + TILE_SIZE//3),
                         (x*TILE_SIZE + TILE_SIZE//4, y*TILE_SIZE + 2*TILE_SIZE//3), 2)
        pygame.draw.line(self.screen, DARK_GREY, (x*TILE_SIZE + 3*TILE_SIZE//4, y*TILE_SIZE + TILE_SIZE//3),
                         (x*TILE_SIZE + 3*TILE_SIZE//4, y*TILE_SIZE + 2*TILE_SIZE//3), 2)

    def draw_map(self):
        # Draw the game map (walls, coins, door)
        for y, row in enumerate(self.game_map):
            for x, tile in enumerate(row):
                if tile == "W":
                    self.draw_brick(x, y)
                elif tile == "C":
                    self.screen.blit(coin_img, (x*TILE_SIZE, y*TILE_SIZE))
                elif tile == "D":
                    self.screen.blit(door_img, (x*TILE_SIZE, y*TILE_SIZE))

    def draw_score(self):
        # Display the number of coins collected
        font = pygame.font.SysFont(None, 30)
        text = font.render(f"Coins: {self.robot.coins_collected}", True, WHITE)
        self.screen.blit(text, (10, 10))

    def check_victory(self):
        # Check if player reached door with enough coins
        x, y = self.robot.position
        return self.game_map[y][x] == "D" and self.robot.coins_collected >= 4

    def check_defeat(self):
        # Check if monster caught the player
        return self.robot.position == self.monster.position

    def show_splash_and_instructions_screen(self):
        # Display both the character introduction and instructions on a single screen
        font = pygame.font.SysFont(None, 36)
        small_font = pygame.font.SysFont(None, 28)

        bounce_height = 10   # Vertical bounce amount
        bounce_speed = 0.1   # Bounce speed
        bounce_angle = 0     # Angle for smooth bouncing

        running = True
        while running:
            self.screen.fill(DARK_GREY)

            # Title for character introduction
            title_text = font.render("Meet the Characters", True, (255, 255, 255))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 12))

            # Bounce calculation
            offset = int(bounce_height * math.sin(bounce_angle))
            bounce_angle += bounce_speed  # Update the bounce angle to animate the bounce

            # Robot with bounce
            robot_x = SCREEN_WIDTH // 4 - robot_img.get_width() // 2
            robot_y = SCREEN_HEIGHT // 4 - 50 + offset
            self.screen.blit(robot_img, (robot_x, robot_y))
            robot_text = small_font.render("Robot: Collect coins and escape!", True, (255, 255, 255))
            self.screen.blit(robot_text, (SCREEN_WIDTH // 4 - robot_text.get_width() // 2, SCREEN_HEIGHT // 4 + 80))

            # Monster with opposite bounce
            monster_x = 3 * SCREEN_WIDTH // 4 - monster_img.get_width() // 2
            monster_y = SCREEN_HEIGHT // 4 - 50 - offset
            self.screen.blit(monster_img, (monster_x, monster_y))
            monster_text = small_font.render("Monster: Don't get caught!", True, (255, 100, 100))
            self.screen.blit(monster_text, (3 * SCREEN_WIDTH // 4 - monster_text.get_width() // 2, SCREEN_HEIGHT // 4 + 80))

            # Title for instructions
            instructions_title_text = font.render("How to Play", True, (255, 255, 255))
            self.screen.blit(instructions_title_text, (SCREEN_WIDTH // 2 - instructions_title_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

            # Instructions text
            instructions_text = [
                ("Use ", "arrow keys", " to move the robot."),
                ("Avoid the ", "monster", ", or it will catch you!"),
                ("Collect at least ", "4 coins", " before reaching the door!"),
                ("", "", ""),
                ("", "Press any key", " to start the game...")
            ]

            # Draw instructions with highlighted keywords
            y_offset = SCREEN_HEIGHT // 2 + 60
            for normal_start, highlight, normal_end in instructions_text:
                normal_start_surface = font.render(normal_start, True, (255, 255, 255))
                highlight_surface = font.render(highlight, True, (255, 215, 0))
                normal_end_surface = font.render(normal_end, True, (255, 255, 255))

                total_width = normal_start_surface.get_width() + highlight_surface.get_width() + normal_end_surface.get_width()
                current_x = SCREEN_WIDTH // 2 - total_width // 2

                self.screen.blit(normal_start_surface, (current_x, y_offset))
                current_x += normal_start_surface.get_width()
                self.screen.blit(highlight_surface, (current_x, y_offset))
                current_x += highlight_surface.get_width()
                self.screen.blit(normal_end_surface, (current_x, y_offset))
                y_offset += 40  # Adjust spacing between lines for a more compact fit

            pygame.display.flip()

            # Wait for key press to start the game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    running = False

            # Add a frame rate limit
            self.clock.tick(FPS)


    def show_outro(self, victory):
        # Display the game over screen with result
        time_taken = (pygame.time.get_ticks() - self.start_time) // 1000

        font = pygame.font.SysFont(None, 36)
        title_text = font.render("Game Over", True, (255, 255, 255))

        result_text = "You Win!" if victory else "You Lose!"

        outro_texts = [
            result_text,
            f"Coins Collected: {self.robot.coins_collected}",
            f"Time Taken: {time_taken} seconds",
            "Press any key to quit."
        ]

        self.screen.fill(DARK_GREY)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4))

        y_offset = SCREEN_HEIGHT // 4 + 60
        for line in outro_texts:
            text = font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 40

        pygame.display.flip()
        pygame.time.delay(2000)

        # Wait for key press to exit
        waiting_for_key = True
        while waiting_for_key:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    waiting_for_key = False

    def run(self):
        self.show_splash_and_instructions_screen()

        while self.running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            if not self.robot.moving:  # Only accept new input when robot is not moving
                if keys[pygame.K_LEFT]:
                    self.robot.move(-1, 0, self.game_map)
                elif keys[pygame.K_RIGHT]:
                    self.robot.move(1, 0, self.game_map)
                elif keys[pygame.K_UP]:
                    self.robot.move(0, -1, self.game_map)
                elif keys[pygame.K_DOWN]:
                    self.robot.move(0, 1, self.game_map)

            # Monster logic
            if not self.monster.moving:
                self.monster.move(self.game_map, self.robot.position)

            self.monster.update()
            

            # Update robot 
            self.robot.update()

            # Check for win or lose
            if self.check_victory():
                self.show_outro(True)
                self.running = False
                continue
            if self.check_defeat():
                self.show_outro(False)
                self.running = False
                continue

            # Draw everything
            self.screen.fill(DARK_GREY)
            self.draw_map()
            self.screen.blit(robot_img, self.robot.pixel_position)
            self.screen.blit(monster_img, self.monster.pixel_position)
            self.draw_score()

            pygame.display.flip()

        pygame.quit()


game = Gameplay()
game.run()
