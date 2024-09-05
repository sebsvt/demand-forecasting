from prophet import Prophet
import pandas as pd

def prophet_forecasting_model(data: pd.DataFrame, periods: int = 1, freq: str = 'D') -> pd.DataFrame:
	model = Prophet()

	model.fit(data)

	future = model.make_future_dataframe(periods=periods, freq=freq)

	forecast = model.predict(future)

	forecast['yhat'] = forecast['yhat'].clip(lower=0)
	forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0)
	forecast['yhat_upper'] = forecast['yhat_upper'].clip(lower=0)

	return pd.DataFrame({
		'Date': forecast['ds'].dt.date.astype('string'),
		'Demand': data['y'].astype('float64'),
		'Forecast': forecast['yhat'].astype('float64'),
		'ForecastLower': forecast['yhat_lower'].astype('float64'),
		'ForecastUpper': forecast['yhat_upper'].astype('float64'),
		'Error': (data['y'] - forecast['yhat']).astype('float64')
	})
