import gym
from trading_env import TradingEnv
import pandas as pd

df = pd.read_csv('BTC.csv')

MAX_NUM_EPISODES = 1 #1000
MAX_STEPS_PER_EPISODES = len(df.loc[:, 'price1'].values) * 30 

env = TradingEnv(df)

for episode in range(MAX_NUM_EPISODES):
    done = False
    obs = env.reset()
    total_reward = 0.0
    step = 0
    while not done:
        env.render()
        action = env.action_space.sample()
        next_state, reward, done, info = env.step(action)
        obs = next_state
        total_reward += reward
        step += 1
    
    print("\nEpisodio #{} terminado en {} pasos con Reward total de {}".format(episode +1, step, total_reward))

#env.close()

#Qlearner Class 

#__init__ self env
#discretize(self, obs)
#get_action(self, obs)
#learn(self,obs,action,reward,next_obs
#EPSILON_MIN vamos aprendiendo hasta que converga a este numero
#MAX_NUM_EPISODES numero maximo que estamos dispuestos a realizar en caso de no converger
#STEPS_PER_EPISODES pasos hasta cumplir la meta lograda
#ALPHA ratio de aprendizaje del agente (puede ser dinamica)
#GAMMA factor de descuento del agente (lo que vamos perdiendo de un paso a otro para incentivar llegar antes al objetivo)
#NUM_DISCRETE_BINS numero en caso de discretizar el espacio continuno
import numpy as np

EPSILON_MIN = 0.005
max_num_steps = MAX_NUM_EPISODES * MAX_STEPS_PER_EPISODES
EPSILON_DECAY = 500 * EPSILON_MIN / max_num_steps
ALPHA = 0.05
GAMMA = 0.98
NUM_DISCRETE_BINS = 30

class Qlearner(object):
    def __init__(self, environment):
        #"Quarters": spaces.Discrete(4),
        #"Estimators": spaces.Box(low=0, high=1, shape=(8,), dtype=np.float16),
        #"Actual":spaces.Box(low=-10, high=10, shape=(1,), dtype=np.float16)
        self.obs_estimators_shape = environment.observation_space["Estimators"].shape
        self.obs_actual_shape = environment.observation_space["Actual"].shape
        self.obs_bins = NUM_DISCRETE_BINS
        self.obs_actual_high = environment.observation_space["Actual"].high
        self.obs_actual_low = environment.observation_space["Actual"].low
        self.obs_estimators_high = environment.observation_space["Estimators"].high
        self.obs_estimators_low = environment.observation_space["Estimators"].low
        self.obs_actual_width = (self.obs_actual_high - self.obs_actual_low ) / self.obs_bins
        self.obs_estimators_width = (self.obs_estimators_high - self.obs_estimators_low ) / self.obs_bins

        self.action_shape = environment.action_space.n
        # Matriz con los 6 estimadores, precio actual, cuarter, y action shape
        self.Q = np.zeros(( self.obs_bins + 1, self.obs_bins + 1,self.obs_bins + 1, self.obs_bins + 1,
                            self.obs_bins + 1, self.obs_bins + 1,self.obs_bins + 1, self.obs_bins + 1,
                            self.obs_bins + 1,environment.observation_space["Quarters"].n, self.action_shape))
        self.alpha = ALPHA
        self.gamma = GAMMA
        self.epsilon = 1.0
    
    def discretize(self, obs):
        tuple_list = []
        tuple_list.append(list(tuple(int(obs["Estimators"] - self.obs_estimators_low) / self.obs_estimators_width))))
        tuple_list.extend(list(tuple(int(obs["Actual"] - self.obs_actual_low) / self.obs_actual_width))))
        tuple_list.append(obs["Quarters"])
        return tuple(tuple_list)
    
    def get_action(self, obs):
        discrete_obs = self.discretize(obs)
        # seleccion de la accion en basae de epsilon gready (politica agresiva)
        if self.epsilon > EPSILON_MIN:
            self.epsilon -= EPSILON_DECAY
        if np.random.random() > self.epsilon: # con probabilidad 1-epislon elegimos la mejor accion
            return np.argmax(self.Q[discrete_obs])
        else:
            return np.random.choice([a for a in range (self.action_shape) ]) # con probabilida epsilon elegimos una a al azar

    
    def learn(self, obs, action, reward, next_obs):
        pass


