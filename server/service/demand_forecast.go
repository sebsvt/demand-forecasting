package service

import (
	"context"
	"time"

	"github.com/sebsvt/message-broker/aggregate"
)

type DemandForecastCreated struct {
	Title        string `json:"title"`
	Description  string `json:"description"`
	BuilderID    string `json:"builder_id"`
	PartnerID    string `json:"partner_id"`
	NumberOfItem int    `json:"number_of_item"`
}

type DemandForecast struct {
	Title       string                                `json:"title"`
	Description string                                `json:"description"`
	Status      aggregate.ForecastingDemandStatusEnum `json:"status"`
	PartnerID   string                                `json:"partner_id"`
	CreatedAt   time.Time                             `json:"created_at"`
}

type DemandForecastService interface {
	CreateNewDemandForecast(ctx context.Context, demand_forecast_created DemandForecastCreated) (string, error)
	GetDemandForecastByID(ctx context.Context, forecast_id string) (*aggregate.DemandForecast, error)
	UpdateDemandForecast() error
}
