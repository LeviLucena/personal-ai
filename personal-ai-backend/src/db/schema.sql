-- Personal AI Platform — PostgreSQL Schema
-- All data in English, matching agent data shapes

DO $$ BEGIN
    CREATE TYPE risk_level AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE priority_level AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE unit_status AS ENUM ('NORMAL', 'WARNING', 'CRITICAL');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE clinical_trend AS ENUM ('IMPROVING', 'STABLE', 'WORSENING');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ============================================================
-- PATIENTS
-- Used by: WF-01 (summarization), WF-07 (documentation), WF-13 (follow-up)
-- ============================================================
CREATE TABLE IF NOT EXISTS patients (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    age INTEGER NOT NULL,
    main_diagnosis VARCHAR NOT NULL,
    comorbidities TEXT[] DEFAULT '{}',
    allergies TEXT[] DEFAULT '{}',
    admission_date DATE NOT NULL,
    bed VARCHAR DEFAULT '',
    specialty VARCHAR DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CLINICAL EVOLUTIONS (daily progress notes)
-- Used by: WF-02 (7-day summarization), WF-07 (documentation context)
-- ============================================================
CREATE TABLE IF NOT EXISTS clinical_evolutions (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    record_date DATE NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evolutions_patient_date ON clinical_evolutions(patient_id, record_date DESC);

-- ============================================================
-- REGULATORY REQUESTS (authorization queue)
-- Used by: WF-04 (queue prioritization)
-- ============================================================
CREATE TABLE IF NOT EXISTS regulatory_requests (
    id VARCHAR PRIMARY KEY,
    patient_name VARCHAR NOT NULL,
    age INTEGER NOT NULL,
    cid VARCHAR NOT NULL,
    procedure_name VARCHAR NOT NULL,
    wait_days INTEGER NOT NULL,
    clinical_risk risk_level NOT NULL,
    sla_days INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- HOSPITAL BILLS (accounts receivable)
-- Used by: WF-05 (denial prediction), WF-06 (document review)
-- ============================================================
CREATE TABLE IF NOT EXISTS hospital_bills (
    id VARCHAR PRIMARY KEY,
    patient_name VARCHAR NOT NULL,
    insurance VARCHAR NOT NULL,
    procedure_name VARCHAR NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    has_medical_report BOOLEAN DEFAULT FALSE,
    has_surgical_report BOOLEAN DEFAULT FALSE,
    has_progress_notes BOOLEAN DEFAULT FALSE,
    has_opme_authorized BOOLEAN DEFAULT FALSE,
    icd_compatible BOOLEAN DEFAULT TRUE,
    historical_denial_rate DECIMAL(4,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- APPOINTMENTS (outpatient schedule)
-- Used by: WF-09 (no-show prediction)
-- ============================================================
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_name VARCHAR NOT NULL,
    appointment_type VARCHAR NOT NULL,
    confirmed BOOLEAN DEFAULT FALSE,
    historical_miss_rate DECIMAL(4,2) DEFAULT 0,
    distance_km DECIMAL(6,2) DEFAULT 0,
    insurance_plan VARCHAR DEFAULT '',
    age INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- HOSPITAL UNITS (occupancy monitoring)
-- Used by: WF-14 (gargalos/monitoramento), aggregator dashboard
-- ============================================================
CREATE TABLE IF NOT EXISTS hospital_units (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    occupancy_pct DECIMAL(5,1) NOT NULL,
    wait_time_min INTEGER NOT NULL,
    status unit_status NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- SURGICAL ROOMS & SURGERIES
-- Used by: WF-10 (surgical scheduling), WF-11 (surgical agenda)
-- ============================================================
CREATE TABLE IF NOT EXISTS surgical_rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS surgeries (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES surgical_rooms(id) ON DELETE CASCADE,
    patient_name VARCHAR NOT NULL,
    procedure_name VARCHAR NOT NULL,
    specialty VARCHAR NOT NULL,
    is_urgent BOOLEAN DEFAULT FALSE,
    duration_min INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- KPI METRICS (aggregated indicators)
-- Used by: WF-03 (insights generation)
-- ============================================================
CREATE TABLE IF NOT EXISTS kpi_metrics (
    id SERIAL PRIMARY KEY,
    category VARCHAR NOT NULL,
    indicator VARCHAR NOT NULL,
    current_value DECIMAL(10,2),
    target_value DECIMAL(10,2),
    unit VARCHAR DEFAULT '',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CONVERSATIONAL SESSIONS (LangGraph memory persistence)
-- Used by: WF-12 (conversational copilot)
-- ============================================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    thread_id VARCHAR PRIMARY KEY,
    profile VARCHAR NOT NULL DEFAULT 'executive',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR NOT NULL REFERENCES chat_sessions(thread_id) ON DELETE CASCADE,
    role VARCHAR NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
