import os
import pandas as pd
import numpy as np
from term_structure_helper import loadData, fit_yield_curve, ARforecast
from bond_price_helper import load_bond, fit_bond_return
from sqlalchemy import create_engine
import sqlite3

engine = create_engine('sqlite:///db/agg.sqlite', echo=False)
################### Analysis ###################
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
loc = os.path.join(__location__ + '/Data/bond_prices.db')
conn = sqlite3.connect(loc)
bonds_prices = pd.read_sql('select * from bond_prices', conn)

beta_fits, residuals, ratedata = loadData()

beta_fits.to_sql('betas', con=engine, if_exists='replace')
ratedata.to_sql('ratedata', con=engine, if_exists='replace')
bonds_prices.to_sql('bonds', con=engine, if_exists='replace')

# bonds_prices = pd.read_sql('select * from bonds', con=engine)
# print(bonds_prices.set_index('Date'))

###############################
# Save sp and gdp data
def sp500_data():
    database = 'Data/sp500_return.db'
    conn = sqlite3.connect(database)

    returns = pd.read_sql('select * from rolling_returns', conn)
    returns.to_sql('sp500', con=engine, if_exists='replace')

def gdp_data():
    database = 'Data/gdp.db'
    conn = sqlite3.connect(database)
    
    gdp = pd.read_sql('select * from quarterly_growth_rate', conn)
    gdp.to_sql('gdp', con=engine, if_exists='replace')


sp500_data()
gdp_data()