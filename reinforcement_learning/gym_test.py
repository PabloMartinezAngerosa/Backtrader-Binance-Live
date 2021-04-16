import gym

environment = gym.make("MountainCar-v0")

MAX_NUM_EPISODES = 1000
STEPS_PER_EPISODES = 200

environment.reset()

for episode in range(MAX_NUM_EPISODES):
    done = False
    obs = environment.reset()
    total_reward = 0.0 #variable para guardar la recommpensa total en cada episodio
    step = 0
    while not done:
        environment.render()
        action = environment.action_space.sample() # se va a remplazar por politica del agente
        next_state, reward, done, info = environment.step(action)
        total_reward += reward
        step += 1
        obs = next_state
    environment.render()
    environment.step(environment.action_space.sample())

    print("Episiodio {} finalizado con {} steps. Recompensa final de {}".format(episode, step +1, total_reward))

environment.close()


#Qlerner class
# __init__(self, environment)
# discretize(self, obs) 
# get_action(self, obs)
# learn(self, obs, action, reward, next_obs)
# EPSILON_MIN : vamos aprendiendo mientras el incremento de aprendizaje sea superior a dicho valor
# MAX_NUM_EPISODES : numero de iteraciones dispuesos a realizar
# STEPS_PER_EPISODPES : numero maximo a ralizar por cada episodio
# ALPHA : ratio de aprensizaje del agente (puede llegar a ser dinamico)
# GAMMA: factor de descuento del agente
# NUM_DISCRETE_BINS: numero de divisiones en el caso de discretizar el espacio de estados continuos
EPSILON_MIN = 0.005
max_num_steps = MAX_NUM_EPISODES * STEPS_PER_EPISODES
EPSILON_DECAY = 500 * EPSILON_MIN / max_num_steps
ALPHA = 0.05
GAMMA = 0.98
NUM_DISCRETE_BINS = 30

Class QLerner(object):
    def __init__(self, environment):
        pass
    def discretize(self, obs):
        pass
    def get_action(self, obs):
        pass
    def learn(obs, action, reward, next_obs):
        pass