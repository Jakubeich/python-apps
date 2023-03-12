import random
import numpy as np

# Definovat třídu neuronu
class Neuron:
  # Inicializovat váhy a bias
  def __init__(self, weights, bias):
    self.weights = weights
    self.bias = bias

  # Definovat metodu pro výpočet neuronu
  def forward(self, inputs):
    # Lineární výpočet: y = mx + b
    y = np.dot(self.weights, inputs) + self.bias
    return y

class NeuralNetwork:
  # Inicializovat síť
  def __init__(self):
    # Nastavit váhy a bias pro jediný neuron
    weights = np.array([1, 2])
    bias = 0
    self.neuron = Neuron(weights, bias)

  # Definovat metodu pro výpočet neuronu
  def forward(self, inputs):
    # Prostřednictvím neuronu projít vstupy
    return self.neuron.forward(inputs)

class Game:
    # Inicializovat síť
    def __init__(self):
        self.network = NeuralNetwork()
  
    def generate_number(self):
        # Vygenerovat náhodné číslo v rozmezí 0-9
        self.number = random.randint(0, 9)
    
    def check_guess(self, guess):
        # Porovnat hráčův odhad s vygenerovaným číslem
        if guess == self.number:
          return True
        else:
          return False
            
    def run(self):
        # Inicializovat proměnnou pro počet pokusů
        attempts = 0
        max_attempts = 3 # Nastavit maximální počet pokusů na 3

        # Vygenerovat náhodné číslo pro síť k odhadnutí
        self.generate_number()

        # Opakovat hru, dokud hráč neodhadne správně nebo dokud nedosáhne maximálního počtu pokusů
        while attempts < max_attempts:
          # Požádat hráče o odhad
          guess = int(input("Zadejte odhad: "))
          attempts += 1 # Zvýšit počet pokusů o jedna

          # Zkontrolovat hráčův odhad a vypsat výsledek
          result = self.check_guess(guess)
          if result:
            print("Gratuluji, odhadli jste správně!")
            print("Počet pokusů:", attempts) # Vypisovat počet pokusů po ukončení hry
            break # Ukončit hru po správném odhadu
          else:
            print("Bohužel, odhadli jste špatně.")
          
          # Pokud hráč neodhadl správně a dosáhl maximálního počtu pokusů, vypsat výsledek    
          if attempts == max_attempts:
              print("Vyčerpali jste všechny pokusy. Správné číslo bylo:", self.number) # Vypisovat správné číslo po ukončení hry
            
# Vytvořit instanci hry a spustit ji
game = Game()
game.run()