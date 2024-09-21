from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy import text
from src.features.allocation.domain import commands
from src.features.allocation.domain.exceptions import InvalidValueError
from sqlalchemy.orm import Session
from src.features.allocation.service_layer import unit_of_work

def get_tariff_for_service(session: Session, id_market: int, cdi: int, voltage_level: int) -> dict:
    tariff_query = text("""
        SELECT "CU", "C"
        FROM tariffs
        WHERE id_market = :id_market AND voltage_level = :voltage_level
        """ + ("""AND cdi = :cdi""" if voltage_level not in (2, 3) else "") + """
        LIMIT 1
    """)
    
    params = {'id_market': id_market, 'voltage_level': voltage_level}
    if voltage_level not in (2, 3):
        params['cdi'] = cdi

    result = session.execute(tariff_query, params).fetchone()

    if result:
        return {'CU': result.CU, 'C': result.C}
    else:
        raise InvalidValueError("No se encontraron tarifas para el servicio especificado.")

def get_service(session: Session, cdi: int):
    service_query = text("""
        SELECT id_service, id_market, voltage_level
        FROM services
        WHERE cdi = :cdi
    """)
    return session.execute(service_query, {'cdi': cdi}).fetchone()

def get_consumption(session: Session, id_service: int, start_date=None, end_date=None):
    query = """
        SELECT COALESCE(SUM(c.value), 0)
        FROM records r
        JOIN consumption c ON r.id_record = c.id_record
        WHERE r.id_service = :id_service
    """
    
    conditions = []

    if start_date:
        conditions.append("r.record_timestamp >= :start_date")
    if end_date:
        conditions.append("r.record_timestamp <= :end_date")
    
    if conditions:
        query += " AND " + " AND ".join(conditions)

    params = {'id_service': id_service}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date

    return session.execute(text(query), params).scalar()

def get_injection_sum(session: Session, id_service: int, start_date=None, end_date=None):
    query = """
        SELECT COALESCE(SUM(i.value), 0) AS total_injection
        FROM records r
        JOIN injection i ON r.id_record = i.id_record
        WHERE r.id_service = :id_service
    """

    conditions = []
    
    if start_date:
        conditions.append("r.record_timestamp >= :start_date")
    if end_date:
        conditions.append("r.record_timestamp <= :end_date")
    
    if conditions:
        query += " AND " + " AND ".join(conditions)

    params = {'id_service': id_service}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date

    return session.execute(text(query), params).scalar()

def calculate_ee2_value(session: Session, ee2_sum: float, start_date: datetime, end_date: datetime) -> float:
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

def calculate_invoice(cmd: commands.GetInvoice, uow: unit_of_work.SqlAlchemyUnitOfWork) -> dict:
    with uow:
        session = uow.session
        try:
            cdi = cmd.client_id
            month = datetime(cmd.month // 100, cmd.month % 100, 1)
            start_date = month.replace(day=1)
            end_date = (month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

            service = get_service(session, cdi)
            if not service:
                raise InvalidValueError("No se encontró el servicio para el cliente especificado.")

            tariffs = get_tariff_for_service(session, service.id_market, cdi, service.voltage_level)

            consumption_sum = get_consumption(session, service.id_service, start_date, end_date)
            injection_sum = get_injection_sum(session, service.id_service, start_date, end_date)

            ea = calculate_energy_active(consumption_sum, tariffs)
            ec = calculate_energy_commercialization(injection_sum, tariffs)
            ee1 = calculate_ee1(consumption_sum, injection_sum, tariffs)
            ee2 = calculate_ee2(session, injection_sum, consumption_sum, start_date, end_date)

            uow.commit()  # Commit transaction if all calculations succeed
            return {
                "EA": ea,
                "EC": ec,
                "EE1": ee1,
                "EE2": ee2,
            }
        except Exception:
            uow.rollback()  # Rollback the transaction on any error
            raise

def calculate_energy_active(consumption_sum: float, tariffs: dict) -> dict:
    energy_active = consumption_sum * tariffs['CU']
    return {
        "concept": "Energía Activa (EA)",
        "sum": consumption_sum,
        "CU": tariffs['CU'],
        "value": energy_active
    }

def calculate_energy_commercialization(injection_sum: float, tariffs: dict) -> dict:
    energy_commercialization = injection_sum * tariffs['C']
    return {
        "concept": "Comercialización de Excedentes de Energía (EC)",
        "sum": injection_sum,
        "C": tariffs['C'],
        "value": energy_commercialization
    }

def calculate_ee1(consumption_sum: float, injection_sum: float, tariffs: dict) -> dict:
    ee1_sum = min(injection_sum, consumption_sum)
    ee1_value = ee1_sum * -tariffs['CU']
    return {
        "concept": "Excedentes de Energía tipo 1 (EE1)",
        "sum": ee1_sum,
        "-CU": -tariffs['CU'],
        "value": ee1_value
    }

def calculate_ee2(session: Session, injection_sum: float, consumption_sum: float, start_date: datetime, end_date: datetime) -> dict:
    ee2_sum = max(0, injection_sum - consumption_sum)
    ee2_value = calculate_ee2_value(session, ee2_sum, start_date, end_date)
    return {
        "concept": "Excedentes de Energía tipo 2 (EE2)",
        "sum": ee2_sum,
        "value": ee2_value
    }

def get_client_statistics(cmd: commands.GetClientStatistics, uow: unit_of_work.SqlAlchemyUnitOfWork) -> dict:
    with uow:
        session = uow.session
        try:
            cdi = cmd.client_id
            service = get_service(session, cdi)
            if not service:
                raise InvalidValueError("No se encontró el servicio para el cliente especificado.")

            consumption_sum = get_consumption(session, service.id_service)
            injection_sum = get_injection_sum(session, service.id_service)

            uow.commit()
            return {
                "consumption": consumption_sum,
                "injection": injection_sum
            }
        except Exception:
            uow.rollback()
            raise

def calculate_independent_concept(cmd: commands.CalculateInvoiceByConcept, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        session = uow.session

        cdi = cmd.client_id
        service = get_service(session, cdi)
        if not service:
            raise InvalidValueError("No se encontró el servicio para el cliente especificado.")

        month = datetime(cmd.month // 100, cmd.month % 100, 1)
        start_date = month.replace(day=1)
        end_date = (month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        tariffs = get_tariff_for_service(session, service.id_market, cdi, service.voltage_level)

        consumption_sum = get_consumption(session, service.id_service, start_date, end_date)
        injection_sum = get_injection_sum(session, service.id_service, start_date, end_date)

        concept = cmd.concept

        if concept == 'EA':
            return calculate_energy_active(consumption_sum, tariffs)
        elif concept == 'EC':
            return calculate_energy_commercialization(injection_sum, tariffs)
        elif concept == 'EE1':
            return calculate_ee1(consumption_sum, injection_sum, tariffs)
        elif concept == 'EE2':
            return calculate_ee2(session, injection_sum, consumption_sum, start_date, end_date)
        else:
            raise InvalidValueError("Concepto no válido.")