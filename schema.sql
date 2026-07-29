--
-- PostgreSQL database dump
--

\restrict FllLqFrbpHFNZXYoR90E0WXi93netb3Bz9XipQL9GHSO2waakb0doJ0XrvMMmBJ

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: evidence_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.evidence_records (
    id integer NOT NULL,
    investigation_id integer,
    service text,
    evidence_type text,
    description text,
    score double precision
);


--
-- Name: evidence_records_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.evidence_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: evidence_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.evidence_records_id_seq OWNED BY public.evidence_records.id;


--
-- Name: investigation_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.investigation_logs (
    id integer NOT NULL,
    investigation_id integer,
    log_id text,
    "timestamp" bigint,
    cmdb_id text,
    log_name text,
    value text
);


--
-- Name: investigation_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.investigation_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: investigation_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.investigation_logs_id_seq OWNED BY public.investigation_logs.id;


--
-- Name: investigation_metrics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.investigation_metrics (
    id integer NOT NULL,
    investigation_id integer,
    "timestamp" bigint,
    cmdb_id text,
    kpi_name text,
    value double precision
);


--
-- Name: investigation_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.investigation_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: investigation_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.investigation_metrics_id_seq OWNED BY public.investigation_metrics.id;


--
-- Name: investigation_traces; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.investigation_traces (
    id integer NOT NULL,
    investigation_id integer,
    "timestamp" bigint,
    cmdb_id text,
    span_id text,
    trace_id text,
    duration integer,
    type text,
    status_code text,
    operation_name text,
    parent_span text
);


--
-- Name: investigation_traces_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.investigation_traces_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: investigation_traces_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.investigation_traces_id_seq OWNED BY public.investigation_traces.id;


--
-- Name: investigations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.investigations (
    id integer NOT NULL,
    issue_key text,
    environment text,
    dataset text,
    incident_time timestamp without time zone,
    window_start timestamp without time zone,
    window_end timestamp without time zone,
    incident_description text
);


--
-- Name: investigations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.investigations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: investigations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.investigations_id_seq OWNED BY public.investigations.id;


--
-- Name: processed_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.processed_logs (
    id integer NOT NULL,
    investigation_id integer,
    cmdb_id text,
    log_pattern text,
    severity text
);


--
-- Name: processed_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.processed_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: processed_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.processed_logs_id_seq OWNED BY public.processed_logs.id;


--
-- Name: processed_metrics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.processed_metrics (
    id integer NOT NULL,
    investigation_id integer,
    cmdb_id text,
    kpi_name text,
    feature_name text,
    feature_value double precision,
    is_anomaly boolean
);


--
-- Name: processed_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.processed_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: processed_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.processed_metrics_id_seq OWNED BY public.processed_metrics.id;


--
-- Name: processed_traces; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.processed_traces (
    id integer NOT NULL,
    investigation_id integer,
    parent_service text,
    child_service text,
    latency double precision
);


--
-- Name: processed_traces_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.processed_traces_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: processed_traces_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.processed_traces_id_seq OWNED BY public.processed_traces.id;


--
-- Name: rca_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rca_results (
    id integer NOT NULL,
    investigation_id integer,
    root_cause text,
    confidence double precision,
    explanation text
);


--
-- Name: rca_results_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.rca_results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rca_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.rca_results_id_seq OWNED BY public.rca_results.id;


--
-- Name: evidence_records id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evidence_records ALTER COLUMN id SET DEFAULT nextval('public.evidence_records_id_seq'::regclass);


--
-- Name: investigation_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investigation_logs ALTER COLUMN id SET DEFAULT nextval('public.investigation_logs_id_seq'::regclass);


--
-- Name: investigation_metrics id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investigation_metrics ALTER COLUMN id SET DEFAULT nextval('public.investigation_metrics_id_seq'::regclass);


--
-- Name: investigation_traces id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investigation_traces ALTER COLUMN id SET DEFAULT nextval('public.investigation_traces_id_seq'::regclass);


--
-- Name: investigations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investigations ALTER COLUMN id SET DEFAULT nextval('public.investigations_id_seq'::regclass);


--
-- Name: processed_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.processed_logs ALTER COLUMN id SET DEFAULT nextval('public.processed_logs_id_seq'::regclass);


--
-- Name: processed_metrics id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.processed_metrics ALTER COLUMN id SET DEFAULT nextval('public.processed_metrics_id_seq'::regclass);


--
-- Name: processed_traces id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.processed_traces ALTER COLUMN id SET DEFAULT nextval('public.processed_traces_id_seq'::regclass);


--
-- Name: rca_results id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rca_results ALTER COLUMN id SET DEFAULT nextval('public.rca_results_id_seq'::regclass);


--
-- Name: evidence_records evidence_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evidence_records
    ADD CONSTRAINT evidence_records_pkey PRIMARY KEY (id);


--
-- Name: investigation_logs investigation_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investigation_logs
    ADD CONSTRAINT investigation_logs_pkey PRIMARY KEY (id);


--
-- Name: investigation_metrics investigation_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investigation_metrics
    ADD CONSTRAINT investigation_metrics_pkey PRIMARY KEY (id);


--
-- Name: investigation_traces investigation_traces_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investigation_traces
    ADD CONSTRAINT investigation_traces_pkey PRIMARY KEY (id);


--
-- Name: investigations investigations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investigations
    ADD CONSTRAINT investigations_pkey PRIMARY KEY (id);


--
-- Name: processed_logs processed_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.processed_logs
    ADD CONSTRAINT processed_logs_pkey PRIMARY KEY (id);


--
-- Name: processed_metrics processed_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.processed_metrics
    ADD CONSTRAINT processed_metrics_pkey PRIMARY KEY (id);


--
-- Name: processed_traces processed_traces_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.processed_traces
    ADD CONSTRAINT processed_traces_pkey PRIMARY KEY (id);


--
-- Name: rca_results rca_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rca_results
    ADD CONSTRAINT rca_results_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

\unrestrict FllLqFrbpHFNZXYoR90E0WXi93netb3Bz9XipQL9GHSO2waakb0doJ0XrvMMmBJ

