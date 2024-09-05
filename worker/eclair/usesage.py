from .demand_forecasting.models.statistics import simple_exponential_smoothing_model
from .demand_forecasting.models.machine_learning import prophet_forecasting_model
from .demand_forecasting.kpi import forecast_kpi
from .demand_forecasting.processing import extract_data_by_item_name_and_group_by, detection_and_delete_outlier_by_quatile, detection_and_delete_outlier_by_std
import pandas as pd

	# df = pd.read_csv('./pure_data.csv')
def demand_forecaste_next_day_from_the_last_date(data: pd.DataFrame, datetime_col: str, demand_type_col: str, filter_by: str, demand: str):
	data_frame = extract_data_by_item_name_and_group_by(
		data=data,
		datetime_column=datetime_col,
		column=demand_type_col,
		filter_value=filter_by,
		y=demand
	)
	# data_frame = detection_and_delete_outlier_by_std(data_frame, 'y')
	demand_forecast = prophet_forecasting_model(data=data_frame, periods=1)
	kpis = forecast_kpi(demand_forecast)
	return {
		'name': filter_by,
		"from_last_date": data[datetime_col].max(),
		"predicted_demand": [{
			"future_date": demand_forecast['Date'].tail(1).values[0],
			"demand": demand_forecast['Forecast'].tail(1).values[0],
		}],
		"kpis": kpis
	}

