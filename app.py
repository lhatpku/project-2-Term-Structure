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

app = Flask(__name__)

beta_fits, residuals, ratedata = loadData()
yield_forecast,beta_forecast = ARforecast(ratedata, beta_fits, 240)

beta_all = pd.concat([beta_fits,beta_forecast],axis=0)

maturities_fit = np.asarray([1,2,3,6,12,24,36,60,84,120,240,360]) 
materities_html = []

for maturity in maturities_fit:
     materities_html.append({"value":f"{maturity}","text":f"{maturity}"})


@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html",maturities = materities_html)
    
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

if __name__ == "__main__":
    app.run()
