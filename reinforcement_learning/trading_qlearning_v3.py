import numpy as np
import gym
from trading_env_v3 import TradingEnv
import pandas as pd
from numpy import save
from numpy import load
import time

'''
En esta version se refuerza por vela.
Cada vela significa el final de un episido.
Se necesitan aproximadamente 3000 interaciones 
para lograr que una vela sea succes.
Por lo tanto si se entrentan ejemplo 20 candles... se necesitarian 3000*20 episodios = 60.000
Igualmente se esta logrando una convergencia a una buena politica con 30.000 episodios.
El espaco de entorno, esta compueto solo por los 3 estimadores high.
Se le da una emplitud de 100 incremiento y se cropea. 
El problema con la proporcionalidad e versiones previas, es que
no se establece una relacion de los estimadores y en el nivel del precio donde estan pegando.
Por lo cual se pierde informacion imporetante. Ejemplo se puede mantener la misma proporcion de estimadores,
pero en distintos niveles del precio.
'''


#10000
MAX_NUM_EPISODES = 10000
# MAX_STEPS_PER_EPISODES = len(df.loc[:, 'price1'].values) * 30 
MAX_STEPS_PER_EPISODES = 20*30

EPSILON_MIN = 0.05
max_num_steps = MAX_NUM_EPISODES * MAX_STEPS_PER_EPISODES
EPSILON_DECAY = 1  / max_num_steps
ALPHA = 0.05
GAMMA = 0.98 # clase del fri 16 abril 1/(1-gamma) = cantidad_pasos_agente_pretende_vivir mientras mas mas cercano a 0.99 mas datos requiere.
NUM_DISCRETE_BINS = 100
NUM_DISCRETE_BINS_ACTUAL = 100 # van de 20 usd desde el frame point que se habilita

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
        #self.obs_balance_high = environment.observation_space["Balance"].high
        #self.obs_balance_low = environment.observation_space["Balance"].low
        self.obs_estimators_high = environment.observation_space["Estimators"].high
        self.obs_estimators_low = environment.observation_space["Estimators"].low
        self.obs_actual_width = (self.obs_actual_high - self.obs_actual_low ) / self.obs_bins_actual_price
        #self.obs_balance_width = (self.obs_balance_high - self.obs_balance_low ) / self.obs_bins_actual_price 
        self.obs_estimators_width = (self.obs_estimators_high - self.obs_estimators_low ) / self.obs_bins

        self.action_shape = environment.action_space.n
        # Matriz con 3 estimadores high, precio actual cropeado, profit _cropeado , quarter y action shape, is_ready
        # 100*100*100*100*100*4*3*2
        self.Q = np.zeros(( self.obs_bins + 1, self.obs_bins + 1, self.obs_bins + 1,
                            self.obs_bins_actual_price + 1,
                            environment.observation_space["Quarters"].n, environment.observation_space["IsReady"].n, self.action_shape))
        self.alpha = ALPHA
        self.gamma = GAMMA
        self.epsilon = 1.0
    
    def discretize(self, obs):
        tuple_list = []
        tuple_list = list(((obs["Estimators"]- self.obs_estimators_low) / self.obs_estimators_width).astype(int))
        tuple_list.extend(list(((obs["Actual"]- self.obs_actual_low) / self.obs_actual_width).astype(int))) # cropeado
        #tuple_list.extend(list(((obs["Balance"]- self.obs_balance_low) / self.obs_balance_width).astype(int))) # cropeado
        tuple_list.append(obs["Quarters"]),
        tuple_list.append(obs["IsReady"])
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
    start = time.time()
    best_reward = -float("inf")
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
        if count%5000 == 0: 
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
        action = np.argmax(policy[agent.discretize(obs)])
        #print(agent.discretize(obs))
        #print(policy[agent.discretize(obs)])
        #print(action)
        next_obs, reward, done, info = env.step(action)
        obs = next_obs
        total_reward += reward
    print("El balance final es: {}, el reward final es: {}".format(env.balance, total_reward))
    return env.balance, total_reward

if __name__ == "__main__":
    total_frames = 16
    for i in range(total_frames):
        cota_inf_train = i * 10
        cota_sup_train = (i + 2) * 10
        cota_inf_test = cota_sup_train
        cota_sup_test = cota_inf_test + 10
        print("Entrena con indices {}:{}".format(cota_inf_train, cota_sup_train))
        df = pd.read_csv('BTC.csv')
        #df = df.sample(n=60)
        df = df.iloc[cota_inf_train:cota_sup_train,:]
        df = df.reset_index()
        env = TradingEnv(df)
        agent = Qlearner(env)
        print("Go to train! time to wait...")
        learned_policy = train(agent, env)
        print("Save Policy...")
        #save('policy.npy', learned_policy)
        #print(learned_policy)
        print("*********************************************************")
        print("Ajuste con la misma muestra.")
        env = TradingEnv(df)
        env.debug = True
        agent = Qlearner(env)
        balance, reward = test(agent, env, learned_policy)
        print("*********************************************************")
        print("Prueba con indices {}:{}".format(cota_inf_test, cota_sup_test))
        df = pd.read_csv('BTC.csv')
        #df_test = df.sample(n=60)
        df_test = df.iloc[cota_inf_test:cota_sup_test,:]
        df_test = df_test.reset_index()
        env = TradingEnv(df_test,10)
        env.debug = True
        agent = Qlearner(env)
        test(agent, env, learned_policy)
        


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
