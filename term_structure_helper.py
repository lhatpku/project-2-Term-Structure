import pandas as pd
from numpy import *
import statsmodels.api as sm
import matplotlib.pylab as plt
import datetime as dt
from sklearn import linear_model
import scipy
import os
import sqlite3
from sqlite3 import Error
import warnings
import itertools
from dateutil.relativedelta import *

warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')

# matplotlib.rcParams['axes.labelsize'] = 14
# matplotlib.rcParams['xtick.labelsize'] = 12
# matplotlib.rcParams['ytick.labelsize'] = 12
# matplotlib.rcParams['text.color'] = 'k'

# py.tools.set_credentials_file(username='lhatpku', api_key='IQ9S1tothSzT9TmjMwnX')

maturities = asarray([1,2,3,6,12,24,36,60,84,120,240,360])
beta_names = ['beta1', 'beta2', 'beta3']
lam_t = .0609
_load2 = lambda x: (1.-exp(-lam_t*x)) / (lam_t*x)
_load3 = lambda x: ((1.-exp(-lam_t*x)) / (lam_t*x)) - exp(-lam_t*x)

##################
# Notes: Update using the sql database
# Read in the data and calculate beta0, beta1, beta2 along the historical horizon

def loadData():

    lam_t = .0609
    # filter where we only get the last day of every month
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    loc = os.path.join(__location__ + '/Data/treasury_yield.db')

    conn = sqlite3.connect(loc)
    ratedata = pd.read_sql('select * from treasury_yield', conn)

    lam_t = .0609
    _load2 = lambda x: (1.-exp(-lam_t*x)) / (lam_t*x)
    _load3 = lambda x: ((1.-exp(-lam_t*x)) / (lam_t*x)) - exp(-lam_t*x)
    ratedata = ratedata.drop('id', axis=1)

    ratedata = ratedata.set_index('Date')

    # make 2D matrix of all of the beta coeff. for each maturity
    X = zeros((len(maturities), 2))
    X[:,0] = _load2(maturities)
    X[:,1] = _load3(maturities)
    X = sm.add_constant(X)

    # for each observation, fit the maturity curve
    beta_fits = zeros((len(ratedata), 3))
    residuals = zeros((len(ratedata), len(maturities)))

    for i in range(0, len(ratedata)):

        ratedata_index = (ratedata.iloc[i].isnull()==0)
        ratedata_select = ratedata.iloc[i][ratedata_index]
        X = zeros((len(ratedata_select), 2))
        X[:,0] = _load2(maturities)[ratedata_index]
        X[:,1] = _load3(maturities)[ratedata_index]
        X = sm.add_constant(X)
        model = sm.regression.linear_model.OLS(ratedata_select, X)
        results = model.fit()
        beta_fits[i,:3] = results.params
        residuals[i,:][ratedata_index] = results.resid

    # convert into a dataframe for conv.
    beta_fits = pd.DataFrame(beta_fits, columns=beta_names)
    residuals = pd.DataFrame(residuals, columns=[str(mat) for mat in maturities])

    beta_fits.index = ratedata.index
    residuals.index = ratedata.index

    return beta_fits, residuals, ratedata

def fit_yield_curve(beta_fits,maturities):

    lam_t = .0609
    _load2 = lambda x: (1.-exp(-lam_t*x)) / (lam_t*x)
    _load3 = lambda x: ((1.-exp(-lam_t*x)) / (lam_t*x)) - exp(-lam_t*x)

    yield_fits = pd.DataFrame(zeros((len(beta_fits),len(maturities))),index=beta_fits.index,columns=list( map(str, maturities)))

    for i in range(0, len(beta_fits)):
        beta_array = beta_fits.iloc[i]
        yield_fits.ix[i,:] = beta_array[0] + beta_array[1] * _load2(maturities) + beta_array[2] * _load3(maturities)

    return yield_fits



def table2(residuals):
	table2 = zeros((len(maturities), 9)) # initialize a matrix
	table2 = pd.DataFrame(table2, index=[str(mat) for mat in maturities])
	table2.columns = ['Mean', 'Std', 'Min', 'Max', 'MAE', 'RMSE', 'ACF(1)', 'ACF(12)', 'ACF(30)']
	for mat in maturities:
		table2.ix[str(mat), 0] = residuals.ix[:,str(mat)].mean()
		table2.ix[str(mat), 1] = residuals.ix[:,str(mat)].std()
		table2.ix[str(mat), 2] = residuals.ix[:,str(mat)].min()
		table2.ix[str(mat), 3] = residuals.ix[:,str(mat)].max()
		table2.ix[str(mat), 4] = abs(residuals.ix[:,str(mat)]).mean() # MAE
		table2.ix[str(mat), 5] = sqrt(pow(residuals.ix[:,str(mat)],2).mean())
		table2.ix[str(mat), 6] = sm.tsa.stattools.acf(residuals.ix[:,str(mat)], nlags=31)[1]
		table2.ix[str(mat), 7] = sm.tsa.stattools.acf(residuals.ix[:,str(mat)], nlags=31)[13]
		table2.ix[str(mat), 8] = sm.tsa.stattools.acf(residuals.ix[:,str(mat)], nlags=31)[-1]

	return table2


def table3(beta_fits):
	table3 = pd.DataFrame(zeros((3, 8)), index=beta_names)
	table3_columns = ['Mean', 'Std', 'Min', 'Max', 'ACF(1)', 'ACF(12)', 'ACF(30)', 'ADF']
	table3.columns = table3_columns
	for beta in beta_names:
		table3.ix[beta, 0] = beta_fits.ix[:,beta].mean()
		table3.ix[beta, 1] = beta_fits.ix[:,beta].std()
		table3.ix[beta, 2] = beta_fits.ix[:,beta].min()
		table3.ix[beta, 3] = beta_fits.ix[:,beta].max()
		table3.ix[beta, 4] = sm.tsa.stattools.acf(beta_fits.ix[:, beta], nlags=31)[1]
		table3.ix[beta, 5] = sm.tsa.stattools.acf(beta_fits.ix[:, beta], nlags=31)[13]
		table3.ix[beta, 6] = sm.tsa.stattools.acf(beta_fits.ix[:, beta], nlags=31)[-1]
		table3.ix[beta, -1] = sm.tsa.adfuller(beta_fits.ix[:,beta])[0] # note the ADF assumes [maxlag = 12*(nobs/100)^.25]

	return table3

def perDone(i, length, goal):
	if i != 0:
		if (float(i)/length) *100 > goal:
			print("{}% done".format(goal))
			return 10.
		else:
			return 0
	else: 
		return 0

def ARforecast_analysis(ratedata, beta_fits):

	ratedata.index = pd.to_datetime(ratedata.index)
	ratedata_m = ratedata.resample('MS').mean()

	beta_fits.index = pd.to_datetime(beta_fits.index)
	beta_fits_m = beta_fits.resample('MS').mean()

	N_out = len(ratedata_m.index) - 100 # N out of sample

	beta_predict_nieve = pd.DataFrame(zeros((N_out, 3)), index=beta_fits_m.index[100:], columns=beta_fits_m.columns)

	yield_forecast_nieve = pd.DataFrame(zeros((N_out, len(ratedata_m.columns))), index=beta_fits_m.index[100:], columns=ratedata_m.columns)

	beta_predict_random = pd.DataFrame(zeros((N_out, 3)), index=beta_fits_m.index[100:], columns=beta_fits_m.columns)

	yield_forecast_random =  pd.DataFrame(zeros((N_out, len(ratedata_m.columns))), index=beta_fits_m.index[100:], columns=ratedata_m.columns)

	# for each date in the withheld series
	d = 10.
	i = 0
	
	for date in range(0,N_out):

		d_updt = perDone(date,N_out,d)
		d = d_updt + d
		now = date + 100 # step each turn to fit
		for beta in beta_fits_m.columns:

			model = sm.tsa.AR(beta_fits_m.ix[:now,beta]).fit(maxlag=1,method='cmle')
			try:
				beta_predict_nieve.ix[date, beta] = model.predict(len(beta_fits_m.ix[:now,beta])-1,len(beta_fits_m.ix[:now,beta])).iloc[-1]
				beta_predict_random.ix[date, beta] = beta_fits_m.ix[now-1,beta]+(beta_fits_m.ix[now-1,beta].std())*random.randn()

			except KeyError:
				pdb.set_trace()

		try:

			yield_forecast_nieve.ix[date,:] = beta_predict_nieve.ix[date, 'beta1'] + \
	            beta_predict_nieve.ix[date, 'beta2']*_load2(asarray(maturities)) +\
	            beta_predict_nieve.ix[date, 'beta3']*_load3(asarray(maturities))
	            

			yield_forecast_random.ix[date,:] = beta_predict_random.ix[date, 'beta1'] + \
	            beta_predict_random.ix[date, 'beta2']*_load2(asarray(maturities)) +\
	            beta_predict_random.ix[date, 'beta3']*_load3(asarray(maturities))
	            

		except TypeError:
			pdb.set_trace()
	        
		i = i +1

	return yield_forecast_nieve, yield_forecast_random


def ARforecast(ratedata, beta_fits, N_out):

	ratedata.index = pd.to_datetime(ratedata.index)
	ratedata_m = ratedata.resample('MS').mean()

	beta_fits.index = pd.to_datetime(beta_fits.index)
	beta_fits_m = beta_fits.resample('MS').mean()

	yield_forecast_nieve = pd.DataFrame(zeros((N_out, len(ratedata_m.columns))),  columns=ratedata_m.columns)

	predict_delta_start = relativedelta(months=+1)
	predict_delta_end = relativedelta(months=+N_out)

	predict_start = predict_delta_start + pd.to_datetime(beta_fits_m.index[-1])
	predict_end = predict_delta_end + pd.to_datetime(beta_fits_m.index[-1])

	beta_predict_raw = {}

	for beta in beta_fits_m.columns:
		model = sm.tsa.AR(beta_fits_m.ix[:,beta]).fit(maxlag=1,method='cmle')
		beta_predict_raw[beta] = model.predict(start=predict_start,end=predict_end,dynamic=False).iloc[:]

	beta_predict_nieve = pd.DataFrame(beta_predict_raw)


	for i in range(len(yield_forecast_nieve)): 
		yield_forecast_nieve.ix[i,:] = beta_predict_nieve.ix[i, 'beta1'] + \
			beta_predict_nieve.ix[i, 'beta2']*_load2(asarray(maturities)) +\
			beta_predict_nieve.ix[i, 'beta3']*_load3(asarray(maturities))

	yield_forecast_nieve.index = beta_predict_nieve.index

	yield_forecast_nieve.index.name = "Date"
	beta_predict_nieve.index.name = "Date"

	return yield_forecast_nieve, beta_predict_nieve
		


def ARIMA_forecast (beta_series):

	beta_series.index = pd.to_datetime(beta_series.index)

	beta_series_m = beta_series.resample('MS').mean()
	# beta_series_m.plot(figsize=(15, 6))
	# plt.show()

	# ARIMA Parameters
	p = d = q = range(0, 2)
	pdq = list(itertools.product(p, d, q))
	seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]

	result_list = []
	aic_list = []

	for param in pdq:
		for param_seasonal in seasonal_pdq:
			try:
				mod = sm.tsa.statespace.SARIMAX(beta_series_m,\
                                            order=param,\
                                            seasonal_order=param_seasonal,\
                                            enforce_stationarity=False,\
                                            enforce_invertibility=False)
				results = mod.fit()
				print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
				result_list.append({'param':param,'param_seasonal':param_seasonal,'aic':results.aic})
				aic_list.append(results.aic)
			except:
				continue

	select_result = list(filter(lambda x: x['aic'] == min(aic_list),result_list))[0]

	mod = sm.tsa.statespace.SARIMAX(beta_series_m,\
                                order = select_result['param'],\
                                seasonal_order = select_result['param_seasonal'],\
                                enforce_stationarity=False,\
                                enforce_invertibility=False)
	results = mod.fit()

	# results.plot_diagnostics(figsize=(16, 8))
	# plt.show()
	pred_uc = results.get_forecast(steps=100)
	pred_ci = pred_uc.conf_int()
	ax = beta_series_m.plot(label='observed', figsize=(14, 7))
	pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
	ax.fill_between(pred_ci.index,
					pred_ci.iloc[:, 0],
					pred_ci.iloc[:, 1], color='k', alpha=.25)
	ax.set_xlabel('Date')
	ax.set_ylabel('beta_prediction')

	plt.legend()
	plt.show()


# beta_fits, residuals, ratedata = loadData()
# yield_forecast,beta_forecast = ARforecast(ratedata, beta_fits, 240)


# ARIMA_forecast (beta_fits['beta2'])