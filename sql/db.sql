CREATE TABLE "services" (
  "id_service" SERIAL PRIMARY KEY,
  "id_market" INTEGER,
  "cdi" INTEGER,
  "voltage_level" INTEGER,
  UNIQUE ("id_market", "cdi", "voltage_level")
);

CREATE TABLE "records" (
  "id_record" SERIAL PRIMARY KEY,
  "id_service" INTEGER,
  "record_timestamp" TIMESTAMP UNIQUE,  -- Añadir restricción única
  FOREIGN KEY ("id_service") REFERENCES "services" ("id_service")
);

CREATE TABLE "injection" (
  "id_injection" SERIAL PRIMARY KEY,
  "id_record" INTEGER,
  "value" FLOAT NOT NULL,
  FOREIGN KEY ("id_record") REFERENCES "records" ("id_record") ON DELETE CASCADE
);

CREATE TABLE "consumption" (
  "id_consumption" SERIAL PRIMARY KEY,
  "id_record" INTEGER,
  "value" FLOAT NOT NULL,
  FOREIGN KEY ("id_record") REFERENCES "records" ("id_record") ON DELETE CASCADE
);

CREATE TABLE "xm_data_hourly_per_agent" (
  "id_xm_data" SERIAL PRIMARY KEY,
  "value" FLOAT NOT NULL,
  "record_timestamp" TIMESTAMP,
  FOREIGN KEY ("record_timestamp") REFERENCES "records" ("record_timestamp")
);

CREATE TABLE "tariffs" (
  "id_market" INTEGER,
  "cdi" INTEGER,
  "voltage_level" INTEGER,
  "G" FLOAT,
  "T" FLOAT,
  "D" FLOAT,
  "R" FLOAT,
  "C" FLOAT,
  "P" FLOAT,
  "CU" FLOAT,
  PRIMARY KEY ("id_market", "cdi", "voltage_level"),
  FOREIGN KEY ("id_market", "cdi", "voltage_level") REFERENCES "services" ("id_market", "cdi", "voltage_level")
);
