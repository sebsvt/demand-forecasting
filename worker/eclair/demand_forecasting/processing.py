import pandas as pd
import numpy as np

# def extract_data_by_column_name_and_group_by_date(data: pd.DataFrame, datetime_column: str, column: str, filter_value: str, y: str) -> pd.DataFrame:
# 	filtered_df = data[data[column] == filter_value]
# 	grouped_df = filtered_df.groupby([datetime_column])[y].sum().reset_index()
# 	grouped_df = grouped_df.rename(columns={datetime_column: 'ds', y: 'y'})
# 	return grouped_df

def extract_data_by_item_name_and_group_by(data: pd.DataFrame, datetime_column: str, column: str, filter_value: str, y: str) -> pd.DataFrame:
	filtered_df = data[data[column] == filter_value]
	grouped_df = filtered_df.groupby([datetime_column])[y].sum().reset_index()
	grouped_df = grouped_df.rename(columns={datetime_column: 'ds', y: 'y'})
	return grouped_df

def detection_and_delete_outlier_by_quatile(data: pd.DataFrame, column: str) -> pd.DataFrame:
	stat = data[column].describe()
	Q1 = stat['25%']
	# Q2 = stat['50%']  # Median (not used for outlier detection here, but calculated)
	Q3 = stat['75%']
	IQR = Q3 - Q1

	# Define the lower and upper bounds for outliers
	lower_bound = Q1 - (1.5 * IQR)
	upper_bound = Q3 + (1.5 * IQR)

	# Filter the DataFrame to remove outliers
	filtered_data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]

	return filtered_data

def detection_and_delete_outlier_by_std(data: pd.DataFrame, column: str, num_std: float = 3.0):
	"""
	Delete rows in the DataFrame where the values in the specified column are
	more than 'num_std' standard deviations away from the mean.

	:param data: The input DataFrame.
	:param column: The column to check for outliers.
	:param num_std: The number of standard deviations from the mean to use as the threshold.
	:return: The DataFrame with outliers removed.
	"""
	mean = data[column].mean()
	std_dev = data[column].std()

	# Define the lower and upper bounds for outliers
	lower_bound = mean - (num_std * std_dev)
	upper_bound = mean + (num_std * std_dev)

	# Filter the DataFrame to remove outliers
	filtered_data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]

	return filtered_data

def detection_and_delete_outlier_by_std(data: pd.DataFrame, column: str, num_std: float = 3.0):
	"""
	Delete rows in the DataFrame where the values in the specified column are
	more than 'num_std' standard deviations away from the mean.

	:param data: The input DataFrame.
	:param column: The column to check for outliers.
	:param num_std: The number of standard deviations from the mean to use as the threshold.
	:return: The DataFrame with outliers removed.
	"""
	mean = data[column].mean()
	std_dev = data[column].std()

	# Define the lower and upper bounds for outliers
	lower_bound = mean - (num_std * std_dev)
	upper_bound = mean + (num_std * std_dev)

	# Filter the DataFrame to remove outliers
	filtered_data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]

	return filtered_data
