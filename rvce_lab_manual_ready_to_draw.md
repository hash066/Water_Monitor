# RVCE DBMS Lab (CD2521A) — Pen-and-Paper Drawing & Write-Up Guide

> **Lab Structure:**
> - **Left Page (Blank / Unruled):** Diagrams to be drawn with pencil, ruler, and stencils (DFD Level 0, Level 1, Level 2, Symbols).
> - **Right Page (Ruled):** Written explanations, tables, Functional Dependencies (FDs), and step-by-step Normalization proofs.

---

# SECTION 1: WHAT TO DRAW ON THE LEFT PAGE (UNRULED)

## Diagram 1: DFD Symbol Legend (Draw at the top of Left Page)
Draw these 4 standard symbols (Gane & Sarson / Yourdon Notation) in a small box:

```
+-----------------------------------------------------------------------------+
|                          DFD NOTATION LEGEND                                |
+-----------------------------------------------------------------------------+
|  1. EXTERNAL ENTITY          2. PROCESS               3. DATA STORE         |
|     +------------------+         .-------------.         +----------------  |
|     |  ENTITY NAME     |        /     1.0       \        | D1 | STORE NAME  |
|     | (Source / Sink)  |       |   Process Name  |       +----------------  |
|     +------------------+        \               /         (Open on right)   |
|                                  '-------------'                            |
|                                                                             |
|  4. DATA FLOW (Directed Arrow with noun label)                              |
|     ------------------ data_attribute_name ------------------>              |
+-----------------------------------------------------------------------------+
```

---

## Diagram 2: Level 0 DFD — Context Diagram
*This shows the entire system as one central process (`0.0`) interacting with external actors.*

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

## Diagram 3: Level 1 DFD — Subsystem & Data Store Decomposition
*Draw this clearly taking the full middle/lower half of the unruled page. Connect processes to Data Stores (D1 through D8).*

```
   [ IoT Sensor ]                     [ Weather Station ]              [ Field Inspector ]
         |                                     |                                |
         | raw_reading                         | rainfall_mm                    | findings, date
         v                                     v                                v
  .--------------.                      .--------------.                 .--------------.
 /      1.0       \                    /      2.0       \               /      3.0       \
| Ingest & Validate|                  |  Log Weather   |               | Record Field   |
| Telemetry Data  |                  |  Observations  |               |  Inspections   |
 \                /                    \                /               \                /
  '--------------'                      '--------------'                 '--------------'
    |           ^                              |                                |       |
    | write     | check                        | write                          | write | update
    v           | status                       v                                v       v
+-----------+ +-----------+             +---------------+              +---------+ +-------------+
|D1|MEASURE | |D2| SENSOR |             |D3| WEATHER_REC|              |D4|INSPEC| |D5|HIST_STATE|
+-----------+ +-----------+             +---------------+              +---------+ +-------------+
    |                                          |                                |       ^
    | telemetry_stream                         | 24h_rainfall                   |       | current
    |                                          |                                |       | condition
    +--------------------+                     |                                |       |
                         |                     |                                |       |
                         v                     v                                |       |
                      .----------------------------------.                      |       |
                     /                4.0                 \                     |       |
                    |      Detect Anomalies & Spikes       |--------------------+-------+
                    |      & Log Pollution Incidents      |  update state to 'Deteriorating'
                     \                                    /
                      '----------------------------------'
                         |                          |
                         | write incident           | alert_notification
                         v                          v
                  +---------------+        [ Pollution Officer ]
                  |D6|POLLUTION_EV|
                  +---------------+
                         |
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

## Diagram 4: Level 2 DFD — Functional Decomposition of Process 4.0
*(RVCE gives the highest rubric band [2 Marks for Design] when Level 2 is drawn!)*

```
[ D1: MEASUREMENT ] -----------------> .----------------------------------.
                                      /                4.1                 \
                                     |   Compute Sensor Baseline Statistics |
                                     |   (Rolling Mean & Std Deviation)     |
                                      \                                    /
                                       '----------------------------------'
                                                        |
                                                        | mean_val, std_val
                                                        v
[ D1: MEASUREMENT ] (current_reading) -> .----------------------------------.
                                        /                4.2                 \
                                       |      Evaluate 2-Sigma Threshold     |
                                       |   (Flag if value > mean + 2*std)    |
                                        \                                    /
                                         '----------------------------------'
                                                        |
                                                        | flag = TRUE (is_anomalous)
                                                        v
[ D3: WEATHER_RECORD ] (rain_24h) ----> .----------------------------------.
                                       /                4.3                 \
                                      |     Correlate Rainfall Window &      |
                                      |         Compute Change %             |
                                       \                                    /
                                        '----------------------------------'
                                                        |
                                                        | rainfall > 0 AND change > 30%
                                                        v
                                        .----------------------------------.
                                       /                4.4                 \
                                      |      Generate Pollution Incident    |
                                      |       & Transition Water State      |
                                       \                                    /
                                        '----------------------------------'
                                           |                 |             |
                         insert event      |    update state |             | dispatch alert
                                           v                 v             v
                                     +-----------+     +-----------+   [ Pollution Board ]
                                     |D6| POLL_EV|     |D5| HIST_ST|
                                     +-----------+     +-----------+
```

---

# SECTION 2: WHAT TO WRITE ON THE RIGHT PAGE (RULED)

Write these exact headings and paragraphs in your lab notebook:

### TITLE:
**Spatiotemporal Water Body Monitoring System (AquaTrace)**

### OBJECTIVE:
To construct Data Flow Diagrams (Level 0, Level 1, Level 2) modeling environmental monitoring data flows, and to normalize the relational schema from Unnormalized Form (UNF) through First (1NF), Second (2NF), Third (3NF), and Boyce-Codd Normal Form (BCNF).

---

## PART A: DFD PROCESS SPECIFICATIONS (P-SPECS)

1. **Process 1.0 (Ingest & Validate Telemetry):**
   - **Input:** Raw telemetry tuple `(sensor_id, parameter_name, measured_value, recorded_at)` from IoT Node.
   - **Logic:** Validate that `sensor_id` exists in `D2: SENSOR`. If valid, append record to `D1: MEASUREMENT` with default `is_anomalous = FALSE`.
   - **Output:** Inserted measurement tuple.

2. **Process 2.0 (Log Weather Observations):**
   - **Input:** Precipitation stream `(location_id, rainfall_mm, recorded_at)` from Weather Station.
   - **Logic:** Verify `location_id`. Write rainfall readings into `D3: WEATHER_RECORD`.
   - **Output:** Validated meteorological record.

3. **Process 3.0 (Record Field Inspections):**
   - **Input:** Inspection entry `(water_body_id, inspected_at, findings)` from Field Officer.
   - **Logic:** Write inspection log to `D4: INSPECTION`. If severe pollution or runoff is reported, update `valid_to` of current state in `D5: HISTORICAL_STATE` and insert new row with condition `'Deteriorating'`.

4. **Process 4.0 (Detect Anomalies & Spikes):**
   - **Input:** Measurement stream from `D1`, rainfall from `D3`, current condition from `D5`.
   - **Logic:** Decomposed into sub-processes 4.1 to 4.4 (Level 2).
   - **Output:** New incident in `D6: POLLUTION_EVENT`, alert notification to Environmental Officer.

5. **Process 5.0 (Spatial & Trend Analytics):**
   - **Input:** Analytical filter `(water_body_id, year)` from Analyst.
   - **Logic:** Executes analytical queries:
     - Query 6: Annual average turbidity with YoY change using `LAG() OVER (...)`.
     - Query 7: Geodesic distance to industrial factors using spherical Haversine formula $\le 2\text{ km}$.
     - Query 8: Statistical anomaly identification exceeding $\mu + 2\sigma$.
   - **Output:** Rendered dashboard views, SVG trend charts, CSV export files.

---

## PART B: STEP-BY-STEP NORMALIZATION PROOF

### 1. Unnormalized Form (UNF)
The initial unnormalized view contains nested multivalued and repeating attributes:

$$\text{WATER\_MONITOR}(\underline{\text{location\_id}}, \text{region}, \text{lat}, \text{long}, \{\text{water\_body\_id}, \text{wb\_name}, \{\text{sensor\_id}, \text{install\_date}, \{\text{meas\_id}, \text{param}, \text{val}, \text{time}, \text{flag}\}\}, \{\text{factor\_id}, \text{factor\_name}, \text{type}\}, \{\text{weather\_id}, \text{rain}, \text{w\_time}\}, \{\text{state\_id}, \text{v\_from}, \text{v\_to}, \text{cond}\}, \{\text{event\_id}, \text{change}, \text{ev\_time}\}, \{\text{insp\_id}, \text{findings}, \text{i\_time}\}\})$$

*Anomalies in UNF:* Redundant storage of coordinates, inability to record a sensor without measurements, deletion of measurements destroying water body data.

---

### 2. First Normal Form (1NF)
> **Definition:** A relation $R$ is in 1NF if and only if all underlying attribute domains are **atomic** (indivisible) and there are **no repeating groups or multivalued arrays**.

**Decomposition into 9 1NF Relations:**
1. `LOCATION` ($\underline{\text{location\_id}}$, $\text{region}$, $\text{latitude}$, $\text{longitude}$)
2. `WATER_BODY` ($\underline{\text{water\_body\_id}}$, $\text{name}$, $\text{location\_id}$)
3. `SENSOR` ($\underline{\text{sensor\_id}}$, $\text{water\_body\_id}$, $\text{installed\_at}$)
4. `MEASUREMENT` ($\underline{\text{measurement\_id}}$, $\text{sensor\_id}$, $\text{parameter\_name}$, $\text{measured\_value}$, $\text{recorded\_at}$, $\text{is\_anomalous}$)
5. `WEATHER_RECORD` ($\underline{\text{weather\_id}}$, $\text{location\_id}$, $\text{rainfall\_mm}$, $\text{recorded\_at}$)
6. `LAND_USE_FACTOR` ($\underline{\text{factor\_id}}$, $\text{location\_id}$, $\text{name}$, $\text{factor\_type}$)
7. `HISTORICAL_STATE` ($\underline{\text{state\_id}}$, $\text{water\_body\_id}$, $\text{valid\_from}$, $\text{valid\_to}$, $\text{condition}$)
8. `POLLUTION_EVENT` ($\underline{\text{pollution\_event\_id}}$, $\text{water\_body\_id}$, $\text{location\_id}$, $\text{state\_id}$, $\text{change\_percent}$, $\text{occurred\_at}$)
9. `INSPECTION` ($\underline{\text{inspection\_id}}$, $\text{water\_body\_id}$, $\text{inspected\_at}$, $\text{findings}$)

*Conclusion:* Every attribute contains single, atomic scalar values. $\Rightarrow$ **1NF Satisfied.**

---

### 3. Second Normal Form (2NF)
> **Definition:** A relation $R$ is in 2NF if:
> 1. It is in 1NF.
> 2. **No non-prime attribute is partially dependent on any candidate key.** (Every non-prime attribute must depend on the *entire* candidate key).

**Proof of 2NF:**
- Partial dependency $A \subset PK \rightarrow Y$ can **only** occur if the primary key is composite ($\ge 2$ attributes).
- In our schema:
  - `LOCATION` Primary Key: $\{\text{location\_id}\}$ (Single attribute)
  - `WATER_BODY` Primary Key: $\{\text{water\_body\_id}\}$ (Single attribute)
  - `SENSOR` Primary Key: $\{\text{sensor\_id}\}$ (Single attribute)
  - `MEASUREMENT` Primary Key: $\{\text{measurement\_id}\}$ (Single attribute)
  - `WEATHER_RECORD` Primary Key: $\{\text{weather\_id}\}$ (Single attribute)
  - `LAND_USE_FACTOR` Primary Key: $\{\text{factor\_id}\}$ (Single attribute)
  - `HISTORICAL_STATE` Primary Key: $\{\text{state\_id}\}$ (Single attribute)
  - `POLLUTION_EVENT` Primary Key: $\{\text{pollution\_event\_id}\}$ (Single attribute)
  - `INSPECTION` Primary Key: $\{\text{inspection\_id}\}$ (Single attribute)
- Because **all candidate keys are single-attribute**, proper subsets do not exist.
- Therefore, **no partial dependency is mathematically possible**. $\Rightarrow$ **2NF Satisfied across all 9 relations.**

---

### 4. Third Normal Form (3NF) & Boyce-Codd Normal Form (BCNF)
> **3NF Definition:** For every non-trivial functional dependency $X \rightarrow Y$:
> - $X$ is a **Super Key**, OR
> - $Y$ is a **Prime Attribute**.
>
> **BCNF Definition:** For every non-trivial functional dependency $X \rightarrow Y$:
> - $X$ **MUST be a Super Key** (Strict condition: no non-superkey determinants permitted).

**Systematic Functional Dependency (FD) Table:**

| Relation | Primary Key (PK) | Functional Dependencies ($X \rightarrow Y$) | Determinant ($X$) Type | Normal Form Achieved |
| :--- | :--- | :--- | :--- | :---: |
| `LOCATION` | `location_id` | $\text{location\_id} \rightarrow \text{region}, \text{latitude}, \text{longitude}$ | Super Key | **BCNF** |
| `WATER_BODY` | `water_body_id` | $\text{water\_body\_id} \rightarrow \text{name}, \text{location\_id}$ | Super Key | **BCNF** |
| `SENSOR` | `sensor_id` | $\text{sensor\_id} \rightarrow \text{water\_body\_id}, \text{installed\_at}$ | Super Key | **BCNF** |
| `MEASUREMENT` | `measurement_id` | $\text{measurement\_id} \rightarrow \text{sensor\_id}, \text{parameter\_name}, \text{measured\_value}, \text{recorded\_at}, \text{is\_anomalous}$ | Super Key | **BCNF** |
| `WEATHER_RECORD` | `weather_id` | $\text{weather\_id} \rightarrow \text{location\_id}, \text{rainfall\_mm}, \text{recorded\_at}$ | Super Key | **BCNF** |
| `LAND_USE_FACTOR`| `factor_id` | $\text{factor\_id} \rightarrow \text{location\_id}, \text{name}, \text{factor\_type}$ | Super Key | **BCNF** |
| `HISTORICAL_STATE`| `state_id` | $\text{state\_id} \rightarrow \text{water\_body\_id}, \text{valid\_from}, \text{valid\_to}, \text{condition}$ | Super Key | **BCNF** |
| `POLLUTION_EVENT`| `pollution_event_id`| $\text{pollution\_event\_id} \rightarrow \text{water\_body\_id}, \text{location\_id}, \text{state\_id}, \text{change\_percent}, \text{occurred\_at}$ | Super Key | **BCNF** |
| `INSPECTION` | `inspection_id` | $\text{inspection\_id} \rightarrow \text{water\_body\_id}, \text{inspected\_at}, \text{findings}$ | Super Key | **BCNF** |

**Transitive Dependency Elimination Proof:**
- In an unnormalized design, `WATER_BODY` might contain `region` and `latitude`:
  $$\text{water\_body\_id} \rightarrow \text{location\_id} \quad \text{and} \quad \text{location\_id} \rightarrow \text{region}$$
  This is a transitive dependency ($\text{Non-Key} \rightarrow \text{Non-Key}$).
- In our normalized schema, `region`, `latitude`, and `longitude` are isolated in `LOCATION`. `WATER_BODY` stores only the foreign key `location_id`.
- Therefore, **no transitive dependency exists**.
- Since in every non-trivial FD the determinant $X$ is a Super Key, **all 9 relations satisfy BCNF and 3NF**.

---

## PART C: VIVA QUESTIONS & INSTANT MEMORY ANSWERS

1. **Q: What is DFD Balancing?**
   > **Ans:** "Sir/Madam, DFD balancing is the principle where all input and output data flows entering and leaving a process bubble at Level $N$ must exactly match the aggregate input and output flows at Level $N+1$. No data flows can mysteriously appear or disappear across levels."

2. **Q: Why cannot an External Entity connect directly to a Data Store?**
   > **Ans:** "Because an external entity has no direct access to internal database tables. All reads and writes must be mediated by a software process bubble that handles authentication, validation, and business logic."

3. **Q: What is the exact mathematical difference between 3NF and BCNF?**
   > **Ans:** "In 3NF, for any FD $X \rightarrow Y$, either $X$ is a super key OR $Y$ is a prime attribute. BCNF is strictly stronger: it disallows the second condition completely—$X$ MUST be a super key for every non-trivial dependency."

4. **Q: How does having single-attribute primary keys guarantee 2NF?**
   > **Ans:** "Partial functional dependency is defined as a non-prime attribute depending on a proper subset of a candidate key ($A \subset PK$). For a single-attribute key, the only proper subset is the empty set ($\emptyset$), so partial dependencies cannot exist."
