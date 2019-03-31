import os
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

from term_structure_helper import loadData, fit_yield_curve, ARforecast
from bond_price_helper import load_bond, fit_bond_return

app = Flask(__name__)

################### Analysis ###################
beta_fits, residuals, ratedata = loadData()
bonds_dict = load_bond()

ETF_short_tickers = ['SHV','VGSH']
ETF_long_tickers = ['TLH']

maturity_short_list = [3,6,12,24,36,48,60]
maturity_long_list = [72,84,96,108,120,132,144,156,168,180,192,204,216,228,240]

ETF_results = {}
for i_ticker in ETF_short_tickers:
    ETF_results[i_ticker] = fit_bond_return(bonds_dict,i_ticker,beta_fits,maturity_short_list,1)

for i_ticker in ETF_long_tickers:
    ETF_results[i_ticker] = fit_bond_return(bonds_dict,i_ticker,beta_fits,maturity_long_list,1)

yield_forecast,beta_forecast = ARforecast(ratedata, beta_fits, 240)
################## Data Prepare ######################
beta_all = pd.concat([beta_fits,beta_forecast],axis=0)

maturities_fit = np.asarray([1,2,3,6,12,24,36,60,84,120,240,360]) 
materities_html = []

for maturity in maturities_fit:
     materities_html.append({"value":f"{maturity}","text":f"{maturity}"})

################## Routes ######################
@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html",maturities = materities_html)

@app.route("/3d")
def chart_3d():
    """Return the 3d chart page."""
    return render_template("chart-3d.html")

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
    beta_all_output = beta_all.reset_index()
    # Return a list of the column names (sample names)
    return beta_all_output.to_json(orient='records')

@app.route("/bonds_fit")
def bonds_fit():
    """Bond Fitting"""
    return jsonify(ETF_results)

if __name__ == "__main__":
    app.run()
