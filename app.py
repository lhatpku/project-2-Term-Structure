import os
import pandas as pd
import numpy as np
from flask import Flask, jsonify, render_template
from term_structure_helper import loadData, fit_yield_curve, ARforecast
from bond_price_helper import load_bond, fit_bond_return
from sqlalchemy import create_engine

app = Flask(__name__)

################## Data Prepare ######################
engine = create_engine('sqlite:///db/agg.sqlite', echo=False)

bonds_prices = pd.read_sql('select * from bonds', con=engine)
bonds_dict = load_bond(bonds_prices)

ratedata = pd.read_sql('select * from ratedata', con=engine)
ratedata.set_index('Date',inplace=True)

beta_fits = pd.read_sql('select * from betas', con=engine)
beta_fits.set_index('Date',inplace=True)

sp500_df = pd.read_sql('select * from sp500', con=engine)
gdp_df = pd.read_sql('select * from gdp', con=engine)

maturities_fit = np.asarray([1,2,3,6,12,24,36,60,84,120,240,360]) 

################## Routes ######################
@app.route("/")
def index():
    materities_html = []
    for maturity in maturities_fit:
        materities_html.append({"value":f"{maturity}","text":f"{maturity}"})
    return render_template("index.html",maturities = materities_html)

@app.route("/3d")
def chart_3d():
    """Return the 3d chart page."""
    return render_template("chart_3d.html")

@app.route("/monthly_yields")
def yields_monthly():
    """Return the yields to plot"""
    beta_fits_monthly = beta_fits.resample('MS').mean()
    monthly_data = fit_yield_curve(beta_fits_monthly, maturities_fit)
    monthly_data = monthly_data.reset_index()
    return monthly_data.to_json(orient='records')


@app.route("/yields")
def yields():
    """Return the yields to plot"""
    yield_forecast,beta_forecast = ARforecast(ratedata, beta_fits, 240)
    beta_all = pd.concat([beta_fits,beta_forecast],axis=0)
    yield_fits = fit_yield_curve(beta_all,maturities_fit)
    yield_fits.reset_index(inplace = True)
    # Return a list of the column names (sample names)
    return yield_fits.to_json(orient='records')


@app.route("/betas")
def betas():
    """Return Fitting Information"""
    beta_fits_plot = pd.concat([beta_fits, ratedata], axis=1, join_axes=[beta_fits.index])
    beta_fits_plot_reset = beta_fits_plot.reset_index()
    # Return a list of the column names (sample names)
    return beta_fits_plot_reset.to_json(orient='records')

@app.route("/betas_all")
def betas_all():
    """Return Prediction Information"""
    yield_forecast,beta_forecast = ARforecast(ratedata, beta_fits, 240)
    beta_all = pd.concat([beta_fits,beta_forecast],axis=0)
    beta_all_output = beta_all.reset_index()
    # Return a list of the column names (sample names)
    return beta_all_output.to_json(orient='records')

@app.route("/bonds_fit")
def bonds_fit():
    """Bond Fitting"""
    ETF_short_tickers = ['SHV','VGSH']
    ETF_long_tickers = ['TLH']
    maturity_short_list = [3,6,12,24,36,48,60]
    maturity_long_list = [72,84,96,108,120,132,144,156,168,180,192,204,216,228,240]

    ETF_results = {}
    for i_ticker in ETF_short_tickers:
        ETF_results[i_ticker] = fit_bond_return(bonds_dict,i_ticker,beta_fits,maturity_short_list,1)

    for i_ticker in ETF_long_tickers:
        ETF_results[i_ticker] = fit_bond_return(bonds_dict,i_ticker,beta_fits,maturity_long_list,1)

    return jsonify(ETF_results)

@app.route("/annual_yields")
def yields_annual():
    beta_fits_plot = pd.concat([beta_fits, ratedata], axis=1, join_axes=[beta_fits.index])
    beta_fits_plot_reset = beta_fits_plot.reset_index()
    records=beta_fits_plot_reset.to_dict('records')
    lam_t = .0609
    maturities_output = list(range(3,363,6))

    yield_rates=[]
    maturity=[]
    date=[]

    for item in records:
         for y in maturities_output:
              load2 = (1. - np.exp(-lam_t*y)) / (lam_t*y)
              load3 = ((1.- np.exp(-lam_t*y)) / (lam_t*y)) - np.exp(-lam_t*y)

              yield_rate = item['beta1'] + item['beta2'] * load2 + item['beta3'] * load3

              yield_rates.append(yield_rate)
              maturity.append(y)
              date.append(item['Date'])

    df=pd.DataFrame({'yield_rates':yield_rates, 'maturity': maturity, 'Date':pd.to_datetime(date)})

    df['Date']=df['Date'].dt.to_period('Y')

    gb=df.groupby(['maturity','Date']).mean()
    df1=gb.reset_index()

    return df1.to_json(orient='records')


@app.route('/sp500')
def sp500():
    """Returns the annualized returns for S&P500 return"""
    return sp500_df.to_json(orient='records')


@app.route('/gdp')
def gdp():
     """Returns annualized quarterly growth rate in GDP"""

     return gdp_df.to_json(orient='records')


if __name__ == "__main__":
    app.run()
