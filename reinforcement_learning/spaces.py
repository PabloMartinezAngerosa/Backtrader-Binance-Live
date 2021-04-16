import gym

# BOX tuplas R^n (x_1, x_2, ... , x_n) para x_1,x_2, ... x_n perteneciente Reales
gym.spaces.Box(low=-10, high=10, shape(2,))

#Discrete 
 # {0,1,2,3,4}

#Dictionary
gym.spaces.Dict({
    "position":gym.spaces.Discrete(5),
    "velocity":gym.spaces.Discrete(2)
})

#Multi Binary
gym.spaces.multibinary(3) # x,y,z bool

gym.spaces.multiDiscrete([-10.12],[2,12]) # x,y,z bool

# Producrto cartecianos de esacisl
gym.spaces.tuple(gym.spaces.Discrete(5),gym.spaces.Discrete(2))

# prng semillas aleatorias
import gym
from gym.spaces import *
import sys


def print_spaces(space):
    print(space)
    if isisntance(space, Box):
        print("cota superior low ", space.low)
        print("cota superior high ", space.high)

if __name__ ==  "__main__":