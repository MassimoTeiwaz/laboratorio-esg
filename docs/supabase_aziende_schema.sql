-- Schema tabella aziende per Sistema Certificazione ESG
-- Esegui questo script nel SQL Editor di Supabase.

create table if not exists public.aziende (
    id bigint generated always as identity primary key,
    nome text not null,
    partita_iva text not null,
    consumo_kwh numeric(12, 2) not null default 0,
    co2_kg numeric(12, 2) not null default 0,
    numero_dipendenti integer not null default 0,
    donne_ruoli_comando integer not null default 0,
    ore_formazione_annue numeric(12, 2) not null default 0,
    codice_etico boolean not null default false,
    rating_esg integer not null default 0,
    created_at timestamptz not null default now()
);

-- Aggiunge eventuali colonne mancanti se la tabella esiste gia'
alter table public.aziende
    add column if not exists nome text,
    add column if not exists partita_iva text,
    add column if not exists consumo_kwh numeric(12, 2) not null default 0,
    add column if not exists co2_kg numeric(12, 2) not null default 0,
    add column if not exists numero_dipendenti integer not null default 0,
    add column if not exists donne_ruoli_comando integer not null default 0,
    add column if not exists ore_formazione_annue numeric(12, 2) not null default 0,
    add column if not exists codice_etico boolean not null default false,
    add column if not exists rating_esg integer not null default 0,
    add column if not exists created_at timestamptz not null default now();

-- Vincoli di qualita' dati
alter table public.aziende
    drop constraint if exists aziende_rating_esg_range;

alter table public.aziende
    add constraint aziende_rating_esg_range check (rating_esg between 0 and 100);

alter table public.aziende
    drop constraint if exists aziende_valori_non_negativi;

alter table public.aziende
    add constraint aziende_valori_non_negativi check (
        consumo_kwh >= 0
        and co2_kg >= 0
        and numero_dipendenti >= 0
        and donne_ruoli_comando >= 0
        and ore_formazione_annue >= 0
    );

alter table public.aziende
    drop constraint if exists aziende_donne_non_superano_totale;

alter table public.aziende
    add constraint aziende_donne_non_superano_totale check (
        donne_ruoli_comando <= numero_dipendenti
    );

-- Indici utili
create index if not exists idx_aziende_created_at on public.aziende (created_at desc);
create index if not exists idx_aziende_partita_iva on public.aziende (partita_iva);

