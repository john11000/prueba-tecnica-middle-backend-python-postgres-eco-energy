from sqlalchemy.orm import relationship
from src.features.allocation.domain import model
from src.features.allocation.infrastructure.models import (
    mapper_registry, injection, consumption, xm_data_hourly_per_agent, services, records, tariffs
)


def start_mappers():
    injection_mapper = mapper_registry.map_imperatively(model.Injection, injection)

    consumption_mapper = mapper_registry.map_imperatively(model.Consumption, consumption)

    xm_data_mapper = mapper_registry.map_imperatively(model.XMDataHourlyPerAgent, xm_data_hourly_per_agent)

    services_mapper = mapper_registry.map_imperatively(
        model.Service,
        services,
        properties={
            "records": relationship("Record", back_populates="service"),
        }
    )

    records_mapper = mapper_registry.map_imperatively(
        model.Record,
        records,
        properties={
            "xm_data": relationship(xm_data_mapper),
        }
    )

    tariffs_mapper = mapper_registry.map_imperatively(
        model.Tariff,
        tariffs,
        properties={
            "service": relationship(services_mapper), 
        }
    )
