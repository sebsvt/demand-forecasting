package aggregate

import (
	"context"
	"time"
)

type ForecastingDemandStatusEnum string

const (
	Pending   ForecastingDemandStatusEnum = "pending"
	Failed    ForecastingDemandStatusEnum = "failed"
	Completed ForecastingDemandStatusEnum = "completed"
)

type DemandForecast struct {
	ForecastID      string                      `bson:"forecast_id" json:"forecast_id"`
	Title           string                      `bson:"title" json:"title"`
	Description     string                      `bson:"description" json:"description"`
	PredictedDemand []PredictedDemand           `bson:"demand_forecast_item" json:"demand_forecast_item"`
	Status          ForecastingDemandStatusEnum `bson:"status" json:"status"`
	CreatedAt       time.Time                   `bson:"created_at" json:"created_at"`
	PartnerID       string                      `bson:"partner_id" json:"partner_id"`
	BuilderID       string                      `bson:"builder_id" json:"builder_id"`
	NumberOfItem    int                         `bson:"number_of_item" json:"number_of_item"`
}

type PredictedDemand struct {
	Name         string         `bson:"name" json:"name"`
	FromLastDate time.Time      `bson:"from_last_date" json:"from_last_date"`
	Predictions  []FutureDemand `bson:"predictions" json:"predictions"`
	Kpi          Kpi            `bson:"kpi" json:"kpi"`
}

type FutureDemand struct {
	FutureDate string  `bson:"future_date" json:"future_date"`
	Demand     float64 `bson:"demand" json:"demand"`
}

type Kpi struct {
	BiasRel float64 `bson:"bias_rel" json:"bias_rel"`
	Mape    float64 `bson:"mape" json:"mape"`
	Mae     float64 `bson:"mae" json:"mae"`
	Rmse    float64 `bson:"rmse" json:"rmse"`
}

type DemandForecastRepository interface {
	NextIdentity() string
	FromForecastID(ctx context.Context, forecastID string) (*DemandForecast, error)
	Save(ctx context.Context, entity DemandForecast) error
}
