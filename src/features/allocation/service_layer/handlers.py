from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy import text
from src.features.allocation.domain import commands
from src.features.allocation.domain.exceptions import InvalidValueError
from sqlalchemy.orm import Session
from src.features.allocation.service_layer import unit_of_work

def get_tariff_for_service(session: Session, id_market: int, cdi: int, voltage_level: int) -> dict:
    tariff_query = text("""
        SELECT cu , c
        FROM tariffs t
        WHERE id_market = :id_market AND voltage_level = :voltage_level
        """ + ("""AND cdi = :cdi""" if voltage_level not in (2, 3) else "") + """
        LIMIT 1
    """)
    
    params = {'id_market': id_market, 'voltage_level': voltage_level}
    if voltage_level not in (2, 3):
        params['cdi'] = cdi

    result = session.execute(tariff_query, params).fetchone()

    if result:
        return {'CU': result.cu, 'C': result.c}
    else:
        raise InvalidValueError("No se encontraron tarifas para el servicio especificado.")

def get_service(session: Session, id_service: int):
    service_query = text("""
        SELECT id_service, id_market, voltage_level, cdi
        FROM services
        WHERE id_service = :id_service
    """)
    return session.execute(service_query, {'id_service': id_service}).fetchone()

def get_consumption(session: Session, id_service: int, start_date=None, end_date=None, showDetails=False):
    base_query = """
        SELECT COALESCE(SUM(c.value), 0) AS total_consumption
        FROM records r
        JOIN consumption c ON r.id_record = c.id_record
        WHERE r.id_service = :id_service
    """
    
    details_query = """
        SELECT c.id_record, r.id_service, c.id_consumption, r.record_timestamp, c.value
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
        base_query += " AND " + " AND ".join(conditions)
        details_query += " AND " + " AND ".join(conditions)

    params = {'id_service': id_service}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date

    total_consumption = session.execute(text(base_query), params).scalar()

    if showDetails:
        details = session.execute(text(details_query), params).fetchall()
        return {
            "total_consumption": total_consumption,
            "details": [
                {
                    "id_record": row.id_record,
                    "id_service": row.id_service,
                    "id_consumption": row.id_consumption,
                    "record_timestamp": row.record_timestamp,
                    "value": row.value
                } for row in details
            ]
        }

    return {
        "total_consumption": total_consumption
    }


def get_injection(session: Session, id_service: int, start_date=None, end_date=None, showDetails=False):
    base_query = """
        SELECT COALESCE(SUM(i.value), 0) AS total_injection
        FROM records r
        JOIN injection i ON r.id_record = i.id_record
        WHERE r.id_service = :id_service
    """
    
    details_query = """
        SELECT i.id_record, r.id_service, i.id_injection, r.record_timestamp, i.value
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
        base_query += " AND " + " AND ".join(conditions)
        details_query += " AND " + " AND ".join(conditions)

    params = {'id_service': id_service}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date

    total_injection = session.execute(text(base_query), params).scalar()

    if showDetails:
        details = session.execute(text(details_query), params).fetchall()
        return {
            "total_injection": total_injection,
            "details": [
                {
                    "id_record": row.id_record,
                    "id_service": row.id_service,
                    "id_injection": row.id_injection,
                    "record_timestamp": row.record_timestamp,
                    "value": row.value
                } for row in details
            ]
        }

    return {
        "total_injection": total_injection
    }

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
        id_service = cmd.id_service
        concept = cmd.concept
        month = datetime(cmd.month // 100, cmd.month % 100, 1)
        start_date = month.replace(day=1)
        end_date = (month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        service = get_service(session, id_service)
        if not service:
            raise InvalidValueError(f"No se encontró el servicio {id_service}")

        tariffs = get_tariff_for_service(session, service.id_market, service.cdi, service.voltage_level)
        consumption = get_consumption(session, service.id_service, start_date, end_date)
        injection = get_injection(session, service.id_service, start_date, end_date)

        consumption_sum = consumption['total_consumption']
        injection_sum = injection['total_injection']

        results = {}
        results['cdi'] = service.cdi
        results['id_market'] = service.id_market
        if concept in {'EA', 'EC', 'EE1', 'EE2'}:
            if concept == 'EA':
                results['EA'] = calculate_energy_active(consumption_sum, tariffs)
            elif concept == 'EC':
                results['EC'] = calculate_energy_commercialization(injection_sum, tariffs)
            elif concept == 'EE1':
                results['EE1'] = calculate_ee1(consumption_sum, injection_sum, tariffs)
            elif concept == 'EE2':
                results['EE2'] = calculate_ee2(session, injection_sum, consumption_sum, start_date, end_date)
        else:
            results['EA'] = calculate_energy_active(consumption_sum, tariffs)
            results['EC'] = calculate_energy_commercialization(injection_sum, tariffs)
            results['EE1'] = calculate_ee1(consumption_sum, injection_sum, tariffs)
            results['EE2'] = calculate_ee2(session, injection_sum, consumption_sum, start_date, end_date)

        uow.commit()
        return results

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
            id_service = cmd.id_service
            show_details = cmd.show_details
            service = get_service(session, id_service)
            if not service:
                raise InvalidValueError("No se encontró el servicio para el cliente especificado.")

            consumption_sum = get_consumption(session, service.id_service ,showDetails=show_details)
            injection_sum = get_injection(session, service.id_service, showDetails=show_details)

            uow.commit()
            return {
                "consumption": consumption_sum,
                "injection": injection_sum
            }
        except Exception:
            uow.rollback()
            raise
