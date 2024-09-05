from eclair.usesage import demand_forecaste_next_day_from_the_last_date
from pymongo import MongoClient
from dotenv import load_dotenv
import os, json, pika
import pandas as pd


# Load environment variables from .env file
load_dotenv()

# Retrieve RabbitMQ connection details from environment variables
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_USER = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_QUEUE = "demand_forecast_tasks"


def connect_to_rabbitmq():
	"""Establish connection to RabbitMQ and declare the queue."""
	credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
	connection = pika.BlockingConnection(
		pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
	)
	channel = connection.channel()
	channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
	return channel

def load_data_from_database(partner_id: str) -> pd.DataFrame:
	client = MongoClient("mongodb://root:example@89.213.177.102:27017/")
	db = client["aiselena_logistic"]
	collection = db["logistic_transactions"]
	transaction = list(collection.find({"partner_id": partner_id}, {
		"time_stamp": 1,
		"consignee.state": 1,
		"package_item.item_name": 1,
		"package_item.item_description": 1,
		"package_item.unit": 1,
		"package_item.quantity": 1,
	}))
	df = pd.json_normalize(transaction)
	return df

def update_demand_forecast_in_db(forecast_id, prediction):
	"""Update the demand forecast item in MongoDB."""
	client = MongoClient("mongodb+srv://vithchatayasaharat:4gDwprHyrAQeX3!@cluster0.hmyqrhd.mongodb.net")
	db = client["aiselena"]
	collection = db["demand_forecast"]

	# Update the forecast with the new prediction
	filter_query = {"forecast_id": forecast_id}
	update_query = {
		"$push": {
			"demand_forecast_item": {
				"name": prediction['name'],
				"from_last_date": prediction['from_last_date'],
				"predictions": prediction['predicted_demand'],
				"kpi": prediction['kpis']
			}
		},
		"$set": {
			"status": "completed"# Set the new status
        }
	}

	result = collection.update_one(filter_query, update_query)
	if result.matched_count == 0:
		print(f"Forecast with ID {forecast_id} not found")
	else:
		print(f"Updated forecast with ID {forecast_id}")

def do_work(data):
	"""Perform demand forecasting and show the top N most frequent items."""
	try:
		forecast_id = data.get("forecast_id")
		partner_id = data.get("partner_id")
		top_n = int(data.get("number_of_item"))
		# Load data from the database
		df = load_data_from_database(partner_id)
		if df.empty:
			raise Exception("data is empty")

		# Calculate the frequency of each item
		top_items = df['package_item.item_name'].value_counts().head(top_n)
		item_names = top_items.index.tolist()
		#Demand forecasting part

		for item in item_names:
			result = demand_forecaste_next_day_from_the_last_date(
				data=df,
				datetime_col="time_stamp",
				demand_type_col="package_item.item_name",
				filter_by=item,
				demand="package_item.quantity"
			)
			# result from prediction
			update_demand_forecast_in_db(forecast_id, result)
			print(f"Demand Forecast: {result}")
	except Exception as error:
		print(f"Error: {error}")
		return {"error": str(error)}


def callback(ch, method, properties, body):
	"""Callback function to process messages from the queue."""
	print(f" [x] Received {body.decode()}")
	data = json.loads(body.decode())
	do_work(data)
	print(" [x] Done")
	ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
	"""Main function to start consuming messages."""
	channel = connect_to_rabbitmq()
	print(' [*] Waiting for messages. To exit press CTRL+C')
	channel.basic_qos(prefetch_count=1)
	channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
	channel.start_consuming()

if __name__ == "__main__":
	main()

