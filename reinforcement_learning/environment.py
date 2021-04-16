'''
import random

class Environment:

    def __init__(self):

        # ejecuta 10 pasos por el entorno, y una vez terminado obtiene una determinada recompensa
        self.episodes_left = 10

    # puede ser una matriz con los pixeles del juego de atari, hasta una iteracion de estados
    def get_observations(self):
        return [0, 1, 2]

    # acciones que puede ejecutar el agente. Ejemplo comprar y vender acciones. 
    def get_actions(self):
        return [0,1]
    
    def is_done(self):
        return self.episodes_left == 0
        
    # el agente ejecuta una accion y cual ejecuta
    def action(self, action):
        if self.is_done():
            print("El juego ha terminado!")
            return
        

        self.episodes_left -= 1

        # retorna la recompenza
        return random.random()


'''

from gym import envs

env_names = [env.id for env in envs.registry.all()]

for name in sorted(env_names):
    print(name)