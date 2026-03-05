# Forklaring: fra første celle til kørende simulation

Denne guide forklarer, hvad der sker, når du starter notebooks i rækkefølge, og hvordan data flyder mellem agenterne via MQTT.

## Før du starter

Du kører fem notebooks som separate agenter:

1. `notebooks/1_agent_observer.ipynb`
2. `notebooks/2_agent_control.ipynb`
3. `notebooks/3_agent_response.ipynb`
4. `notebooks/4_dashboard.ipynb`
5. `notebooks/5_agent_trigger.ipynb`

Alle notebooks læser `config.yaml` via `simulated_city.config.load_config()`.

## Start-rækkefølge (praktisk workflow)

Start i denne rækkefølge, så alle lyttere er klar før Trigger begynder at sende:

1. Observer: kør Cell 1–4
2. Control: kør Cell 1–4
3. Response: kør Cell 1–4
4. Dashboard: kør Cell 1–5 (Cell 5 holder loopet kørende)
5. Trigger: kør Cell 1–4

Når Trigger kører, er simulationen i gang.

## Hvad der sker i hver notebook

### 1) Observer (`1_agent_observer.ipynb`)

- **Cell 1**: Importerer moduler, læser config og definerer topics.
- **Cell 2**: Opretter distance-funktion og buffer til personer pr. step.
- **Cell 3**: Forbinder til MQTT og abonnerer på Trigger-topic.
- **Cell 4 (message processing via callback)**:
  - Samler personbeskeder pr. step.
  - Beregner afstand mellem infected og susceptible.
  - Publicerer `observer/exposure_event`.
  - Publicerer `observer/city_snapshot` med S/I/R-tællinger.

Observer ændrer ikke health status; den observerer og publicerer afledte data.

### 2) Control (`2_agent_control.ipynb`)

- **Cell 1**: Læser config, topic-kontrakter og epidemiregler.
- **Cell 2**: Initialiserer intern status for personer.
- **Cell 3**: Forbinder til MQTT og abonnerer på:
  - `trigger/person_state`
  - `observer/exposure_event`
- **Cell 4 (callback-logik)**:
  - Tager imod eksponeringer.
  - Anvender transitionsregler: `susceptible -> infected -> recovered`.
  - Publicerer `control/health_update`.

Control er den agent, der ejer statusovergange.

### 3) Response (`3_agent_response.ipynb`)

- **Cell 1**: Læser config og topics.
- **Cell 2**: Initialiserer tællere og per-step hjælpefunktioner.
- **Cell 3**: Forbinder til MQTT og abonnerer på:
  - `observer/city_snapshot`
  - `control/health_update`
- **Cell 4 (callback-logik)**:
  - Opdaterer tællinger baseret på health updates.
  - Publicerer `response/metrics` én gang pr. step.

Response laver by-metrikker, som kan bruges til monitorering.

### 4) Dashboard (`4_dashboard.ipynb`)

- **Cell 1**: Læser config og sætter topic-abonnement op.
- **Cell 2**: Opretter anymap-ts kort og dashboard-state.
- **Cell 3**: Forbinder til MQTT og lægger beskeder i kø.
- **Cell 4**: Starter processing-loop:
  - Bygger step-synkron frame af personer.
  - Opdaterer kortmarkører.
  - Opdaterer SIR-grafen under kortet.
- **Cell 5 (valgfri under kørsel)**: viser kort status for trackede personer.

Dashboard er read-only og træffer ingen kontrolbeslutninger.

### 5) Trigger (`5_agent_trigger.ipynb`)

- **Cell 1**: Læser config, simulationkonstanter og topics.
- **Cell 2**: Initialiserer personer og start-status.
- **Cell 3**: Forbinder til MQTT, simulerer bevægelse og publicerer:
  - `trigger/person_state` for hver person og step.
  - Abonnerer også på `control/health_update` for feedback.
- **Cell 4**: Viser preview og disconnecter rent.

Trigger er motoren, der driver tidssteg fremad.

## Dataflow (kort fortalt)

1. Trigger publicerer rå persontilstande.
2. Observer læser rå data og publicerer eksponeringer + snapshots.
3. Control læser eksponeringer og publicerer health updates.
4. Response læser snapshots + health updates og publicerer metrics.
5. Dashboard viser live kort + SIR-graf ud fra strømmen.

## Hvornår er simulationen "kørende"?

Simulationen er kørende, når disse tre ting sker samtidig:

- Trigger printer step-linjer (`step=...`).
- Observer/Control/Response viser stigende tællere i deres logs.
- Dashboard viser bevægelige markører og opdateret SIR-graf.

## Afslutning (ren nedlukning)

Når du er færdig, kører du summary/cleanup-cellen i hver notebook:

1. Observer sidste celle
2. Control sidste celle
3. Response sidste celle
4. Dashboard sidste celle
5. Trigger sidste celle (hvis ikke allerede kørt)

Så bliver MQTT-forbindelser lukket korrekt.