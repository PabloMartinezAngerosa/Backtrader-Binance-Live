import gym
import json
import datetime as dt
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2
from custom_env import StockTradingEnv
import pandas as pd
df = pd.read_csv('BTCUSDT-1h.csv')
df = df.sort_values('timestamp')
# The algorithms require a vectorized environment to run
env = DummyVecEnv([lambda: StockTradingEnv(df)])
model = PPO2(MlpPolicy, env, verbose=1)
model.learn(total_timesteps=20000)
obs = env.reset()

for i in range(2000):
  action, _states = model.predict(obs)
  obs, rewards, done, info = env.step(action)
  env.render()