import pandas as pd
import numpy as np

def moving_average_model(demand: list[int | float], extra_periods: int = 1, n=3) -> pd.DataFrame:
	# Historical periods length
	cols = len(demand)
	# append future times
	demand = np.append(demand, [np.nan] * extra_periods)
	# create forecasting array which fill with NaN
	f = np.full(cols + extra_periods, np.nan)

	for t in range(n, cols):
		f[t] = np.mean(demand[t-n:t])

	f[t+1:] = np.mean(demand[t-n+1:t+1])
	df = pd.DataFrame.from_dict({"Demand": demand, "Forecast": f, "Error": demand-f})
	return df

def simple_exponential_smoothing_model(demand: list[int | float], extra_periods=1, alpha=0.4) -> pd.DataFrame:
	cols = len(demand)

	demand = np.append(demand, [np.nan] * extra_periods)
	forecast = np.full(cols+extra_periods, np.nan)
	forecast[1] = demand[0]

	for t in range(2, cols+1):
		forecast[t] = alpha*demand[t-1] +(1-alpha)*forecast[t-1]

	for t in range(cols + 1, cols + extra_periods):
		forecast[t] = forecast[t-1]

	df = pd.DataFrame.from_dict({'Demand': demand, "Forecast": forecast, 'Error': demand-forecast})

	return df

def double_exponential_smoothing_model(d, extra_periods=1, alpha=0.4, beta=0.4) -> pd.DataFrame:
	# Historical period length
	cols = len(d)
	# Append np.nan into the demand array to cover future periods
	d = np.append(d,[np.nan]*extra_periods)

	# Creation of the level, trend and forecast arrays
	f,a,b = np.full((3,cols+extra_periods),np.nan)

	# Level & Trend initialization
	a[0] = d[0]
	b[0] = d[1] - d[0]

	# Create all the t+1 forecast
	for t in range(1,cols):
		f[t] = a[t-1] + b[t-1]
		a[t] = alpha*d[t] + (1-alpha)*(a[t-1]+b[t-1])
		b[t] = beta*(a[t]-a[t-1]) + (1-beta)*b[t-1]

	# Forecast for all extra periods
	for t in range(cols,cols+extra_periods):
		f[t] = a[t-1] + b[t-1]
		a[t] = f[t]
		b[t] = b[t-1]

	df = pd.DataFrame.from_dict({'Demand':d,'Forecast':f,'Level':a,'Trend':b,'Error':d-f})

	return df

def damped_double_smoothing_model(d, extra_periods=1, alpha=0.4, beta=0.4, phi=0.9) -> pd.DataFrame:
	cols = len(d) # Historical period length
	d = np.append(d,[np.nan]*extra_periods) # Append np.nan into

	f,a,b = np.full((3,cols+extra_periods),np.nan)

	a[0] = d[0]
	b[0] = d[1] - d[0]

	for t in range(1,cols):
		f[t] = a[t-1] + phi*b[t-1]
		a[t] = alpha*d[t] + (1-alpha)*(a[t-1]+phi*b[t-1])
		b[t] = beta*(a[t]-a[t-1]) + (1-beta)*phi*b[t-1]

	for t in range(cols,cols+extra_periods):
		f[t] = a[t-1] + phi*b[t-1]
		a[t] = f[t]
		b[t] = phi*b[t-1]

	df = pd.DataFrame.from_dict({'Demand':d,'Forecast':f,'Level':a, 'Trend':b, 'Error':d-f})

	return df

def exponential_smoothing_optimization(d, extra_periods=6):
	params = []
	KPIs = []
	dfs = []

	for alpha in [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
		df = simple_exponential_smoothing_model(d, extra_periods=extra_periods, alpha=alpha)
		params.append(f'Simple Smoothing, alpha: {alpha}')
		dfs.append(df)
		# MAE = df['Error'].abs().mean()
		RMSE = np.sqrt((df["Error"] ** 2).mean())
		KPIs.append(RMSE)

		for beta in [0.05, 0.1, 0.2, 0.3, 0.4]:
			df = double_exponential_smoothing_model(d, extra_periods=extra_periods, alpha=alpha, beta=beta)
			params.append(f'Double Smoothing, alpha: {alpha}, beta: {beta}')
			dfs.append(df)
			RMSE = np.sqrt((df["Error"] ** 2).mean())
			KPIs.append(RMSE)

	mini = np.argmin(KPIs)
	print(f'Best solution found for {params[mini]} RMSE of', round(KPIs[mini], 2))
