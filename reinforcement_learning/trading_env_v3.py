import random
import json
import gym
from gym import spaces
import pandas as pd
import numpy as np

MAX_ACCOUNT_BALANCE = 1500000
MAX_NUM_SHARES = 5000
MAX_SHARE_PRICE = 40000
MAX_OPEN_POSITIONS = 5
MAX_STEPS = 20000

# $USDT Dollars
INITIAL_ACCOUNT_BALANCE = 1000
BINANCE_FEE = 1 - 0.001 


#df = pd.read_csv('BTC.csv')

# MAX_NUM_EPISODES = 1000
# MAX_STEPS_PER_EPISODES = len(df.loc[:, 'price1'].values) * 30 
# MAX_STEPS_PER_EPISODES = 61
MAX_CANDLE_PER_EPISODES = 20

class TradingEnv(gym.Env):
    """A stock trading environment for OpenAI gym"""
    metadata = {'render.modes': ['human']}

    def __init__(self, df, max_candle=MAX_CANDLE_PER_EPISODES):
        super(TradingEnv, self).__init__()

        self.df = df
        self.max_candle_per_episodes = max_candle
        self.debug = False
        self.delta_space_actual = 0.0007 * 50
        self.delta_space_balance = 0.001 * 50
        self.max_operation = 17 # operacion desde la mitad para adelante no se aceptan. Se deja 2 mas.

        #self.reward_range = (0, MAX_ACCOUNT_BALANCE)

        # Actions of the format: Buy, Sell, Nothing.
        self.action_space = spaces.Discrete(3) # {0,1,2}

        # Quarters - discrete(4) // se encuentra en el primer cuarto, segundo, tercero o final, de la vela.
        # Estimators Lows - Estimators High - Box 0a1 x 6
        # Actual Price - Box -10 a 10 X 1
        self.observation_space = spaces.Dict({
            "IsReady": spaces.Discrete(2),
            "Quarters": spaces.Discrete(4),
            "Estimators": spaces.Box(low=self.delta_space_actual * -1, high=self.delta_space_actual, shape=(3,), dtype=np.float16),
            "Actual": spaces.Box(low=self.delta_space_actual * -1 , high=self.delta_space_actual, shape=(1,), dtype=np.float16) # crop
            #"Balance": spaces.Box(low=self.delta_space_balance * -1, high=self.delta_space_balance, shape=(1,), dtype=np.float16) # crop
        })
    

    
    def reset(self):
        # Reset the state of the environment to an initial state
        self.balance = INITIAL_ACCOUNT_BALANCE
        self.initial_balance = INITIAL_ACCOUNT_BALANCE
        self.inicial_balance = INITIAL_ACCOUNT_BALANCE
        self.usdt_balance = INITIAL_ACCOUNT_BALANCE
        self.bitcoin_balance = 0

        # Set the current step to 1
        self.current_step = 1
        # Set the current candle to 0
        self.current_candle = 0
        # solo se permite una operacion por candle
        self.operation_candle_made = False
        self.is_buy = False

        self.inicial_price = self._get_initial_price()

        return self._next_observation()
    

    def _get_row_candle_step(self):
        index = str(self.current_step)
        return "price" + index
    
    def _get_is_ready(self):
        if self._subida_redy() == True:
            return 1
        else: 
            return 0 

    def _get_cuarter(self):
        actual_index = self.current_step - 1
        cuarter = int((actual_index*4)/30)
        return cuarter
  
    def _get_estimators(self):
        estimators = np.array([])
        return estimators

    def _get_delta_estimators(self):

        low_mean = self.df.loc[self.current_candle,"low_media"]
        high_mean = self.df.loc[self.current_candle,"high_media"]

        delta = high_mean - low_mean
        
        return low_mean, delta

    def _get_estimators(self):
        # order: low_media,low_media_iter2,low_media_iter3,low_delta,high_media,high_media_iter2,high_media_iter3,high_delta
        #low_media = self.df.loc[self.current_candle,"low_media"]
        #low_media_iter2 = self.df.loc[self.current_candle,"low_media_iter2"]
        #low_media_iter3 = self.df.loc[self.current_candle,"low_media_iter3"]

        high_media = self.df.loc[self.current_candle,"high_media"]
        high_media_iter2 = self.df.loc[self.current_candle,"high_media_iter2"]
        high_media_iter3 = self.df.loc[self.current_candle,"high_media_iter3"]


        estimators =  np.array([
            #self._normalize_delta_estimators(low_media),
            #self._normalize_delta_estimators(low_media_iter2),
            #self._normalize_delta_estimators(low_media_iter3),
            self._normalize_delta_estimators(high_media),
            self._normalize_delta_estimators(high_media_iter2),
            self._normalize_delta_estimators(high_media_iter3)
        ])
        return estimators

    def _normalize_delta_estimators(self, value):
        #min_estimator, delta_estimators = self._get_delta_estimators()
        # toma el minimo y el maximo de los estimadores
        # crea el delta del estimador
        # normaliza con el delta mediante regla d 3 proporcional 
        # ejemplo delta entre 15k y 12k y precio actuala norm 18k 
        # (18000 - 12000) / (15000-12000) = 2.0
        # get actual data point
        actual_price = value
        # Actual price
        delta_price = (actual_price / self._get_initial_price()) - 1
        # CROP DELTA PRICE MAS 300 MIN -300
        if delta_price > self.delta_space_actual:
            delta_price = self.delta_space_actual
        if delta_price < (self.delta_space_actual * -1):
            delta_price = self.delta_space_actual * -1

        return delta_price
    
    def _get_current_price(self, normalize = True):
        actual = self.df.loc[self.current_candle,self._get_row_candle_step()]
        if normalize == True:
            actual = self._normalize_delta_estimators(actual)
        return actual
    
    def _get_initial_price(self):
        index_subida = self.df.loc[self.current_candle,"subida_exa_index"]
        etiqueta = "price" + str(index_subida)
        initial = self.df.loc[self.current_candle,etiqueta]
        return initial
    
    def _make_buy_operation(self):
        # compra toda lo que tiene la cuenta en bitcoin al precio actual
        actual_price = self._get_current_price(False)
        bitcoin_bought = (self.usdt_balance / actual_price) * BINANCE_FEE
        self.usdt_balance = 0
        self.bitcoin_balance = bitcoin_bought
        if self.debug == True:
            print("Compra en {} en el index {}".format(actual_price, self.current_step))
    
    def _make_sell_operation(self):
        # vende todo lo que tiene en Bitcoin
        actual_price = self._get_current_price(False)
        usdt = ( self.bitcoin_balance * actual_price ) * BINANCE_FEE
        self.usdt_balance = usdt
        self.bitcoin_balance = 0
        if self.debug == True: 
            print("Vende en {} en el index {}".format(actual_price, self.current_step))
    
    def _bitcoin_balance_to_usdt(self):
        actual_price = self._get_current_price(False)
        return self.bitcoin_balance * actual_price 

    
    def _refresh_balance(self):
        self.balance = self.usdt_balance + self._bitcoin_balance_to_usdt()

    def _next_observation(self):

        # get actual data point
        actual_price = self._get_current_price(False)
        # Actual price
        delta_price = (actual_price / self._get_initial_price()) - 1
        # CROP DELTA PRICE MAS 300 MIN -300
        if delta_price > self.delta_space_actual:
            delta_price = self.delta_space_actual
        if delta_price < (self.delta_space_actual * -1):
            delta_price = self.delta_space_actual * -1

        actual_price = np.array([delta_price])

        # Balance
        balance = self.balance
        delta_balance = (balance / self.inicial_balance) - 1
        # CROP DELTA PRICE MAS 300 MIN -300
        if delta_balance > self.delta_space_balance:
            delta_balance = self.delta_space_balance
        if delta_balance < (self.delta_space_balance * -1):
            delta_balance = self.delta_space_balance * -1

        balance = np.array([delta_balance])

        obs = {
            "IsReady": self._get_is_ready(),
            "Quarters": self._get_cuarter(),
            "Estimators": self._get_estimators(),
            "Actual": actual_price
            #"Balance": balance
        }
        return obs

    def _subida_redy(self):
        if self.current_step > self.max_operation and self.is_buy == False:
            return False
        index = self.df.loc[self.current_candle,"subida_exa_index"]
        if self.current_step == index:
            self.inicial_balance = self.balance
            self.inicial_price = self._get_current_price(False)
        if self.current_step >= index:
            return True
        return False

    def _take_action(self, action):
        # Action space 0,1,2
        # 0 = do nothing
        # 1 = buy
        # 2 = sell

        if self.operation_candle_made == True:
            return True
        else:
            if action == 0 and self.is_buy == True:
                if self.current_step == 30:
                    self._make_sell_operation()
                    self.is_buy = False
                    self.operation_candle_made = True
                # actualiza el balance 
                self._refresh_balance()
            elif action == 1 and self.is_buy == False:
                if self.current_step == 30:
                    # no esta permitido comprar y vender en el utlimo
                    return True
                # hace compra y actualiza balance
                self._make_buy_operation()
                self.is_buy = True
                self._refresh_balance()
            elif action == 2 and self.is_buy == True:
                # hace venta y actualiza balance
                self._make_sell_operation()
                self.is_buy = False
                self.operation_candle_made = True
                self._refresh_balance()
            elif action == 1 and self.is_buy == True:
                if self.current_step == 30:
                    self._make_sell_operation()
                    self.is_buy = False
                    self.operation_candle_made = True
            

        return True

    def step(self, action):

        reward = 0

        if self._subida_redy() == True:
            # Execute one time step within the environment
            self._take_action(action)

        self.current_step += 1
        
        if self.current_step > 30:
            # cambia de candle
            self.current_candle += 1
            self.current_step = 1
            self.operation_candle_made = False
            self.is_buy = False
            

        done = self.balance <= 15.0
        #if(done == True):
        #    print("El balanec es {}".format(self.balance))
        # len(self.df.loc[:, 'price1'].values)
        if self.current_candle == self.max_candle_per_episodes:
            done = True
            self.current_candle = 0
            #print("Llego al ultimo candle!")
        
        #delay_modifier = (self.current_candle + 1) / MAX_STEPS_PER_EPISODES
        #reward = self.balance * delay_modifier

        obs = self._next_observation()

        if done == True:
            reward = self.balance  - self.initial_balance 
        
        return obs, reward, done, {}
    
    def render(self, mode='human', close=False):
        # Render the environment to the screen
        profit = self.balance - INITIAL_ACCOUNT_BALANCE

        print(f'Step: {self.current_step}')
        print(f'Candle: {self.current_candle}')
        print(f'Balance: {self.balance}')
        print(f'Profit: {profit}')





#import pandas as pd

#df = pd.read_csv('BTC.csv')
#env = TradingEnv(df)
#print(env.action_space.n)