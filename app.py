import os
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from term_structure_helper import loadData, fit_yield_curve

app = Flask(__name__)

beta_fits, residuals, ratedata = loadData()

maturities_fit = np.asarray([1,2,3,6,12,24,36,60,84,120,240,360]) 
materities_html = []

for maturity in maturities_fit:
    materities_html.append({"value":f"{maturity}","text":f"YTM - {maturity}"})


@app.route("/")
def chart():
    """Return the homepage."""
    return render_template("3d_chart.html",maturities = materities_html)


@app.route("/yields")
def yields():
    """Return a list of sample names."""

    yield_fits = fit_yield_curve(beta_fits,maturities_fit)
    yield_fits.reset_index(inplace = True)
    # Return a list of the column names (sample names)
    return yield_fits.to_json(orient='records')

@app.route("/betas")
def betas():
    beta_fits_reset = beta_fits.reset_index()
    # Return a list of the column names (sample names)
    return beta_fits_reset.to_json(orient='records')


@app.route("/monthly_yields")
def yields_monthly():
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
               load2 = (1. - math.exp(-lam_t*y)) / (lam_t*y);
               load3 = ((1.- math.exp(-lam_t*y)) / (lam_t*y)) - math.exp(-lam_t*y);

               yield_rate = item['beta1'] + item['beta2'] * load2 + item['beta3'] * load3;

               yield_rates.append(yield_rate)
               maturity.append(y)
               date.append(item['Date'])

     df=pd.DataFrame({'yield_rates':yield_rates, 'maturity': maturity, 'Date':pd.to_datetime(date)})

     df['Date']=df['Date'].dt.to_period('Y')

     gb=df.groupby(['maturity','Date']).mean()
     df1=gb.reset_index()

     return df1.to_json(orient='records')

if __name__ == "__main__":
    app.run()
