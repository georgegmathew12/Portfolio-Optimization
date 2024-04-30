import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
import itertools



class TradingEnv(gym.Env):
    """
  A 3-stock (MSFT, IBM, QCOM) trading environment. Adapted from WJie12's code.

  State: [# of stock owned, current stock prices, cash in hand]
    - array of length n_stock * 2 + 1
    - price is discretized (to integer) to reduce state space
    - use close price for each stock
    - cash in hand is evaluated at each step based on action performed

  Action: sell (0), hold (1), and buy (2)
    - when selling, sell all the shares
    - when buying, buy as many as cash in hand allows
    - if buying multiple stock, equally distribute cash in hand and then utilize the balance
  """

    def __init__(self, train_data, init_invest=20000):
        # data
        self.n_industry = 5
        self.stock_price_history = train_data
        self.n_stock, self.n_step = self.stock_price_history.shape

        # instance attributes
        self.init_invest = init_invest
        self.cur_step = None
        self.stock_owned = None
        self.stock_price = None
        self.cash_in_hand = None

        # action space
        self.action_space = spaces.Discrete(3 ** self.n_industry)

        # observation space:
        stock_max_price = self.stock_price_history.max(axis=1)
        stock_range = [[0, init_invest * 2 // mx] for mx in stock_max_price]
        price_range = [[0, mx] for mx in stock_max_price]
        cash_in_hand_range = [[0, init_invest * 2]]
        self.observation_space = spaces.MultiDiscrete(stock_range + price_range + cash_in_hand_range)

        self._seed()
        self._reset()

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _reset(self):
        self.cur_step = 0
        self.stock_owned = [0] * self.n_stock
        self.stock_price = self.stock_price_history[:, self.cur_step]
        self.cash_in_hand = self.init_invest
        return self._get_obs()

    def _step(self, action):
        assert self.action_space.contains(action)
        prev_val = self._get_val()
        self.cur_step += 1
        self.stock_price = self.stock_price_history[:, self.cur_step]  # update price
        self._trade(action)
        cur_val = self._get_val()
        reward = cur_val - prev_val
        done = self.cur_step == self.n_step - 1
        info = {'cur_val': cur_val}
        return self._get_obs(), reward, done, info

    def _get_obs(self):
        obs = []
        obs.extend(self.stock_owned)
        obs.extend(list(self.stock_price))
        obs.append(self.cash_in_hand)
        return obs

    def _get_val(self):
        return np.sum(self.stock_owned * self.stock_price) + self.cash_in_hand

    def _trade(self, action):

        action_combo = list(map(list, itertools.product([0, 1, 2], repeat=self.n_industry)))
        action_vec = action_combo[action]

        for i, a in enumerate(action_vec):
            if a == 0:
                for j in range(i, 4 * i):
                    if j < self.n_stock:
                        self.cash_in_hand += self.stock_price[j] * self.stock_owned[j]
                        self.stock_owned[j] = 0

                    else:
                        break
            elif a == 2:
                for j in range(i, 4 * i):
                    if j < self.n_stock and self.cash_in_hand > self.stock_price[i] * 200:
                        self.stock_owned[j] += 200  # buy one share
                        self.cash_in_hand -= self.stock_price[j] * 200
                    else:
                        break
