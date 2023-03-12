import pygame
import random
import numpy as np

# Konstanty pro nastavení velikosti okna a velikosti hada
WIDTH = 600
HEIGHT = 600
BLOCK_SIZE = 20

# Třída pro neuronovou síť
class NeuralNetwork:
    def __init__(self, input_nodes, hidden_nodes, output_nodes):
        self.input_nodes = input_nodes
        self.hidden_nodes = hidden_nodes
        self.output_nodes = output_nodes

        # Náhodné inicializace vah a biasů
        self.weights_ih = np.random.rand(self.hidden_nodes, self.input_nodes)
        self.weights_ho = np.random.rand(self.output_nodes, self.hidden_nodes)
        self.bias_h = np.random.rand(self.hidden_nodes)
        self.bias_o = np.random.rand(self.output_nodes)

    # Metoda pro předpověď výstupu sítě na základě zadaných vstupů
    def predict(self, inputs):
        # Výpočet skrytých výstupů
        hidden_inputs = np.dot(self.weights_ih, inputs) + self.bias_h
        hidden_outputs = self.sigmoid(hidden_inputs)

        # Výpočet výstupů sítě
        final_inputs = np.dot(self.weights_ho, hidden_outputs) + self.bias_o
        final_outputs = self.sigmoid(final_inputs)

        return final_outputs

    # Metoda pro trénování sítě pomocí zpětného špropravování chyb
    def train(self, inputs, targets):
        # Výpočet skrytých výstupů
        hidden_inputs = np.dot(self.weights_ih, inputs) + self.bias_h
        hidden_outputs = self.sigmoid(hidden_inputs)

        # Výpočet výstupů sítě
        final_inputs = np.dot(self.weights_ho, hidden_outputs) + self.bias_o
        final_outputs = self.sigmoid(final_inputs)

        # Výpočet chyb výstupních uzlů
        output_errors = targets - final_outputs

        # Výpočet chyb skrytých uzlů
        hidden_errors = np.dot(self.weights_ho.T, output_errors)
        
        # Aktualizace vah a biasů
        self.weights_ho += np.dot((output_errors * final_outputs * (1 - final_outputs)), np.transpose([hidden_outputs]))
        self.weights_ih += np.dot((hidden_errors * hidden_outputs * (1 - hidden_outputs)), np.transpose([inputs]))
        
        self.bias_o += output_errors * final_outputs * (1 - final_outputs)
        self.bias_h += hidden_errors * hidden_outputs * (1 - hidden_outputs)
        
    # Metoda pro sigmoidovou funkci
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
    
    # Metoda pro derivaci sigmoidní funkce
    def sigmoid_derivative(self, x):
        return x * (1 - x)
  
# Třída pro hada
class Snake:
    def __init__(self):
        self.position = [100, 50]
        self.body = [[100, 50], [90, 50], [80, 50]]
        self.direction = "RIGHT"
        self.change_to = self.direction

    # Metoda pro přesun hada na další pozici
    def move(self):
        # Získání souřadnic hlavy hada
        head = self.body[0]

        # Podle aktuálního směru hada aktualizujeme jeho pozici
        if self.direction == "RIGHT":
            self.position[0] += BLOCK_SIZE
        elif self.direction == "LEFT":
            self.position[0] -= BLOCK_SIZE
        elif self.direction == "UP":
            self.position[1] -= BLOCK_SIZE
        elif self.direction == "DOWN":
            self.position[1] += BLOCK_SIZE

        # Aktualizace těla hada
        self.body.insert(0, list(self.position))
        self.body.pop()

    # Metoda pro vykreslení hada a jablka na dané ploše
    def draw(self, surface):
        # Vykreslení těla hada
        for pos in self.body:
            pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

        # Vykreslení jablka
        pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(self.apple[0], self.apple[1], BLOCK_SIZE, BLOCK_SIZE))

    # Metoda pro kontrolu, zda došlo k nějaké kolizi
    def check_collision(self):
        # Kontrola kolize se zdí
        if self.position[0] > WIDTH-BLOCK_SIZE or self.position[0] < 0:
            return 1
        elif self.position[1] > HEIGHT-BLOCK_SIZE or self.position[1] < 0:
            return 1

        # Kontrola kolize s vlastním tělem
        for block in self.body[1:]:
            if self.position == block:
                return 1
            
        return 0

    # Metoda pro generování nového jablka
    def set_apple(self):
        self.apple = [random.randrange(1, (WIDTH//BLOCK_SIZE)) * BLOCK_SIZE, random.randrange(1, (HEIGHT//BLOCK_SIZE)) * BLOCK_SIZE]

    # Metoda pro zjištění, zda had sežral jablko
    def eat(self):
        if self.position == self.apple:
            self.apple = []
            self.body.append(self.apple)
            return 1
        else:
            return 0

    def play_game(nn):
        # Inicializace pygame a vytvoření okna
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        running = True
        FPS = 15

        # Vytvoření instance třídy Snake
        snake = Snake()
        snake.set_apple()
        
        # Hlavní herní smyčka
        while running:
            # Nastavení FPS
            pygame.time.Clock().tick(FPS)

            # Získání vstupů pro neuronovou síť (pozice hlavy hada a jablka)
            inputs = (snake.position[0], snake.position[1], snake.apple[0], snake.apple[1])

            # Předpověď výstupu sítě a získání největší hodnoty
            outputs = nn.predict(inputs)
            action = np.argmax(outputs)

            # Nastavení nového směru hada podle výstupu sítě
            if action == 0:
                snake.change_to = "UP"
            elif action == 1:
                snake.change_to = "DOWN"
            elif action == 2:
                snake.change_to = "LEFT"
            elif action == 3:
                snake.change_to = "RIGHT"

            # Kontrola událostí
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        snake.change_to = "UP"
                    if event.key == pygame.K_DOWN:
                        snake.change_to = "DOWN"
                    if event.key == pygame.K_LEFT:
                        snake.change_to = "LEFT"
                    if event.key == pygame.K_RIGHT:
                        snake.change_to = "RIGHT"
                elif event.type == pygame.QUIT:
                    running = False

            # Přesun hada na novou pozici
            snake.move()

            # Kontrola kolizí
            if snake.check_collision() == 1:
                running = False

            # Kontrola, zda had sežral jablko
            if snake.eat() == 1:
                snake.set_apple()

            # Vyčištění obrazovky
            screen.fill((0, 0, 0))

            # Vykreslení hada a jablka
            snake.draw(screen)

            # Aktualizace obrazovky
            pygame.display.update()

# Ukončení pygame
pygame.quit()