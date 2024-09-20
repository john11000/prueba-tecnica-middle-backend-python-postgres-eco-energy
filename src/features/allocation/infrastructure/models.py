from sqlalchemy import (
    Table, Column, Integer, Float, ForeignKey, String, DateTime, CheckConstraint, UniqueConstraint, event, ForeignKeyConstraint
)
from sqlalchemy.orm import registry
from src.features.allocation.domain import model

# Registrar el mapper
mapper_registry = registry()

# Table injection
injection = Table(
    "injection",
    mapper_registry.metadata,
    Column("id_record", Integer, primary_key=True, autoincrement=True),
    Column("value", Float, nullable=False)
)

# Table consumption
consumption = Table(
    "consumption",
    mapper_registry.metadata,
    Column("id_record", Integer, primary_key=True, autoincrement=True),
    Column("value", Float, nullable=False)
)

# Table xm_data_hourly_per_agent
xm_data_hourly_per_agent = Table(
    "xm_data_hourly_per_agent",
    mapper_registry.metadata,
    Column("value", Float, nullable=False),
    Column("record_timestamp", DateTime, primary_key=True)
)

# Table services
services = Table(
    "services",
    mapper_registry.metadata,
    Column("id_service", Integer, primary_key=True, autoincrement=True),
    Column("id_market", Integer, nullable=False),
    Column("cdi", Integer, nullable=False),
    Column("voltage_level", Integer, nullable=False),
    CheckConstraint('voltage_level IN (1, 2, 3, 4)'),
    UniqueConstraint("id_market", "cdi", "voltage_level")
)

# Table records
records = Table(
    "records",
    mapper_registry.metadata,
    Column("id_record", Integer, primary_key=True, autoincrement=True),
    Column("id_service", Integer, ForeignKey("services.id_service"), nullable=False),
    Column("record_timestamp", DateTime, ForeignKey("xm_data_hourly_per_agent.record_timestamp"), nullable=False)
)

# Table tariffs
tariffs = Table(
    "tariffs",
    mapper_registry.metadata,
    Column("id_market", Integer, primary_key=True),
    Column("cdi", Integer, primary_key=True),
    Column("voltage_level", Integer, primary_key=True),
    Column("G", Float),
    Column("T", Float),
    Column("D", Float),
    Column("R", Float),
    Column("C", Float),
    Column("P", Float),
    Column("CU", Float),
    ForeignKeyConstraint(
        ["id_market", "cdi", "voltage_level"],
        ["services.id_market", "services.cdi", "services.voltage_level"]
    )
)