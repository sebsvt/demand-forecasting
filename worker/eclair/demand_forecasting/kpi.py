import pandas as pd
import numpy as np

def forecast_kpi(df: pd.DataFrame):
	kpis = {}
	demand_avg = df.loc[df['Error'].notnull(), 'Demand'].mean()

	bias_abs = df['Error'].mean()
	bias_rel = bias_abs/demand_avg
	kpis['bias_rel'] = bias_rel

	MAPE = (df['Error'].abs()/df['Demand']).mean()
	kpis['mape'] = round(MAPE, 2)

	MAE_abs = df['Error'].abs().mean()
	MAE_rel = MAE_abs / demand_avg
	kpis['mae'] = round(MAE_rel, 2)

	RMSE_abs = np.sqrt((df["Error"] ** 2).mean())
	RMSE_rel = RMSE_abs / demand_avg
	kpis['rmse'] = round(RMSE_rel, 2)

	return kpis
