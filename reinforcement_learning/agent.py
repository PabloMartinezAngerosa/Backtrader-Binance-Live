from environment import Environment
import random

class Agent:

    def __init__(self):

        self.total_reward = 0

    # recibe un entorno y ejecuta un accion
    # esta se ejecuta desde una politica aleatoria
    def step(self, env):

        # retorna el estado del entorno
        observations = env.get_observations()
        # las posibles acciones que se pueden realizar en el entorno
        actions = env.get_actions()
        selected_action = random.choice(actions)
        reward = env.action(selected_action)
        self.total_reward += reward

        if env.is_done():
            print(self.total_reward)


agent = Agent()
env = Environment()

while not env.is_done():
    agent.step(env)

