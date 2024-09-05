package service

import (
	"context"
	"encoding/json"
	"time"

	"github.com/google/uuid"
	"github.com/sebsvt/message-broker/aggregate"
	"github.com/sebsvt/message-broker/logs"
	"github.com/sebsvt/message-broker/queue"
)

type demandForecastService struct {
	demand_forecast_repo aggregate.DemandForecastRepository
	message_queue        queue.MessageQueue
}

func NewDemandForecastService(demand_forecast_repo aggregate.DemandForecastRepository, message_queue queue.MessageQueue) DemandForecastService {
	return demandForecastService{
		demand_forecast_repo: demand_forecast_repo,
		message_queue:        message_queue,
	}
}

func (srv demandForecastService) CreateNewDemandForecast(ctx context.Context, demand_forecast_created DemandForecastCreated) (string, error) {
	if demand_forecast_created.NumberOfItem <= 0 {
		demand_forecast_created.NumberOfItem = 10
	}
	new_demand_forecast := aggregate.DemandForecast{
		ForecastID:      uuid.New().String(),
		Title:           demand_forecast_created.Title,
		Description:     demand_forecast_created.Description,
		PartnerID:       demand_forecast_created.PartnerID,
		BuilderID:       demand_forecast_created.BuilderID,
		NumberOfItem:    demand_forecast_created.NumberOfItem,
		Status:          aggregate.Pending,
		PredictedDemand: make([]aggregate.PredictedDemand, 0),
		CreatedAt:       time.Now(),
	}

	// Save the new demand forecast to the repository
	if err := srv.demand_forecast_repo.Save(ctx, new_demand_forecast); err != nil {
		logs.Error(err)
		return "", err
	}

	// Marshal the new demand forecast to JSON
	message, err := json.Marshal(new_demand_forecast)
	if err != nil {
		logs.Error(err)
		return "", err
	}

	// Send the JSON message to the queue
	if err := srv.message_queue.SendQueueMessage(ctx, message); err != nil {
		logs.Error(err)
		return "", err
	}

	return new_demand_forecast.ForecastID, nil
}

func (srv demandForecastService) GetDemandForecastByID(ctx context.Context, forecast_id string) (*aggregate.DemandForecast, error) {
	demand_forecast, err := srv.demand_forecast_repo.FromForecastID(ctx, forecast_id)
	if err != nil {
		logs.Error(err)
		return nil, err
	}
	return demand_forecast, nil
}
func (srv demandForecastService) UpdateDemandForecast() error {
	return nil
}
