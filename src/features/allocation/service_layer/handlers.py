from __future__ import annotations
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from sqlalchemy import text

if TYPE_CHECKING:
    from . import unit_of_work
    from src.features.allocation.domain import commands

def get_tariff_for_service(session, id_market, cdi, voltage_level, start_date):
    tariff_query = text("""
        SELECT "CU", "C"
        FROM tariffs
        WHERE id_market = :id_market AND cdi = :cdi AND voltage_level = :voltage_level
        LIMIT 1
    """)
    result = session.execute(tariff_query, {
        'id_market': id_market,
        'cdi': cdi,
        'voltage_level': voltage_level,
        'start_date': start_date
    }).fetchone()

    if result:
        return {'CU': result.CU, 'C': result.C}
    else:
        raise ValueError("No se encontraron tarifas para el servicio especificado.")

def get_invoice(cmd: commands.GetInvoice, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        session = uow.session

        # Variables para el cálculo
        cdi = cmd.client_id  # CDI del cliente
        month = datetime(cmd.month // 100, cmd.month % 100, 1)
        start_date = month.replace(day=1)
        end_date = (month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        # Obtención de servicios
        service_query = text("""
            SELECT id_service, id_market, voltage_level
            FROM services
            WHERE cdi = :cdi
        """)
        service = session.execute(service_query, {'cdi': cdi}).fetchone()

        if not service:
            raise ValueError("No se encontró el servicio para el cliente especificado.")

        # Cálculo de Energía Activa (EA)
        consumption_query = text("""
            SELECT COALESCE(SUM(c.value), 0)
            FROM records r
            JOIN consumption c ON r.id_record = c.id_record
            WHERE r.id_service = :id_service AND r.record_timestamp BETWEEN :start_date AND :end_date
        """)
        consumption_sum = session.execute(consumption_query, {
            'id_service': service.id_service,
            'start_date': start_date,
            'end_date': end_date
        }).scalar()

        # Obtención de tarifas
        tariffs = get_tariff_for_service(session, service.id_market, cdi, service.voltage_level, start_date)
        energy_active = consumption_sum * tariffs['CU']

        # Cálculo de Comercialización de Excedentes de Energía (EC)
        injection_query = text("""
            SELECT COALESCE(SUM(value), 0)
            FROM injection
            WHERE id_record IN (
                SELECT id_record
                FROM records
                WHERE id_service = :id_service AND record_timestamp BETWEEN :start_date AND :end_date
            )
        """)
        injection_sum = session.execute(injection_query, {
            'id_service': service.id_service,
            'start_date': start_date,
            'end_date': end_date
        }).scalar()

        energy_commercialization = injection_sum * tariffs['C']

        # Cálculo de Excedentes de Energía tipo 1 (EE1)
        ee1_sum = min(injection_sum, consumption_sum)
        ee1_value = ee1_sum * -tariffs['CU']

        # Cálculo de Excedentes de Energía tipo 2 (EE2)
        ee2_sum = max(0, injection_sum - consumption_sum)
        ee2_value = 0

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
            for hour in hourly_data:
                if remaining_ee2 > 0:
                    hourly_limit = hour.value
                    hourly_value = min(remaining_ee2, hourly_limit)
                    ee2_value += hourly_value * hourly_limit  # Verifica que este cálculo sea el deseado
                    remaining_ee2 -= hourly_value

        return {
            "Energía Activa (EA)": energy_active,
            "Comercialización de Excedentes de Energía (EC)": energy_commercialization,
            "Excedentes de Energía tipo 1 (EE1)": ee1_value,
            "Excedentes de Energía tipo 2 (EE2)": ee2_value,
        }
