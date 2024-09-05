package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/joho/godotenv"
	"github.com/rabbitmq/amqp091-go"
	"github.com/sebsvt/message-broker/handler"
	"github.com/sebsvt/message-broker/queue"
	"github.com/sebsvt/message-broker/repository"
	"github.com/sebsvt/message-broker/service"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func initRabbitMQ() (*amqp091.Channel, *amqp091.Connection, error) {
	dsn := fmt.Sprintf(
		"amqp://%v:%v@%v:%v/",
		os.Getenv("RABBITMQ_USERNAME"),
		os.Getenv("RABBITMQ_PASSWORD"),
		os.Getenv("RABBITMQ_HOST"),
		os.Getenv("RABBITMQ_PORT"),
	)
	fmt.Println(dsn)
	connection, err := amqp091.Dial(dsn)
	if err != nil {
		return nil, nil, err
	}
	ch, err := connection.Channel()
	if err != nil {
		return nil, nil, err
	}
	return ch, connection, nil
}

func initMongoDB() (*mongo.Client, error) {
	clientOptions := options.Client().ApplyURI(os.Getenv("MONGODB_URI"))
	ctx := context.TODO()
	client, err := mongo.Connect(ctx, clientOptions)
	if err != nil {
		return nil, err
	}
	return client, nil
}

func main() {
	godotenv.Load()
	ch, conn, err := initRabbitMQ()
	if err != nil {
		log.Fatalln(err)
	}
	defer conn.Close() // Close the connection when the application shuts down
	defer ch.Close()   // Close the channel when the application shuts down

	mongo_client, err := initMongoDB()
	if err != nil {
		log.Fatalln(err)
	}
	defer mongo_client.Disconnect(context.TODO())
	db := mongo_client.Database("aiselena")
	app := fiber.New()

	message_queue := queue.NewMessageQueue(ch)

	demand_forecast_repo := repository.NewDemandForecastRepositoryDB(db.Collection("demand_forecast"))
	demand_forecast_srv := service.NewDemandForecastService(demand_forecast_repo, message_queue)
	demand_forecast_handler := handler.NewDemandForecastHandler(demand_forecast_srv)

	api := app.Group("/api")
	api.Post("/demand-forecast/create", demand_forecast_handler.CreateNewDemandForecast)
	api.Get("/demand-forecast/:forecast_id", demand_forecast_handler.GetDemandForecastFromID)
	app.Listen(":8082")
}
