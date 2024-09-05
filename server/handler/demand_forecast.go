package handler

import (
	"context"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/sebsvt/message-broker/service"
)

type demandForecastHandler struct {
	demand_srv service.DemandForecastService
}

func NewDemandForecastHandler(demand_srv service.DemandForecastService) demandForecastHandler {
	return demandForecastHandler{
		demand_srv: demand_srv,
	}
}

func (h demandForecastHandler) CreateNewDemandForecast(c *fiber.Ctx) error {
	var demand_forecast service.DemandForecastCreated
	if err := c.BodyParser(&demand_forecast); err != nil {
		return c.JSON(fiber.Map{
			"error": err,
		})
	}
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*5)
	defer cancel()
	forecast_id, err := h.demand_srv.CreateNewDemandForecast(ctx, demand_forecast)
	if err != nil {
		return err
	}
	return c.JSON(fiber.Map{
		"forecast_id": forecast_id,
	})
}

func (h demandForecastHandler) GetDemandForecastFromID(c *fiber.Ctx) error {
	forecast_id := c.Params("forecast_id")
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*5)
	defer cancel()
	demand_forecast, err := h.demand_srv.GetDemandForecastByID(ctx, forecast_id)
	if err != nil {
		return err
	}
	return c.JSON(demand_forecast)
}
