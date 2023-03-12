import pygame
import random

# Velikost okna
window_size = (800, 600)

# Barva pozadí
bg_color = (0, 0, 0)

# Rychlost hry
speed = 10

# Velikost kostičky
block_size = 20

# Velikost hada
snake_size = 3

# Inicializace pygame
pygame.init()

# Vytvoření okna
window = pygame.display.set_mode(window_size)

# Nastavení titulku okna
pygame.display.set_caption('Snake')

# Nastavení pozadí
window.fill(bg_color)

# Seznam pro uchování souřadnic hada
snake_coords = []

# Inicializace hada
for i in range(snake_size):
    x = random.randint(0, window_size[0] - block_size)
    y = random.randint(0, window_size[1] - block_size)
    snake_coords.append((x, y))

# Funkce pro vykreslení hada
def draw_snake():
    for coord in snake_coords:
        pygame.draw.rect(window, (0, 255, 0), (coord[0], coord[1], block_size, block_size))

# Funkce pro pohyb hada
def move_snake(direction):
    # Získání souřadnic hlavy hada
    head_x, head_y = snake_coords[0]

    # Pohyb hada podle zadaného směru
    if direction == 'up':
        head_y -= block_size
    elif direction == 'down':
        head_y += block_size
    elif direction == 'left':
        head_x -= block_size
    elif direction == 'right':
        head_x += block_size

    # Přidání nové hlavy hada na začátek seznamu souřadnic
    snake_coords.insert(0, (head_x, head_y))

    # Odstranění posledního prvku seznamu souřadnic (očištění hada)
    snake_coords.pop()

# Funkce pro určení, jak se má had pohnout
def get_next_move(food_x, food_y):
    # Získání souřadnic hlavy hada
    head_x, head_y = snake_coords[0]
    
    # Určení, jestli je jídlo vlevo nebo vpravo od hlavy hada
    if food_x < head_x:
        # Pokud je jídlo vlevo, vrátit směr vlevo
        return 'left'
    elif food_x > head_x:
        # Pokud je jídlo vpravo, vrátit směr vpravo
        return 'right'

    # Pokud je jídlo ve stejné vodorovné pozici jako hlava hada, porovnat souřadnice jídla s hlavou hada s ohledem na výšku
    elif food_y < head_y:
        # Pokud je jídlo nad hlavou hada, vrátit směr nahoru
        return 'up'
    elif food_y > head_y:
        # Pokud je jídlo pod hlavou hada, vrátit směr dolů
        return 'down'

# Náhodné souřadnice jídla
food_x = random.randint(0, window_size[0] - block_size)
food_y = random.randint(0, window_size[1] - block_size)

# Hlavní smyčka hry
running = True
while running:
    # Vykreslení hada
    draw_snake()

    # Změna pozice hada podle AI
    direction = get_next_move(food_x, food_y)
    move_snake(direction)

    # Zobrazení vykreslených objektů
    pygame.display.flip()

    # Zpracování událostí
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Ukončení pygame
pygame.quit()