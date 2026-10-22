# RVCE DBMS Lab (CD2521A) — Pen-and-Paper Drawing & Write-Up Guide (With "Outcome" Symbols)

> **Important Lab Rule:**
> Your lab syllabus specifically requires **5 DFD Symbols**:
> 1. **External Entity** (Rectangle)
> 2. **Process** (Circle)
> 3. **Data Store** (Rounded Rectangle / Open parallel lines)
> 4. **Outcome / Decision** (Diamond ◊)
> 5. **Data Flow** (Directed Arrow →)

---

# SECTION 1: WHAT TO DRAW ON THE LEFT PAGE (UNRULED)

## Diagram 1: The 5 DFD Symbols Legend
*(Draw this at the top of your drawing sheet)*

```
+-----------------------------------------------------------------------------------------+
|                               DFD NOTATION LEGEND (5 SYMBOLS)                           |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  1. EXTERNAL ENTITY           2. PROCESS               3. DATA STORE                    |
|     +------------------+         .-------------.         .-------------------.          |
|     |  ENTITY NAME     |        /     1.0       \       (   D1: STORE NAME    )         |
|     | (Source / Sink)  |       |   Process Name  |       '-------------------'          |
|     +------------------+        \               /       (Rounded Rectangle /            |
|                                  '-------------'         open parallel lines)           |
|                                                                                         |
|  4. OUTCOME (Decision Branch)                          5. DATA FLOW                     |
|            /\                                                                           |
|           /  \   Evaluation / Outcome                     ------------------------>     |
|          <    >  Condition (Yes / No)                       (Directed Labeled Arrow)    |
|           \  /                                                                          |
|            \/                                                                           |
+-----------------------------------------------------------------------------------------+
```

---

## Diagram 2: Level 0 DFD — Context Diagram
*Context level showing high-level system boundaries, inputs, and outputs.*

```
                               +-----------------------------+
                               |     METEOROLOGICAL STATION  |
                               +-----------------------------+
                                              |
                                              | precipitation_record
                                              | (location_id, rainfall_mm, time)
                                              v
+-----------------------+              .--------------.              +--------------------------+
|    IoT SENSOR NODE    |  telemetry  /      0.0       \  alert_msg  | POLLUTION CONTROL BOARD  |
|   (Field Hardware)    |----------->|    AQUATRACE     |----------->|  (Environmental Officer) |
+-----------------------+  (sensor_id|  WATER MONITORING| (event_id, +--------------------------+
                            param,val|     SYSTEM       |  wb_name,
                            timestamp)\                /   change_pct)
                                       '--------------'
                                           ^        |
                              query_filter |        | trend_visualizations
                              (wb_id, year)|        | geo_coordinates
                                           |        v
                               +-----------------------------+
                               |   CATCHMENT ANALYST / USER  |
                               +-----------------------------+
```

---

## Diagram 3: Level 1 DFD — Subsystems with "Outcome" Decision Nodes
*Shows the 5 sub-processes, Data Stores (D1–D8), and explicit **Outcome (Diamond)** decision branches.*

```
   [ IoT Sensor ]                     [ Weather Station ]              [ Field Inspector ]
         |                                     |                                |
         | raw_reading                         | rainfall_mm                    | findings, date
         v                                     v                                v
  .--------------.                      .--------------.                 .--------------.
 /      1.0       \                    /      2.0       \               /      3.0       \
| Ingest Telemetry |                  |  Log Weather   |               | Record Field   |
 \                /                    \                /               \                /
  '--------------'                      '--------------'                 '--------------'
         |                                     |                                |
         v                                     |                                v
        /\                                     |                               /\
       /  \  Valid Sensor ID?                  |                              /  \  Severe Runoff?
      < O1 >                                   |                             < O2 >
       \  /                                    |                              \  /
        \/                                     |                               \/
    [YES]|  \[NO: Reject Error]                |                           [YES]|  \[NO: Routine]
         |                                     |                                |   |
         v                                     v                                v   v
   +-----------+                        +---------------+                 +-------------+
   |D1|MEASURE |                        |D3| WEATHER_REC|                 |D5|HIST_STATE|
   +-----------+                        +---------------+                 +-------------+
         |                                     |                   (State -> 'Deteriorating')
         | telemetry_stream                    | 24h_rainfall                   ^
         |                                     |                                |
         +-------------------+                 |                                |
                             |                 |                                |
                             v                 v                                |
                          .------------------------.                            |
                         /           4.0            \                           |
                        | Detect Anomalies & Spikes  |                          |
                         \                          /                           |
                          '------------------------'                            |
                                       |                                        |
                                       v                                        |
                                      /\                                        |
                                     /  \  Rainfall > 0 &                       |
                                    < O3 > Change > 30%?                        |
                                     \  /                                       |
                                      \/                                        |
                                  [YES]|  \[NO: Regular Flag]                   |
                                       |                                        |
                        +--------------+-------------------+                    |
                        | write incident                   | update state       |
                        v                                  +--------------------+
                 +---------------+                                  |
                 |D6|POLLUTION_EV|                                  | alert_dispatch
                 +---------------+                                  v
                        |                                 [ Pollution Officer ]
                        | event_history
                        v
                     .----------------------------------.
                    /                5.0                 \ <----- [ Catchment Analyst ]
                   |     Spatial, Statistical & Trend     |       query_filter (wb_id, year)
                   |               Analytics              | -----> dashboard_metrics & CSV
                    \                                    /
                     '----------------------------------'
                        ^                      ^
                        | read coords          | read factors
                 +---------------+      +---------------+
                 |D7| WATER_BODY |      |D8|LAND_USE_FAC|
                 +---------------+      +---------------+
```

---

## Diagram 4: Level 2 DFD — Detailed Decomposition of Process 4.0 with Outcomes
*(This is where the Outcome symbol gives you 10/10 marks)*

```
[ D1: MEASUREMENT ] -----------------> .----------------------------------.
                                      /                4.1                 \
                                     |   Compute Sensor Baseline Statistics |
                                     |   (Rolling Mean & Std Deviation)     |
                                      \                                    /
                                       '----------------------------------'
                                                        |
                                                        | baseline: mean, std
                                                        v
[ D1: MEASUREMENT ] (current_val) ---> .----------------------------------.
                                      /                4.2                 \
                                     |      Compare with 2-Sigma Limit      |
                                      \                                    /
                                       '----------------------------------'
                                                        |
                                                        v
                                                       /\
                                                      /  \  Value > (Mean + 2*Std)?
                                                     < O4 > 
                                                      \  /
                                                       \/
                                 [YES: Flagged Spike]  /    \  [NO: Normal Observation]
                                      +---------------+      +----------------------------+
                                      |                                                   |
                                      v                                                   v
                       .----------------------------------.                     .-------------------.
                      /                4.3                 \                   (  Retain Normal Log  )
                     |     Check Preceding 24h Rainfall     |                   '-------------------'
                      \                                    /
                       '----------------------------------'
                         ^
                         | read rainfall_mm
                  +---------------+
                  |D3| WEATHER_REC|
                  +---------------+
                         |
                         v
                        /\
                       /  \  Rainfall > 0 mm AND
                      < O5 > Change % > 30%?
                       \  /
                        \/
             [YES: Critical Incident]  \
             +-------------------------+ \ [NO: Local Anomaly Only]
             |                           |
             v                           v
      .--------------.            .--------------.
     /      4.4       \          /      4.5       \
    | Log Pollution    |        | Set Sensor Flag |
    | Incident & Alert |        |  'Review Req'   |
     \                /          \                /
      '--------------'            '--------------'
       |       |      \                  |
       |       |       \                 v
       v       |        \          [ D1: Update flag ]
+-----------+  |         \
|D6| POLL_EV|  |          v
+-----------+  |    [ Pollution Board ]
               v
         +-----------+
         |D5| HIST_ST| (Condition -> 'Deteriorating')
         +-----------+
```

---

# SECTION 2: EXPLANATION OF "OUTCOME" NODES FOR YOUR WRITTEN SHEET

When writing the DFD explanation on your ruled page, include this exact subsection:

### Outcome / Decision Specifications:
1. **Outcome $O_1$ (Sensor Credential Validation):**
   - **Condition:** Does incoming `sensor_id` exist in `D2: SENSOR`?
   - **Outcomes:**
     - `[YES]` → Proceed to insert into `D1: MEASUREMENT`.
     - `[NO]` → Reject telemetry as unrecognized hardware error.

2. **Outcome $O_2$ (Severity of Field Inspection):**
   - **Condition:** Does the inspector report visible runoff, oil slicks, or critical contamination?
   - **Outcomes:**
     - `[YES]` → Terminate current historical state (`valid_to = NOW`) and open a new state with condition `'Deteriorating'`.
     - `[NO]` → Preserve existing historical condition (`'Stable'` / `'Recovering'`).

3. **Outcome $O_3$ / $O_5$ (Pollution Event Trigger):**
   - **Condition:** Is `rainfall_mm > 0` in preceding 24 hours AND `change_percent > 30%`?
   - **Outcomes:**
     - `[YES]` → Trigger critical incident: write to `D6: POLLUTION_EVENT`, transition `HISTORICAL_STATE`, and dispatch alert to Pollution Control Board.
     - `[NO]` → Record as isolated sensor deviation without escalating to multi-agency pollution event.

4. **Outcome $O_4$ (Statistical Anomaly Decision):**
   - **Condition:** Is $\text{measured\_value} > \mu + 2\sigma$?
   - **Outcomes:**
     - `[YES]` → Set `is_anomalous = TRUE`.
     - `[NO]` → Set `is_anomalous = FALSE`.
