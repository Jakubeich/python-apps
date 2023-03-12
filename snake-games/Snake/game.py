import pygame
import sys
import random

# velikost herního okna
WIDTH = 400
HEIGHT = 300

# velikost jednotlivých částí těla hada
BLOCK_SIZE = 20

# barva hada a potravy
SNAKE_COLOR = (255, 0, 0)
FOOD_COLOR = (0, 255, 0)

# inicializace pygame a vytvoření okna
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# seznam souřadnic jednotlivých částí těla hada
snake = [(200, 150)]

# náhodné umístění potravy
food_x = random.randint(0, WIDTH - BLOCK_SIZE)
food_y = random.randint(0, HEIGHT - BLOCK_SIZE)

# směr pohybu hada
direction = (1, 0)

# skóre
score = 0

# hlavní herní smyčka
while True:
    # zpracování událostí
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            # změna směru pohybu hada pomocí šipek
            if event.key == pygame.K_UP and direction != (0, 1):
                direction = (0, -1)
            elif event.key == pygame.K_DOWN and direction != (0, -1):
                direction = (0, 1)
            elif event.key == pygame.K_LEFT and direction != (1, 0):
                direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                direction = (1, 0)

    # pohyb hada
    head_x, head_y = snake[-1]
    head_x += direction[0] * BLOCK_SIZE
    head_y += direction[1] * BLOCK_SIZE
    snake.append((head_x, head_y))
    snake.pop(0)

    # kontrola kolizí hada s okraji herního okna nebo sama sebou
    if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT or (head_x, head_y) in snake[:-1]:
        print("Prohrál jsi! Skóre: ", score)
        pygame.quit()
        sys.exit()
        
    # kontrola kolizí hada s potravou
    if head_x >= food_x and head_x <= food_x + BLOCK_SIZE and head_y >= food_y and head_y <= food_y + BLOCK_SIZE:
        # přidání nové části těla a zvýšení skóre
        snake.insert(0, (snake[0][0] - direction[0] * BLOCK_SIZE, snake[0][1] - direction[1] * BLOCK_SIZE))
        score += 1
    
        # náhodné umístění nové potravy
        food_x = random.randint(0, WIDTH - BLOCK_SIZE)
        food_y = random.randint(0, HEIGHT - BLOCK_SIZE)
        
    # vyčištění herního okna
    screen.fill((0, 0, 0))
    
    # vykreslení hada
    for x, y in snake:
        pygame.draw.rect(screen, SNAKE_COLOR, (x, y, BLOCK_SIZE, BLOCK_SIZE))

    # vykreslení potravy
    pygame.draw.circle(screen, FOOD_COLOR, (food_x, food_y), 10)

    # zobrazení okna
    pygame.display.flip()

    # zpomalení hry
    pygame.time.delay(100)
    