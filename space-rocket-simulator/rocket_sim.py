import pygame
import sys
import random
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ROCKET_WIDTH = 50
ROCKET_HEIGHT = 100
PLATFORM_WIDTH = 200
PLATFORM_HEIGHT = 10
DOCK_HEIGHT = 20

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set the title
pygame.display.set_caption("Space Rocket Simulator")

# Clock
clock = pygame.time.Clock()

class Rocket:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.acceleration = 0.01
        self.angle = 0
        self.rocket_rect = pygame.Rect(x, y, ROCKET_WIDTH, ROCKET_HEIGHT)

    def update(self):
        self.vy += self.acceleration
        self.y -= self.vy

        # Tilt the rocket and decrease its power
        if self.y < SCREEN_HEIGHT / 2:
            self.angle += 0.5
            self.vx += math.sin(math.radians(self.angle)) * self.acceleration
            self.vy -= math.cos(math.radians(self.angle)) * self.acceleration

        self.x += self.vx
        self.rocket_rect.topleft = (self.x, self.y)

    def draw(self, surface):
        # Draw the rocket body
        pygame.draw.rect(surface, RED, self.rocket_rect)
        # Draw the rocket fins
        pygame.draw.polygon(surface, RED, [(self.x, self.y + ROCKET_HEIGHT // 2), (self.x - ROCKET_WIDTH // 2, self.y + ROCKET_HEIGHT // 2 + ROCKET_WIDTH // 3), (self.x, self.y + ROCKET_HEIGHT // 2 + ROCKET_WIDTH // 3)])
        pygame.draw.polygon(surface, RED, [(self.x + ROCKET_WIDTH, self.y + ROCKET_HEIGHT // 2), (self.x + ROCKET_WIDTH + ROCKET_WIDTH // 2, self.y + ROCKET_HEIGHT // 2 + ROCKET_WIDTH // 3), (self.x + ROCKET_WIDTH, self.y + ROCKET_HEIGHT // 2 + ROCKET_WIDTH // 3)])

class Platform:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.platform_rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)

    def update(self, rocket_x):
        self.x = rocket_x - PLATFORM_WIDTH // 2
        self.platform_rect.x = self.x

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.platform_rect)

def draw_dock(surface, x, y):
    pygame.draw.rect(surface, BLACK, pygame.Rect(x, y, ROCKET_WIDTH, DOCK_HEIGHT))

def main():
    rocket = Rocket(SCREEN_WIDTH // 2 - ROCKET_WIDTH // 2, SCREEN_HEIGHT - ROCKET_HEIGHT - DOCK_HEIGHT - 10)
    platform = Platform(0, SCREEN_HEIGHT - PLATFORM_HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
        
        rocket.update()
        platform.update(rocket.x)
        
        screen.fill(WHITE)
        rocket.draw(screen)
        platform.draw(screen)
        draw_dock(screen, rocket.x, SCREEN_HEIGHT - DOCK_HEIGHT)
        pygame.display.update()
        clock.tick(60)
        
if __name__ == "__main__":
    main()