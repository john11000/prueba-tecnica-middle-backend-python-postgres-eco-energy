from __future__ import annotations
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from sqlalchemy import text

if TYPE_CHECKING:
    from . import unit_of_work
    from src.features.allocation.domain import commands

def get_tariff_for_service(session, id_market, cdi, voltage_level):
    tariff_query = text("""
        SELECT "CU", "C"
        FROM tariffs
        WHERE id_market = :id_market AND cdi = :cdi AND voltage_level = :voltage_level
        LIMIT 1
    """)
    result = session.execute(tariff_query, {
        'id_market': id_market,
        'cdi': cdi,
        'voltage_level': voltage_level
    }).fetchone()

    if result:
        return {'CU': result.CU, 'C': result.C}
    else:
        raise ValueError("No se encontraron tarifas para el servicio especificado.")

def get_service(session, cdi):
    service_query = text("""
        SELECT id_service, id_market, voltage_level
        FROM services
        WHERE cdi = :cdi
    """)
    return session.execute(service_query, {'cdi': cdi}).fetchone()

def get_consumption(session, id_service, start_date, end_date):
    consumption_query = text("""
        SELECT COALESCE(SUM(c.value), 0)
        FROM records r
        JOIN consumption c ON r.id_record = c.id_record
        WHERE r.id_service = :id_service AND r.record_timestamp BETWEEN :start_date AND :end_date
    """)
    return session.execute(consumption_query, {
        'id_service': id_service,
        'start_date': start_date,
        'end_date': end_date
    }).scalar()

def get_injection_sum(session, id_service, start_date, end_date):
    injection_query = text("""
        SELECT COALESCE(SUM(value), 0)
        FROM injection
        WHERE id_record IN (
            SELECT id_record
            FROM records
            WHERE id_service = :id_service AND record_timestamp BETWEEN :start_date AND :end_date
        )
    """)
    return session.execute(injection_query, {
        'id_service': id_service,
        'start_date': start_date,
        'end_date': end_date
    }).scalar()

def calculate_ee2_value(session, ee2_sum, start_date, end_date):
    if ee2_sum > 0:
        hourly_data_query = text("""
            SELECT record_timestamp, value
            FROM xm_data_hourly_per_agent
            WHERE record_timestamp BETWEEN :start_date AND :end_date
        """)
        hourly_data = session.execute(hourly_data_query, {
            'start_date': start_date,
            'end_date': end_date
        }).fetchall()

        remaining_ee2 = ee2_sum
        ee2_value = 0
        for hour in hourly_data:
            if remaining_ee2 > 0:
                hourly_limit = hour.value
                hourly_value = min(remaining_ee2, hourly_limit)
                ee2_value += hourly_value * hourly_limit
                remaining_ee2 -= hourly_value
        return ee2_value
    return 0

def calculate_invoice(cmd: commands.GetInvoice, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        session = uow.session

        cdi = cmd.client_id
        month = datetime(cmd.month // 100, cmd.month % 100, 1)
        start_date = month.replace(day=1)
        end_date = (month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        service = get_service(session, cdi)
        if not service:
            raise ValueError("No se encontró el servicio para el cliente especificado.")

        consumption_sum = get_consumption(session, service.id_service, start_date, end_date)
        tariffs = get_tariff_for_service(session, service.id_market, cdi, service.voltage_level)
        energy_active = consumption_sum * tariffs['CU']

        injection_sum = get_injection_sum(session, service.id_service, start_date, end_date)
        energy_commercialization = injection_sum * tariffs['C']

        ee1_sum = min(injection_sum, consumption_sum)
        ee1_value = ee1_sum * -tariffs['CU']

        ee2_sum = max(0, injection_sum - consumption_sum)
        ee2_value = calculate_ee2_value(session, ee2_sum, start_date, end_date)

        return {
            "EA": {
                "concept": "Energía Activa (EA)",
                "value": energy_active
            },
            "EC": {
                "concept": "Comercialización de Excedentes de Energía (EC)",
                "value": energy_commercialization
            },
            "EE1": {
                "concept": "Excedentes de Energía tipo 1 (EE1)",
                "value": ee1_value
            },
            "EE2": {
                "concept": "Excedentes de Energía tipo 2 (EE2)",
                "value": ee2_value
            },
        }

def get_client_statistics(cmd: commands.GetClientStatistics, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        session = uow.session

        cdi = cmd.client_id
        month = datetime(cmd.month // 100, cmd.month % 100, 1)
        start_date = month.replace(day=1)
        end_date = (month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        service = get_service(session, cdi)
        if not service:
            raise ValueError("No se encontró el servicio para el cliente especificado.")

        consumption_sum = get_consumption(session, service.id_service, start_date, end_date)
        injection_sum = get_injection_sum(session, service.id_service, start_date, end_date)

        return {
            "consumption": consumption_sum,
            "injection": injection_sum
        }

def get_system_load(uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        session = uow.session
        load_query = text("""
            SELECT record_timestamp, SUM(value) AS load
            FROM consumption
            GROUP BY record_timestamp
            ORDER BY record_timestamp
        """)
        return session.execute(load_query).fetchall()

def calculate_independent_concept(concept: str, cmd, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        session = uow.session

        if concept == 'EA':
            return calculate_invoice(cmd, uow)['EA']
        elif concept == 'EC':
            return calculate_invoice(cmd, uow)['EC']
        elif concept == 'EE1':
            return calculate_invoice(cmd, uow)['EE1']
        elif concept == 'EE2':
            return calculate_invoice(cmd, uow)['EE2']
        else:
            raise ValueError("Concepto no válido.")
