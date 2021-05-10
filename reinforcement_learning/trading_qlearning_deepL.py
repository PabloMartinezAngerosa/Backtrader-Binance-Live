import numpy as np
import gym
from trading_env_deepL import TradingEnv
import pandas as pd
from numpy import save
from numpy import load
import time
from random import randrange
import torch
from perceptron import SLP
from decay_schedule import LinearDecaySchedule
import random
from experience_memory import ExperienceMemory, Experience
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

#10000
MAX_NUM_EPISODES = 50000
# MAX_STEPS_PER_EPISODES = len(df.loc[:, 'price1'].values) * 30 
MAX_STEPS_PER_EPISODES = 30*40


class SwallowQlearner():
    def __init__(self, environment, learning_rate = 0.005, gamma = 0.98):

        self.action_shape = environment.action_space.n
        
        # Matriz con 4 estimadores, precio actual cropeado, , profit _cropeado , quarter y action shape
        # Neuronas de entrada, 4 high, 4 low, balance, precio actual, indice_actual
        # Neuronas de salida son las posibles acciones
        self.Q = SLP([11], self.action_shape)
        self.Q_optimizer = torch.optim.Adam(self.Q.parameters(), lr=learning_rate)
        self.gamma = gamma
        self.epsilon_max = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = LinearDecaySchedule(initial_value=self.epsilon_max, final_value= self.epsilon_min, max_steps= 0.5* MAX_NUM_EPISODES * MAX_STEPS_PER_EPISODES)
        self.step_num =  0
        self.policy = self.epsilon_greedy_Q

        self.memory = ExperienceMemory(capacity = int(1e5))
    
    def get_action(self, obs):
        return self.policy(obs)
    
    def epsilon_greedy_Q(self, obs):
        if random.random() < self.epsilon_decay(self.step_num):
            action = random.choice([a for a in range(self.action_shape)])
        else:
            action =  np.argmax(self.Q(obs).data.to(torch.device('cpu')).numpy())
        return action

    def learn(self, obs, action, reward, next_obs):
        #discrete_obs = self.discretize(obs)
        #discrete_next_obs = self.discretize(next_obs)
        td_target = reward + self.gamma * torch.max(self.Q(next_obs))
        td_error = torch.nn.functional.mse_loss(self.Q(obs)[action], td_target)
        #self.Q[discrete_obs][action] += self.alpha * td_error
        self.Q_optimizer.zero_grad()
        td_error.backward()
        self.Q_optimizer.step()

    def replay_experience(self, batch_size):
        '''
        vuelve a jugar alamacenando la experiencia almacenada
        ''' 
        experience_batch = self.memory.sample(batch_size)
        self.learn_from_batch_expirience(experience_batch)

    def learn_from_batch_expirience(self, experiences):
        '''
        actualiza la red profunda en base a recuerdos anteriores
        '''
        batch_xp = Experience(*zip(*experiences))
        obs_batch = np.array(batch_xp.obs)
        action_batch = np.array(batch_xp.action)
        reward_batch = np.array(batch_xp.reward)
        next_obs_batch = np.array(batch_xp.next_obs)
        done_batch = np.array(batch_xp.done)
        td_target = reward_batch + ~done_batch * \
                    np.tile(self.gamma, len(next_obs_batch)) * \
                    self.Q(next_obs_batch).detach().max(1)[0].data.numpy()
        td_target = torch.from_numpy(td_target)
        device = torch.device("cpu")
        td_target = td_target.to(device)
        action_idx = torch.from_numpy(action_batch).to(device)
        td_error = torch.nn.functional.mse_loss(
            self.Q(obs_batch).gather(1,action_idx.view(-1,1).long()),
            td_target.float().unsqueeze(1)
        )
        self.Q_optimizer.zero_grad()
        td_error.mean().backward()
        self.Q_optimizer.step()


def train(agent, env):
    best_reward = -float("inf")
    start = time.time()
    count = 0
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
        count +=1
        if count%2000 == 0: 
            print("Episodio: {}, con recompensa: {}, mejor recompensa: {}, epsilon: {}, balance {}".format(episode, total_reward, best_reward, agent.epsilon, env.balance )) 
    end = time.time()
    # total time taken
    print(f"Runtime of the program is {end - start}")
    return agent.Q

def test(agent, env, policy):
    done = False
    obs = env.reset()
    total_reward = 0
    while not done:
        # action = policy[agent.discretize(obs)]
        action = np.argmax(policy[obs])
        #print(agent.discretize(obs))
        #print(policy[agent.discretize(obs)])
        #print(action)
        next_obs, reward, done, info = env.step(action)
        obs = next_obs
        total_reward += reward
    print("El balance final es: {}, el reward final es: {}".format(env.balance, total_reward))
    return env.balance, total_reward

def make_rl():
    df = pd.read_csv('BTC_LBH.csv')
    random_index = randrange(50)
    delta = 20
    print("El index con random es {} con un delta de {}".format(random_index, delta))
    print("Los indices para entrenar RL son {},{}".format(random_index * delta, (random_index + 1) * delta))
    #df = df.sample(n=60)
    df = df.iloc[random_index * delta: (random_index+1) * delta ,:]
    df = df.reset_index()
    env = TradingEnv(df)
    agent = SwallowQlearner(env)
    print("Go to train! time to wait...")
    learned_policy = train(agent, env)
    #print("Save Policy...")
    #save('policy.npy', learned_policy)
    #print(learned_policy)
    print("*********************************************************")
    print("Ajuste con la misma muestra.")
    env = TradingEnv(df)
    env.debug = True
    agent = SwallowQlearner(env)
    test(agent, env, learned_policy)
    print("*********************************************************")
    print("Muestra aleatorio de testeo en la que algunos nunca vio.")
    print("Los indices para entrenar RL son {},{}".format(delta * (random_index+1), delta * (random_index + 2)))
    df = pd.read_csv('BTC_LBH.csv')
    #df_test = df.sample(n=60)
    df_test = df.iloc[delta * ( random_index+1): delta * (random_index + 2),:]
    df_test = df_test.reset_index()
    print("llega211")
    env = TradingEnv(df_test,10)
    env.debug = True
    print("llega21")
    agent = SwallowQlearner(env)
    print("llega2")
    test(agent, env, learned_policy)
    print("*********************************************************")
    
    '''
    print("Muestra aleatorio de testeo en la que algunos nunca vio.30 a 40 con primera")
    print("Los indices para entrenar RL son {},{}".format(delta * (random_index+2), delta * (random_index + 3)))
    df = pd.read_csv('BTC_LBH.csv')
    #df_test = df.sample(n=60)
    df_test = df.iloc[delta * (random_index+2): delta * (random_index + 3),:]
    df_test = df_test.reset_index()
    env = TradingEnv(df_test,10)
    env.debug = True
    agent = SwallowQlearner(env)
    test(agent, env, learned_policy)
    print("*********************************************************")
    print("Muestra aleatorio de testeo en la que algunos nunca vio.40 a 50 con primera")
    print("Los indices para entrenar RL son {},{}".format(delta * (random_index+3), delta * (random_index + 4)))
    df = pd.read_csv('BTC_LBH.csv')
    #df_test = df.sample(n=60)
    df_test = df.iloc[delta * (random_index+3): delta * (random_index + 4),:]
    df_test = df_test.reset_index()
    env = TradingEnv(df_test,10)
    env.debug = True
    agent = SwallowQlearner(env)
    test(agent, env, learned_policy)
    '''

if __name__ == "__main__":
    '''
    for i in range(9):
        make_rl()
    '''
    df = pd.read_csv('BTC.csv')
    df = df.sample(n=40)
    df = df.reset_index()
    env = TradingEnv(df)
    agent = SwallowQlearner(env)
    first_episode = True
    episode_rewards = list()
    for episode in range(MAX_NUM_EPISODES):
        obs = env.reset()
        total_reward = 0.0
        for step in range(MAX_STEPS_PER_EPISODES):
            action = agent.get_action(obs)
            next_obs, reward, done, info = env.step(action)
            agent.memory.store(Experience(obs, action, reward, next_obs, done))
            agent.learn(obs, action, reward, next_obs)

            obs = next_obs
            total_reward += reward
            if done is True:
                if first_episode:
                    first_episode = False
                    max_reward = total_reward
                episode_rewards.append(total_reward)
                if total_reward > max_reward:
                    max_reward = total_reward
                if episode%100==0:
                    print("\nEpisodio {} finalizado con {} reward. El reward maximo fue {}. La media fue {}".format(episode, total_reward, max_reward, sum(episode_rewards)/len(episode_rewards)))
                if agent.memory.get_size()> 100:
                    agent.replay_experience(32)
                break

'''
env = TradingEnv(df)
q = Qlearner(env)
obs = {
        "Quarters": 1,
        "Estimators": np.array([0.122,0.21,0.455,0.7]),
        "Actual": np.array([(26850/27100) - 1]),
        "Balance":np.array([(1000.2/1000)- 1]),
        "IsReady":0
}
q.Q[q.discretize(obs)][0] = 0.15
q.Q[q.discretize(obs)][1] = 3.15
q.Q[q.discretize(obs)][2] = 0.7

print(q.discretize(obs))

'''


# TO LOAD and SAVE!
#save('policy.npy', q.Q)
# load array
#policy = load('policy.npy')
#print(policy[q.discretize(obs)])
# print the array
#print(policy)
