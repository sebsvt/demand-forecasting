package queue

import (
	"context"
	"log"

	"github.com/rabbitmq/amqp091-go"
)

type MessageQueue interface {
	SendQueueMessage(ctx context.Context, message []byte) error
}

type messageQueue struct {
	ch *amqp091.Channel
}

func NewMessageQueue(ch *amqp091.Channel) MessageQueue {
	return messageQueue{ch: ch}
}

// SendQueueMessage implements MessageQueue.
func (m messageQueue) SendQueueMessage(ctx context.Context, message []byte) error {
	queue, err := m.ch.QueueDeclare(
		"demand_forecast_tasks",
		true,  // durable
		false, // delete when unused
		false, // exclusive
		false, // no-wait
		nil,   // arguments
	)
	if err != nil {
		return err
	}

	err = m.ch.PublishWithContext(ctx, "", queue.Name, false, false, amqp091.Publishing{
		DeliveryMode: amqp091.Persistent,
		ContentType:  "application/json",
		Body:         message,
	})
	if err != nil {
		return err
	}

	log.Printf("Sent message: %s\n", message)
	return nil
}
