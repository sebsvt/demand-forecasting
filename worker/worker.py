from eclair.usesage import demand_forecaste_next_day_from_the_last_date
from pymongo import MongoClient
from dotenv import load_dotenv
import os, json, pika
import pandas as pd


# Load environment variables from .env file
load_dotenv()

class RabbitMQConnectionManager:
	def __init__(self, host: str, user: str, password: str, queue: str):
		self.host = host
		self.user = user
		self.password = password
		self.queue = queue
		self.connection = None
		self.channel = None

	def connect(self):
		"""Establish connection to RabbitMQ and declare the queue."""
		credentials = pika.PlainCredentials(self.user, self.password)
		self.connection = pika.BlockingConnection(
			pika.ConnectionParameters(host=self.host, credentials=credentials)
		)
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue=self.queue, durable=True)
		return self.channel

	def close(self):
		"""Close the RabbitMQ connection."""
		if self.connection:
			self.connection.close()

class MongoDBConnectionManager:
	def __init__(self, uri: str):
		self.client = MongoClient(uri)
		self.db = None

	def select_database(self, db_name: str):
		"""Select the database."""
		self.db = self.client[db_name]

	def get_collection(self, collection_name: str):
		"""Get a collection from the database."""
		if not self.db:
			raise ValueError("Database not selected")
		return self.db[collection_name]

class DemandForecastingService:
	def __init__(self, mongo_uri: str, forecast_db_name: str, transactions_db_name: str):
		self.mongo_manager = MongoDBConnectionManager(mongo_uri)
		self.mongo_manager.select_database(forecast_db_name)
		self.transactions_db = MongoDBConnectionManager(mongo_uri)
		self.transactions_db.select_database(transactions_db_name)

	def load_data(self, partner_id: str) -> pd.DataFrame:
		collection = self.transactions_db.get_collection("logistic_transactions")
		transaction = list(collection.find({"partner_id": partner_id}, {
			"time_stamp": 1,
			"consignee.state": 1,
			"package_item.item_name": 1,
			"package_item.item_description": 1,
			"package_item.unit": 1,
			"package_item.quantity": 1,
		}))
		return pd.json_normalize(transaction)

	def update_forecast(self, forecast_id: str, prediction: dict):
		collection = self.mongo_manager.get_collection("demand_forecast")
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
				"status": "completed"  # Set the new status
			}
		}
		result = collection.update_one(filter_query, update_query)
		if result.matched_count == 0:
			print(f"Forecast with ID {forecast_id} not found")
		else:
			print(f"Updated forecast with ID {forecast_id}")

class ForecastingWorker:
	def __init__(self, rabbitmq_host: str, rabbitmq_user: str, rabbitmq_password: str, queue: str, mongo_uri: str, forecast_db_name: str, transactions_db_name: str):
		self.rabbitmq_manager = RabbitMQConnectionManager(rabbitmq_host, rabbitmq_user, rabbitmq_password, queue)
		self.forecasting_service = DemandForecastingService(mongo_uri, forecast_db_name, transactions_db_name)

	def process_message(self, ch, method, properties, body):
		"""Process incoming RabbitMQ messages."""
		print(f" [x] Received {body.decode()}")
		data = json.loads(body.decode())
		self.perform_forecasting(data)
		print(" [x] Done")
		ch.basic_ack(delivery_tag=method.delivery_tag)

	def perform_forecasting(self, data: dict):
		"""Perform demand forecasting and update the database."""
		try:
			forecast_id = data.get("forecast_id")
			partner_id = data.get("partner_id")
			top_n = int(data.get("number_of_item"))

			df = self.forecasting_service.load_data(partner_id)
			if df.empty:
				raise ValueError("Data is empty")

			top_items = df['package_item.item_name'].value_counts().head(top_n)
			item_names = top_items.index.tolist()

			for item in item_names:
				result = demand_forecaste_next_day_from_the_last_date(
					data=df,
					datetime_col="time_stamp",
					demand_type_col="package_item.item_name",
					filter_by=item,
					demand="package_item.quantity"
				)
				self.forecasting_service.update_forecast(forecast_id, result)
				print(f"Demand Forecast: {result}")
		except Exception as error:
			print(f"Error: {error}")
			return {"error": str(error)}

	def start_consuming(self):
		"""Start consuming messages from RabbitMQ."""
		channel = self.rabbitmq_manager.connect()
		print(' [*] Waiting for messages. To exit press CTRL+C')
		channel.basic_qos(prefetch_count=1)
		channel.basic_consume(queue=self.rabbitmq_manager.queue, on_message_callback=self.process_message)
		channel.start_consuming()

def main():
	"""Main function to initialize and run the worker."""
	rabbitmq_host = os.getenv("RABBITMQ_HOST")
	rabbitmq_user = os.getenv("RABBITMQ_USERNAME")
	rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")
	mongo_uri = os.getenv("MONGO_URI")
	forecast_db_name = os.getenv("FORECAST_DB_NAME")
	transactions_db_name = os.getenv("TRANSACTIONS_DB_NAME")
	queue = "demand_forecast_tasks"

	worker = ForecastingWorker(
		rabbitmq_host, rabbitmq_user, rabbitmq_password, queue,
		mongo_uri, forecast_db_name, transactions_db_name
	)
	worker.start_consuming()

if __name__ == "__main__":
	main()
