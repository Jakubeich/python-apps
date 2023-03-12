# Description: Spouštěcí soubor pro hru s neuronovou sítí
from game_with_neural import NeuralNetwork
from game_with_neural import Snake

# Inicializace neuronové sítě
nn = NeuralNetwork(4, 6, 2)

# Spuštění hry s použitím neuronové sítě
Snake.play_game(nn)