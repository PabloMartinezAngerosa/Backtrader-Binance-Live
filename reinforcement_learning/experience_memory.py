from collections import namedtuple
import random

Experience = namedtuple("Experience", ["obs", "action", "reward", "next_obs", "done"])

class ExperienceMemory(object):
    '''
    Un buffer que simula la memoria del agente
    '''
    def __init__(self, capacity = int(1e6)):
        '''
        :param capcity: Capacidad total de la memoria ciclica. (nunmero maximo de experiencias almacenables)
        :return
        '''
        self.capacity = capacity
        self.memory_idx = 0 # identificador que sabe la experiencia actual
        self.memory = []
    
    def sample(self, batch_size):
        '''
        tamanio de la memoria a recuperar.
        muestra aleatoria
        '''
        assert batch_size <= self.get_size(), "El tamanio de la muestra es superior a la muestra disponible"
        return random.sample(self.memory, batch_size)
    
    def get_size(self):
        return len(self.memory) # numero de experienicas almacenadas en memorias

    def store(self, exp):
        '''
        exp: sirve. Objeto experiencia a ser alamacenado en memoria.
        '''
        self.memory.insert(self.memory_idx % self.capacity, exp)
        self.memory_idx +=1

