import pygame
import pygame_gui
import math
import sys
import os
import numpy as np
import random
from pygame_gui.elements import UILabel
from pygame import transform, Surface

#start_time = datetime.datetime.now()

# Physical constants
G = 6.67430e-11  # gravitational constant
M_SUN = 1.98892e30  # mass of the sun
M_EARTH = 5.9742e24  # mass of Earth
R_EARTH = 6371e3  # radius of Earth

# Scaling factors
SCALE_FACTOR = 1e9
TIME_STEP = 100

# Počáteční podmínky pro každou planetu
planet_init = {
    "Mercury": {
        "m": 3.285e23, # hmotnost
        "r": 2.4397e6, # poloměr
        "a": 57.91e9, # velká poloosa
        "e": 0.2056, # excentricity
        "i": 7.005, # inklinace
        "O": 48.33, # longitude vstupního uzlu
        "o": 77.45, # argument pericentra
        "theta": 0 # pravý ascension
    },
    "Earth": {
        "m": M_EARTH,
        "r": R_EARTH,
        "a": 149.60e9,
        "e": 0.0167,
        "i": 0.000,
        "O": -11.26,
        "o": 102.95,
        "theta": 0
    },
    "Mars": {
        "m": 6.39e23,
        "r": 3.3895e6,
        "a": 227.93e9,
        "e": 0.0934,
        "i": 1.850,
        "O": 49.58,
        "o": 336.03,
        "theta": 0
    },
    "Venus": {
        "m": 4.8675e24,
        "r": 6.0518e6,
        "a": 108.21e9,
        "e": 0.0067,
        "i": 3.3946,
        "O": 76.68,
        "o": 131.53,
        "theta": 0
    },
    "Moon": {
        "m": 7.342e22,  # mass
        "r": 1.7371e6,  # radius
        "a": 384400e3,  # semi-major axis
        "e": 0.0549,    # eccentricity
        "i": 5.145,     # inclination
        "O": 0.0,       # longitude of ascending node
        "o": 0.0,       # argument of pericenter
        "theta": 0      # true anomaly
    }
}

# set initial zoom level
zoom_level = 1

def crop_image_to_circle(image, radius):
    cropped_image = Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(cropped_image, (255, 255, 255), (radius, radius), radius)
    cropped_image.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return cropped_image

def generate_star_positions(num_stars, screen_width, screen_height):
    star_positions = []
    for _ in range(num_stars):
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        star_positions.append((x, y))
    return star_positions

def draw_stars(screen, star_positions, star_color=(255, 255, 255)):
    for pos in star_positions:
        pygame.draw.circle(screen, star_color, pos, 1)
        
def move_camera(event, camera_position, sun_position):
    move_speed = 10000000000 # adjust this value to change the speed of the camera movement
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            camera_position[0] += move_speed
            sun_position[0] += move_speed
        elif event.key == pygame.K_RIGHT:
            camera_position[0] -= move_speed
            sun_position[0] -= move_speed
        elif event.key == pygame.K_UP:
            camera_position[1] += move_speed
            sun_position[1] += move_speed
        elif event.key == pygame.K_DOWN:
            camera_position[1] -= move_speed
            sun_position[1] -= move_speed
    return camera_position, sun_position

def draw_sun(screen, zoom_level, sun_position):
    sun_image_path = os.path.join("images", "sun.png")
    sun_image = pygame.image.load(sun_image_path)

    sun_radius = int(20 * zoom_level)
    sun_image = transform.scale(sun_image, (sun_radius * 2, sun_radius * 2))
    sun_image = crop_image_to_circle(sun_image, sun_radius)

    # vzcentruj slunce doprostred orbit i pri zoomu
    sun_x = max(0, min(screen.get_width() - sun_radius * 2, sun_position[0] - sun_radius))
    sun_y = max(0, min(screen.get_height() - sun_radius * 2, sun_position[1] - sun_radius))

    screen.blit(sun_image, (sun_x, sun_y))

#def update_simulation_time(t):
#    global start_time
#    elapsed_time = datetime.timedelta(seconds=t)
#    simulation_time = start_time + elapsed_time
#    return simulation_time.strftime("%Y/%m/%d/%H/%M/%S")

class Body:
    def __init__(self, name, m, r, a, e, i, O, o, theta):
        self.name = name # jméno tělesa
        self.m = m # hmotnost
        self.r = r # poloměr
        self.a = a # velká poloosa
        self.b = a * math.sqrt(1 - e**2) # malá poloosa
        self.e = e # excentricity
        self.i = math.radians(i) # inklinace
        self.O = math.radians(O) # longitude vstupního uzlu
        self.o = math.radians(o) # argument pericentra
        self.theta = math.radians(theta) # pravý ascension

        self.x = 0 # x-ová souřadnice
        self.y = 0 # y-ová souřadnice
        self.z = 0 # z-ová souřadnice
        self.vx = 0 # x-ová rychlost
        self.vy = 0 # y-ová rychlost
        self.vz = 0 # z-ová rychlost
            
    def compute(self, t, bodies):
        t /= TIME_STEP

        if self.name == "Moon":
            earth = next(body for body in bodies if body.name == "Earth")
            # Compute the relative position and velocity of the Moon with respect to Earth
            r_earth = math.sqrt((self.x - earth.x) ** 2 + (self.y - earth.y) ** 2 + (self.z - earth.z) ** 2)
            v_earth = math.sqrt(G * earth.m / r_earth)

            # Update the position and velocity of the Moon
            self.x = earth.x + r_earth * (1 - self.e) * math.cos(self.theta)
            self.y = earth.y + r_earth * (1 - self.e) * math.sin(self.theta)
            self.z = earth.z

            self.vx = -v_earth * math.sin(self.theta + self.o) * math.sin(self.O) + v_earth * math.cos(self.theta + self.o) * math.cos(self.O) * math.cos(self.i)
            self.vy = v_earth * math.sin(self.theta + self.o) * math.cos(self.O) + v_earth * math.cos(self.theta + self.o) * math.sin(self.O) * math.cos(self.i)
            self.vz = v_earth * math.cos(self.theta + self.o) * math.sin(self.i)

        else:
            # výpočet polohy tělesa
            x = self.a * (math.cos(self.theta) - self.e)
            y = self.b * math.sin(self.theta)
            z = 0
            self.x = x * math.cos(self.O) - y * math.cos(self.i) * math.sin(self.O) + z * math.sin(self.i) * math.sin(self.O)
            self.y = x * math.sin(self.O) + y * math.cos(self.i) * math.cos(self.O) - z * math.sin(self.i) * math.cos(self.O)
            self.z = y * math.sin(self.i) + z * math.cos(self.i)

            # výpočet rychlosti tělesa
            r = math.sqrt(self.x**2 + self.y**2 + self.z**2)
            v = math.sqrt(G * M_SUN / r)
            self.vx = -v * math.sin(self.theta + self.o) * math.sin(self.O) + v * math.cos(self.theta + self.o) * math.cos(self.O) * math.cos(self.i)
            self.vy = v * math.sin(self.theta + self.o) * math.cos(self.O) + v * math.cos(self.theta + self.o) * math.sin(self.O) * math.cos(self.i)
            self.vz = v * math.cos(self.theta + self.o) * math.sin(self.i)

            # výpočet gravitačních sil působících na těleso
            for body in bodies:
                if body != self:
                    r2 = math.sqrt((self.x - body.x)**2 + (self.y - body.y)**2 + (self.z - body.z)**2)
                    F = G * self.m * body.m / r2**2
                    self.vx += F * (body.x - self.x) / r2 / self.m
                    self.vy += F * (body.y - self.y) / r2 / self.m
                    self.vz += F * (body.z - self.z) / r2 / self.m

            # výpočet nové polohy a rychlosti tělesa
            self.x += self.vx * t
            self.y += self.vy * t
            self.z += self.vz * t
            self.theta += math.sqrt(G * M_SUN / self.a**3) * t
            
    def draw_bodies(self, screen, zoom_level, camera_position):
        planet_image_path = os.path.join("images", f"{self.name.lower()}.png")
        planet_image = pygame.image.load(planet_image_path)

        # Scale the image based on the radius of the planet
        image_scale = int(5000 * self.r * zoom_level / SCALE_FACTOR)
        scaled_image = transform.scale(planet_image, (image_scale, image_scale))

        # Crop the image to a circle using a mask
        cropped_image = crop_image_to_circle(scaled_image, image_scale // 2)

        image_x = int(((self.x - camera_position[0]) * zoom_level) / SCALE_FACTOR) + 400 - image_scale // 2
        image_y = int(((self.y - camera_position[1]) * zoom_level) / SCALE_FACTOR) + 300 - image_scale // 2

        screen.blit(cropped_image, (image_x, image_y))

    def draw_orbits(self, screen, zoom_level, camera_position):
        pygame.draw.ellipse(screen, (255, 255, 255), (int(((-self.a - camera_position[0]) * zoom_level) / SCALE_FACTOR) + 400, int(((-self.b - camera_position[1]) * zoom_level) / SCALE_FACTOR) + 300, int((2 * self.a * zoom_level) / SCALE_FACTOR), int((2 * self.b * zoom_level) / SCALE_FACTOR)), 1)
        
    def distance_to_earth(self, earth):
        return np.sqrt((self.x - earth.x)**2 + (self.y - earth.y)**2 + (self.z - earth.z)**2)
        
def main():
    global TIME_STEP
    global zoom_level
    camera_position = [0, 0] # x, y
    sun_position = [400, 300] # x, y
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Solar system simulator")
    clock = pygame.time.Clock()

    # Set up the user interface manager and slider
    ui_manager = pygame_gui.UIManager((800, 600))
    rotation_speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((50, 10), (200, 20)), start_value=1, value_range=(1, 10), manager=ui_manager)
    slider_label = UILabel(relative_rect=pygame.Rect((50, 35), (200, 20)), text="Planet Speed Slider", manager=ui_manager)
    slider_min_label = UILabel(relative_rect=pygame.Rect((30, 10), (20, 20)), text="1", manager=ui_manager) 
    slider_max_label = UILabel(relative_rect=pygame.Rect((250, 10), (20, 20)), text="10", manager=ui_manager)
    #time_label = UILabel(relative_rect=pygame.Rect((20, 80), (200, 20)), text="", manager=ui_manager)
    
    star_positions = generate_star_positions(100, 800, 600)

    distance_labels = []

    bodies = []
    for body in planet_init:
        new_body = Body(body, planet_init[body]["m"], planet_init[body]["r"], planet_init[body]["a"], planet_init[body]["e"], planet_init[body]["i"], planet_init[body]["O"], planet_init[body]["o"], planet_init[body]["theta"])
        bodies.append(new_body)
        if new_body.name != "Earth":
            label = UILabel(relative_rect=pygame.Rect((580, 10 + 20 * len(distance_labels)), (200, 20)), text="", manager=ui_manager)  # Change the position of the labels to the top right corner
            distance_labels.append((new_body, label))
    t = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == rotation_speed_slider:
                        TIME_STEP = 0.5 / rotation_speed_slider.get_current_value()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    zoom_level *= 1.1
            elif event.button == 5:  # Mouse wheel down
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    zoom_level /= 1.1
                    
        if event.type == pygame.MOUSEWHEEL:
            zoom_change = event.y
            zoom_level += zoom_change * 1e-2
            if zoom_level < 1e-1:
                zoom_level = 1e-1
            elif zoom_level > 10e1:
                zoom_level = 10e1

        camera_position, sun_position = move_camera(event, camera_position, sun_position)
        ui_manager.process_events(event)

        ui_manager.update(1 / 60.0)

        screen.fill((0, 0, 0))
        draw_stars(screen, star_positions)

        for body in bodies:
            body.compute(t, bodies)

        earth = next(body for body in bodies if body.name == "Earth")

        for body, label in distance_labels:
            distance = body.distance_to_earth(earth)
            label.set_text(f"{body.name}: {distance / 1000:.0f} km")

        for body in bodies:
            body.draw_orbits(screen, zoom_level, camera_position)

        draw_sun(screen, zoom_level, sun_position)

        for body in bodies:
            body.draw_bodies(screen, zoom_level, camera_position)

        t += TIME_STEP

        ui_manager.draw_ui(screen)

        pygame.display.flip()
        clock.tick(60)
        
if __name__ == "__main__":
    main()