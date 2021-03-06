#!/usr/bin/python3
"""
Bittensor.
by: AlphaGriffin
"""

__author__ = "Eric Petersen @Ruckusist"
__copyright__ = "Copyright 2018, The Alpha Griffin Project"
__credits__ = ["Eric Petersen", "Shawn Wilson", "@alphagriffin"]
__license__ = "***"
__version__ = "0.0.2"
__maintainer__ = "Eric Petersen"
__email__ = "ruckusist@alphagriffin.com"
__status__ = "Beta"

#////////////////// | Imports | \\\\\\\\\\\\\\\#
# generic
import os, sys, time, datetime, collections
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'
from timeit import default_timer as timer
runtime = timer()
from tqdm import tqdm, trange

# crypto
import ccxt

# Tensorflow
from ag.bittensor.ai.AI import Q_Trader
import numpy as np

# Dataset
import ag.bittensor.ai.dataprep as dataprep
from ag.bittensor.ai.dataprep import DataStruct
import pandas as pd

# GameEngine // need access to engine for reward data
import ag.bittensor.game.engine as engine

# REPLACING THE OLD STUFFS
from ag.bittensor.ai.stock_env import StockEnv
# from ag.bittensor.ai.DQN_trade import DQN_Trade as bot

# Utilities
import ag.bittensor.utils.options as options
import ag.bittensor.utils.plotter as plotter
# import ag.bittensor.utils.sheets as sheets
import ag.bittensor.utils.printer as printer
import ag.logging as log

# set globals
log.set(log.WARN)


class Bittensor(object):
    """
    Bittensor.
    Another AlphaGriffin Project 2018.
    Alphagriffin.com
    """

    def __init__(self, options):
        """Use the options for a proper setup."""
        self.options = options
        self.options.save_file = True
        # build objects
        self.plotter = plotter.Plot(options)
        log.debug('Loaded Plotter Program.')
        # self.sheets = sheets.gHooks(options)
        # log.debug('Loaded gHooks Program.')
        self.P = printer.Printer(options)
        log.debug('Loaded Printer Program.')
        # self.agent = Q_Trader(options)
        # log.debug('Loaded AI Program.')
        self.dataHandler = dataprep.DataHandler(options)
        log.debug('Loaded Data Handler Program')
        self.gameEngine = engine.GameEngine(options)
        log.debug('Loaded Game Engine.')

        # CONSOLE LOGGING
        self.P('Setup Complete')
        log.debug('setup complete')

        self.P('Starting BitTensor Service.')
        log.debug('Checking Configuration...')

        self.mins_to_train = 2
        """
        self.P('Using Exchanges:')
        for id in list(self.options.use_exchanges.split(',')):
            self.P("{}".format(id))
        self.P('Trading Pairs:')
        for id in list(self.options.use_pairs.split(',')):
            self.P("{}".format(id))
        """

    def main(self):
        self.P('Thing #1: get Dataset')
        ss = self.get_megaset()
        self.P('Thing #2: setup Model')
        model = Q_Trader(self.options, ss)
        self.P('Thing #3: Training the Model for {} mins'.format(self.mins_to_train))
        while model.IsRunning:
            for i in trange(7, desc='Epoch', leave=False, ascii=True, smoothing=0.01):
                if not model.IsRunning:
                    break
                iters = int(len(ss)/240)
                for j in trange(iters, leave=False, desc='Round', ascii=True, smoothing=0.5):
                    if not model.IsRunning:
                        break
                    batch = ss[j * 240: j * 240 + 240]
                    env = StockEnv(batch)
                    set = env.reset()
                    while True:
                        action = model.egreedy_action(set)
                        next_set, reward, done = env.gostep(action)
                        model.train(set, action, reward, next_set, done)
                        set = next_set
                        if done:
                            tqdm.write("Total Global Steps: {} | Loss: {} | Reward: {}".format(
                                model.stats.g_step, model.stats.cost, env.cash), end='\r')
                            break
                    # Training OFF switch ...
                    cur_runtime = timer() - runtime
                    if int(cur_runtime / 60) > self.mins_to_train:
                        model.save_or_load()
                        model.running = False
                        self.P('Shutting \'er Down due to time limit.')
                        break
                model.save_or_load()
                tqdm.write('Saved at Global Step: {}, Total Loss: {}'.format(
                    model.stats.g_step, model.stats.cost
                ))
                # finish stats
                tqdm.write('Current Runtime is {:.1f} mins'.format(float(timer() - runtime) / 60))
                
        self.P('Total Runtime is {:.1f} mins'.format(float(timer() - runtime) / 60))
        model.session.close()
        return True

    """ Depricated.
    def main(self):
        exchange = 'poloniex'
        pair = 'LTC/BTC'

        # ss = self.get_dataset(exchange, pair)
        ss = self.get_megaset()
        # self.P('Total Runtime to collect and process all data is {:.1f} mins'.format(float(timer()-runtime)/60))
        # start AI engine.
        Agent = bot(self.options)
        Agent.running = True
        data = ss
        print("trying to finish here... SHAPE: {}".format(np.array(data).shape))
        # print(data.shape)
        # exit()
        if False:
            self.P('Gathering options for training session.')

            if False:
                training_cycles = trange(2)
                iters = trange(2)
            else:
                training_cycles = trange(10)
                iters = trange(int(len(data) / 240),
                                ascii=True,
                                desc="{}".format('iters'),
                                dynamic_ncols=True,
                                smoothing=0,
                                leave=False,
                                unit_scale=True)


            for i in training_cycles:
                tqdm.write("Round: {}".format(i))
                for iter_step in iters:
                    # tqdm.write("Iter step {}".format(iter_step))
                    iter_data = data[
                                iter_step * 240: iter_step * 240 + 240
                                ]
                    # time.sleep(3)
                    # sys.exit()

                    # exit()
                    # build data set and reset to 0
                    env = StockEnv(iter_data)
                    s = env.reset()

                    # until break
                    while True:
                        # first S is data 0 from first dataloop
                        # s is recycled from bottom of loop
                        action = Agent.egreedy_action(s)

                        s_, reward, done = env.gostep(action)
                        # print ("Action: {} | 0 = buy, 1 = sell".format(action))
                        # print ("Reward: {:.4f}".format(reward))
                        # print ("Current Price set: {}".format(s_))
                        Agent.train(s, action, reward, s_, done)
                        # print ("Prediction made...")
                        # print("Total Cash on hand?: {}".format(env.cash))
                        s = s_
                        if done:
                            # print("done")
                            tqdm.write("Total Cash on hand?: {:.8f}".format(env.cash))
                            tqdm.write("Total Global Steps: {}".format(Agent.stats.g_step))
                            tqdm.write("Total Loss of Model: {}".format(Agent.stats.cost))
                            break
                    # break
                # break
                Agent.save_or_load()
                tqdm.write('Saved @ Global Step: {}, Total Loss: {}'.format(
                    Agent.stats.g_step, Agent.stats.cost
                ))
        # finish stats
        self.P('Total Runtime is {:.1f} mins'.format(float(timer()-runtime)/60))
        return True

    def get_dataset(self, exchange, pair):
        # Main Program.
        coin1, coin2 = pair.split('/')
        df_filename = 'df_{}_{}_{}.csv'.format(exchange, coin1, coin2)
        ss_filename = 'ss_{}_{}_{}.csv'.format(exchange, coin1, coin2)
        dir_path = os.path.dirname(os.path.realpath(__file__))

        # search for previous save files
        if self.options.save_file:
            if os.path.exists(os.path.join(dir_path, 'data', 'datasets', ss_filename)):
                self.P('Loading Saved Superset')
                ss = pd.read_csv(os.path.join(dir_path, 'data', 'datasets', ss_filename))
                self.P('Found {} elements per line'.format(len(ss.loc[0])))
            else:
                self.P('Fetching new Pricedata... This could take up to 21 mins per coin')
                df = self.dataHandler.get_candles(exchange, pair)
                # trunkating df size!!!!
                # df = df[:500]
                df.to_csv(os.path.join(dir_path, 'data', 'datasets', df_filename), index=False, header=True)
                self.P('Creating Superset.')
                start = timer()
                ss = df.superset()
                self.P('Took {:.1f} mins to build superset.'.format(float(timer() - start) / 60))
                ss.to_csv(os.path.join(dir_path, 'data', 'datasets', ss_filename), index=False, header=False)
                if True:
                    self.P('Fixing time in data')
                    start = timer()
                    ft = df.fix_time()
                    self.P('Took {:.1f} mins to build fixed time set.'.format(float(timer() - start) / 60))
                    self.plotter.Plot_me(ft, to_file=True)

        self.P('We have a superset, with a len of {}'.format(len(ss)))
        ss = ss.as_matrix()
        return ss
    """

    def get_megaset(self):
        filename = 'AG_megaset.npy'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if self.options.save_file:
            if os.path.exists(os.path.join(dir_path, 'data', 'datasets', filename)):
                self.P('Loading Saved Superset')
                ss = np.load(os.path.join(dir_path, 'data', 'datasets', filename))
                self.P('Found {} elements per line, and a shape of {}'.format(len(ss[0]), ss.shape))
            else:
                self.P('Fetching new Pricedata... This could take up to an hour.')
                self.P('Please consider sharing your normalized dataset with the community.')
                start = timer()
                ss = self.dataHandler.get_all_dataframes()
                np.save(os.path.join(dir_path, 'data', 'datasets', filename), ss)
                self.P('Took {:.1f} mins to build the Megaset.'.format(float(timer() - start) / 60))
        else:
            start = timer()
            ss = self.dataHandler.get_all_dataframes()
            self.P('Took {:.1f} mins to build fixed time set.'.format(float(timer() - start) / 60))
        return ss


def main():
    """Launcher for the app."""
    if os.path.exists('config/access_codes.yaml'):
        config = options.Options('config/access_codes.yaml')
    else:
        print('\n#| AlphaGriffin - BitTensor |#')
        print(": To begin copy the dummy_codes.yaml file,")
        print(": the one thats in the config folder in this repo.")
        print(': to access_codes.yaml.\n')
        print(": After that, restart this app.")
        exit('AlphaGriffin | 2018')
    app = Bittensor(config)
    if app.main():
        return True
    return False


if __name__ == '__main__':
    try:
        if main():
            print("AlphaGriffin  |  2018")
        else:
            print("Controlled Errors. Good day.")
    except Exception as e:
        print("and thats okay too.")
        log.error(e)
        sys.exit(e)
