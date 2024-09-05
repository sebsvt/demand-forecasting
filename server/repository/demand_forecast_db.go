package repository

import (
	"context"

	"github.com/google/uuid"
	"github.com/sebsvt/message-broker/aggregate"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type demandForecastRepositoryDB struct {
	collection *mongo.Collection
}

func NewDemandForecastRepositoryDB(collection *mongo.Collection) aggregate.DemandForecastRepository {
	return demandForecastRepositoryDB{
		collection: collection,
	}
}

func (repo demandForecastRepositoryDB) NextIdentity() string {
	return uuid.New().String()
}
func (repo demandForecastRepositoryDB) FromForecastID(ctx context.Context, forecast_id string) (*aggregate.DemandForecast, error) {
	var demand_forecast aggregate.DemandForecast
	filter := bson.M{
		"forecast_id": forecast_id,
	}
	result := repo.collection.FindOne(ctx, filter, options.FindOne())
	if err := result.Decode(&demand_forecast); err != nil {
		return nil, err
	}
	return &demand_forecast, nil
}
func (repo demandForecastRepositoryDB) Save(ctx context.Context, entity aggregate.DemandForecast) error {
	forecast_id := entity.ForecastID
	filter := bson.M{
		"forecast_id": forecast_id,
	}
	update := bson.M{
		"$set": entity,
	}
	upsert := true
	opts := options.UpdateOptions{
		Upsert: &upsert,
	}
	_, err := repo.collection.UpdateOne(ctx, filter, update, &opts)
	return err
}
