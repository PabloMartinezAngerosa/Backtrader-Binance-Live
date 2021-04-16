import numpy as np
import gym
from trading_env import TradingEnv
import pandas as pd

df = pd.read_csv('BTC.csv')

MAX_NUM_EPISODES = 1000
# MAX_STEPS_PER_EPISODES = len(df.loc[:, 'price1'].values) * 30 
MAX_STEPS_PER_EPISODES = 600

EPSILON_MIN = 0.05
max_num_steps = MAX_NUM_EPISODES * MAX_STEPS_PER_EPISODES
EPSILON_DECAY = 1  / max_num_steps
ALPHA = 0.05
GAMMA = 0.98
NUM_DISCRETE_BINS = 5
NUM_DISCRETE_BINS_ACTUAL = 1000

class Qlearner():
    def __init__(self, environment):
        #"Quarters": spaces.Discrete(4),
        #"Estimators": spaces.Box(low=0, high=1, shape=(6,), dtype=np.float16),
        #"Actual":spaces.Box(low=-10, high=10, shape=(1,), dtype=np.float16)
        self.obs_estimators_shape = environment.observation_space["Estimators"].shape
        self.obs_actual_shape = environment.observation_space["Actual"].shape
        self.obs_bins = NUM_DISCRETE_BINS
        self.obs_bins_actual_price = NUM_DISCRETE_BINS_ACTUAL
        self.obs_actual_high = environment.observation_space["Actual"].high
        self.obs_actual_low = environment.observation_space["Actual"].low
        self.obs_estimators_high = environment.observation_space["Estimators"].high
        self.obs_estimators_low = environment.observation_space["Estimators"].low
        self.obs_actual_width = (self.obs_actual_high - self.obs_actual_low ) / self.obs_bins_actual_price
        self.obs_estimators_width = (self.obs_estimators_high - self.obs_estimators_low ) / self.obs_bins

        self.action_shape = environment.action_space.n
        # Matriz con los no estimadores, precio actual, cuarter, y action shape
        self.Q = np.zeros(( self.obs_bins_actual_price + 1,environment.observation_space["Quarters"].n, self.action_shape))
        self.alpha = ALPHA
        self.gamma = GAMMA
        self.epsilon = 1.0
    
    def discretize(self, obs):
        tuple_list = []
        #tuple_list = list(((obs["Estimators"]- self.obs_estimators_low) / self.obs_estimators_width).astype(int))
        tuple_list.extend(list(((obs["Actual"]- self.obs_actual_low) / self.obs_actual_width).astype(int)))
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
            #print("al azar")
            return np.random.choice([a for a in range (self.action_shape) ]) # con probabilida epsilon elegimos una a al azar

    def learn(self, obs, action, reward, next_obs):
        discrete_obs = self.discretize(obs)
        discrete_next_obs = self.discretize(next_obs)
        td_target = reward + self.gamma * np.max(self.Q[discrete_next_obs])
        td_error = td_target - self.Q[discrete_obs][action]
        self.Q[discrete_obs][action] += self.alpha * td_error 


def train(agent, env):
    best_reward = -float("inf")
    for episode in range(MAX_NUM_EPISODES):
        done = False
        obs = env.reset()
        total_reward = 0.0
        while not done:
            action = agent.get_action(obs) # accion elegida segun la ecuacion de qlearning
            next_obs, reward, done, info = env.step(action)
            agent.learn(obs, action, reward, next_obs)
            obs = next_obs
            total_reward += reward
        if total_reward > best_reward:
            best_reward = total_reward
        print("Episodio: {}, con recompensa: {}, mejor recompensa: {}, epsilon: {}, balance {}".format(episode, total_reward, best_reward, agent.epsilon, env.balance )) 
    return agent.Q

def test(agent, env, policy):
    done = False
    obs = env.reset()
    total_reward = 0
    while not done:
        # action = policy[agent.discretize(obs)]
        action = np.argmax(policy[agent.discretize(obs)])
        print(agent.discretize(obs))
        print(policy[agent.discretize(obs)])
        print(action)
        next_obs, reward, done, info = env.step(action)
        obs = next_obs
        total_reward += reward
    print("El balance final es: {}, el reward final es: {}".format(env.balance, total_reward))
    return env.balance, total_reward

if __name__ == "__main__":
    env = TradingEnv(df)
    agent = Qlearner(env)
    learned_policy = train(agent, env)
    print("Go to test...")
    #print(learned_policy)
    env.debug = True
    agent = Qlearner(env)
    test(agent, env, learned_policy)

'''
env = TradingEnv(df)
q = Qlearner(env)
obs = {
        "Quarters": 1,
        "Estimators": np.array([0,0.122,0.21,0.455,0.56,0.7]),
        "Actual": np.array([-3])
}
print(q.discretize(obs))

q.Q[q.discretize(obs)][0] = 0.15
q.Q[q.discretize(obs)][1] = 3.15
q.Q[q.discretize(obs)][2] = 0.7
q.Q[(NUM_DISCRETE_BINS ,NUM_DISCRETE_BINS,NUM_DISCRETE_BINS,NUM_DISCRETE_BINS,NUM_DISCRETE_BINS,NUM_DISCRETE_BINS,NUM_DISCRETE_BINS,3)][2] = 0.7

new_q = np.zeros(( NUM_DISCRETE_BINS + 1, NUM_DISCRETE_BINS + 1,NUM_DISCRETE_BINS + 1, 
                            NUM_DISCRETE_BINS + 1, NUM_DISCRETE_BINS + 1,NUM_DISCRETE_BINS + 1,
                            NUM_DISCRETE_BINS + 1,4, 1))

for i_1 in range(NUM_DISCRETE_BINS +1):
    for i_2 in range(NUM_DISCRETE_BINS +1):
        for i_3 in range(NUM_DISCRETE_BINS +1):
            for i_4 in range(NUM_DISCRETE_BINS +1):
                for i_5 in range(NUM_DISCRETE_BINS +1):
                    for i_6 in range(NUM_DISCRETE_BINS +1):
                        for i_7 in range(NUM_DISCRETE_BINS +1):
                            for i_8 in range(4):
                                arg_max = np.argmax(q.Q[(i_1,i_2,i_3,i_4,i_5,i_6,i_7,i_8)])
                                new_q[(i_1,i_2,i_3,i_4,i_5,i_6,i_7,i_8)] = arg_max
print(new_q)
#print(np.argmax(q.Q, axis=8))
#print(np.argmax(q.Q[q.discretize(obs)]))
#print(q.Q[q.discretize(obs)])
'''