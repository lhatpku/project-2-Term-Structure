import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pylab as plt
import os
import sqlite3
from sqlite3 import Error
from term_structure_helper import loadData
import statsmodels.formula.api as sm
from scipy.optimize import minimize


def load_bond():

    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    loc = os.path.join(__location__ + '/Data/bond_prices.db')

    conn = sqlite3.connect(loc)
    bonds_prices = pd.read_sql('select * from bond_prices', conn)

    bond_names = bonds_prices['Ticker'].unique()

    bonds_dict = {}

    for bond_name in bond_names:
        filtered_bond = bonds_prices[bonds_prices['Ticker'] == bond_name]
        filtered_bond = filtered_bond.drop('Ticker', 1)
        bonds_dict[bond_name] = filtered_bond

    return bonds_dict

def get_monthly_return (bonds_dict,ticker):

    bond_price = bonds_dict[ticker].set_index('Date')['Adj_Close']
    bond_price.index = pd.to_datetime(bond_price.index)
    bond_price_monthly = bond_price.resample('MS').mean()
    bond_price_monthly_notna = bond_price_monthly.notna()
    last_notna_index = bond_price_monthly_notna.where(bond_price_monthly_notna==False).last_valid_index()
    bond_price_monthly_clean = bond_price_monthly[bond_price_monthly.index > last_notna_index]

    bond_return_monthly = bond_price_monthly_clean.pct_change(1).dropna()

    return bond_return_monthly

# beta_fits, residuals, ratedata = loadData()

def get_yield_rates(betas,maturity):

    lam_t = .0609
    _load2 = lambda x: (1.-np.exp(-lam_t*x)) / (lam_t*x)
    _load3 = lambda x: ((1.-np.exp(-lam_t*x)) / (lam_t*x)) - np.exp(-lam_t*x)

    betas.index = pd.to_datetime(betas.index)
    betas_monthly = betas.resample('MS').mean()

    # Convert from percent value to actual value
    yield_rates = (betas_monthly['beta1'] + betas_monthly['beta2'] * _load2(maturity) + betas_monthly['beta3'] * _load3(maturity)) / 100

    return yield_rates

def get_zero_coupon_bond_price (betas,maturity):

    yield_rates = get_yield_rates(betas,maturity)

    zc_bond_price = np.exp(- yield_rates * maturity / 12)

    return zc_bond_price

def get_spot_rate (betas,maturity):

    zc_bond_price_bought = get_zero_coupon_bond_price (betas,maturity)
    zc_bond_price_sell = get_zero_coupon_bond_price (betas,maturity-1)

    zc_bond_spot_rate = zc_bond_price_sell / zc_bond_price_bought.shift(periods=1) - 1

    return zc_bond_spot_rate.dropna()

# Use zero coupon bond spot rates to fit ETF bond returns
def fit_bond_return (bonds_dict,ticker,betas,maturity_list,json=0):

    bond_returns = get_monthly_return (bonds_dict,ticker)

    count = 0 

    for maturity in maturity_list:
        if count == 0: 
            zc_bond_rate_df = get_spot_rate(betas,maturity)
        else:
            zc_bond_rate_df = pd.concat([zc_bond_rate_df, get_spot_rate (betas,maturity)], axis=1)
        count = count + 1

    zc_columns = list(map(lambda x: f'YTM-{x}',maturity_list))
    zc_bond_rate_df.columns = zc_columns

    agg_df = zc_bond_rate_df.join(bond_returns, how='inner')

    X = agg_df[zc_columns]
    y = agg_df['Adj_Close']

    def obj_fun(x, y, X):
        count = 0
        for column in X.columns:
            if count == 0: 
                y_ = X[column] * x[count]
            else:
                y_ = y_ + X[column] * x[count]
            count = count + 1

        return np.sum((y-y_)**2)

    bnds = [(0, 1)] * len(maturity_list)
    cons = [{"type": "eq", "fun": lambda x: np.sum(x) - 1}]
    xinit = np.ones(len(zc_columns)) * (1/len(zc_columns))

    res = minimize(fun=obj_fun, args=(y, X), x0=xinit, bounds=bnds, constraints=cons)
    fit_params_list = res.x

    fit_params = []

    for i in range(len(maturity_list)):
        fit_params.append({"maturity":maturity_list[i],"param":fit_params_list[i]})

    y_fit = X.dot(fit_params_list)

    result = {}

    result['params'] = fit_params
    if json == 1:
        y_fit_df = pd.DataFrame({'Date':y_fit.index, 'return':y_fit.values})
        y_df = pd.DataFrame({'Date':y.index, 'return':y.values})
        result['y_fit'] = y_fit_df.to_dict(orient='records')
        result['y'] = y_df.to_dict(orient='records')
    else:
        result['y_fit'] = y_fit
        result['y'] = y

    return result


# bonds_dict = load_bond()
# beta_fits, residuals, ratedata = loadData()

# ETF_short_tickers = ['SHV','VGSH']
# ETF_long_tickers = ['DTYL','TLH']

# maturity_short_list = [3,6,12,24,36,48,60]
# maturity_long_list = [72,84,96,108,120,132,144,156,168,180,192,204,216,228,240]

# ETF_results = {}
# for i_ticker in ETF_short_tickers:
#     print(i_ticker)
#     ETF_results[i_ticker] = fit_bond_return(bonds_dict,i_ticker,beta_fits,maturity_short_list)

# for i_ticker in ETF_long_tickers:
#     print(i_ticker)
#     ETF_results[i_ticker] = fit_bond_return(bonds_dict,i_ticker,beta_fits,maturity_long_list)