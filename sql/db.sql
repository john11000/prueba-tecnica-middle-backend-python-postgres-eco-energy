CREATE SEQUENCE IF NOT EXISTS services_id_service_seq;
CREATE SEQUENCE IF NOT EXISTS records_id_record_seq;
CREATE SEQUENCE IF NOT EXISTS injection_id_injection_seq;
CREATE SEQUENCE IF NOT EXISTS consumption_id_consumption_seq;
CREATE SEQUENCE IF NOT EXISTS xm_data_hourly_per_agent_id_xm_data_seq;

CREATE TABLE IF NOT exists "services" (
    id_service INTEGER PRIMARY KEY DEFAULT nextval('services_id_service_seq'),
    id_market INTEGER NOT NULL,
    cdi INTEGER,
    voltage_level INTEGER NOT NULL,
    UNIQUE (id_market, cdi, voltage_level)
);


CREATE TABLE IF NOT EXISTS "records" (
    id_record SERIAL PRIMARY KEY,
    id_service INTEGER,
    record_timestamp TIMESTAMP,
    FOREIGN KEY (id_service) REFERENCES "services" (id_service)
);

CREATE TABLE IF NOT EXISTS "xm_data_hourly_per_agent" (
    record_timestamp TIMESTAMP PRIMARY KEY,
    value FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS "injection" (
    id_injection INTEGER PRIMARY KEY DEFAULT nextval('injection_id_injection_seq'),
    id_record INTEGER,
    value FLOAT NOT NULL,
    FOREIGN KEY (id_record) REFERENCES "records" (id_record) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "consumption" (
    id_consumption INTEGER PRIMARY KEY DEFAULT nextval('consumption_id_consumption_seq'),
    id_record INTEGER,
    value FLOAT NOT NULL,
    FOREIGN KEY (id_record) REFERENCES "records" (id_record) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "xm_data_hourly_per_agent" (
    id_xm_data INTEGER PRIMARY KEY DEFAULT nextval('xm_data_hourly_per_agent_id_xm_data_seq'),
    value FLOAT NOT NULL,
    record_timestamp TIMESTAMP,
    FOREIGN KEY (record_timestamp) REFERENCES "records" (record_timestamp)
);

CREATE TABLE IF NOT EXISTS tariffs (
    id_tariff SERIAL PRIMARY KEY,
    id_market INTEGER NOT NULL,
    cdi INTEGER,
    voltage_level INTEGER NOT NULL,
    G FLOAT,
    T FLOAT,
    D FLOAT,
    R FLOAT,
    C FLOAT,
    P FLOAT,
    CU FLOAT,
    FOREIGN KEY (id_market, cdi, voltage_level) 
        REFERENCES services (id_market, cdi, voltage_level) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION ensure_service_exists()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM services 
        WHERE id_market = NEW.id_market 
        AND (cdi IS NOT DISTINCT FROM NEW.cdi)
        AND voltage_level = NEW.voltage_level
    ) THEN
        INSERT INTO services (id_market, cdi, voltage_level)
        VALUES (NEW.id_market, NEW.cdi, NEW.voltage_level);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_insert_tariffs
BEFORE INSERT ON tariffs
FOR EACH ROW
EXECUTE FUNCTION ensure_service_exists();

