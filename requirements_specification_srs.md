# Software & Hardware Requirements Specification (SRS)
**Project Title:** AquaTrace — Spatiotemporal Water Body Monitoring Database System  
**Course:** Database Management Systems Lab (CD2521A) — RVCE Department of CSE  
**Standard:** IEEE 830-1998 Recommended Practice for SRS

---

## 1. System Overview & Scope
**AquaTrace** is a high-performance spatiotemporal environmental database management system designed to collect, process, analyze, and visualize longitudinal water quality telemetry, meteorological observations, land-use environmental pressures, and pollution incidents across multiple catchment regions.

The system bridges low-latency embedded relational storage (DuckDB) with analytical window functions, great-circle geographic distance calculations, dynamic two-sigma ($2\sigma$) statistical anomaly detection, and an interactive web dashboard.

---

## 2. Hardware Requirements

### 2.1 Minimum Hardware Requirements (Client & Development Server)
| Component | Specification | Description |
| :--- | :--- | :--- |
| **Processor (CPU)** | Intel Core i3 / AMD Ryzen 3 (10th Gen or higher, Dual-Core 2.0 GHz) | Required for relational query execution and in-memory vectorized calculations |
| **System Memory (RAM)** | 4 GB DDR4 | Sufficient for running the embedded database engine and HTTP server |
| **Storage (Disk space)** | 500 MB free space (SSD recommended) | Database file (`.duckdb`), synthetic seed files, query cache, and log files |
| **Display Resolution** | $1366 \times 768$ pixels | Standard HD resolution for the responsive SVG dashboard |
| **Input Devices** | Standard Keyboard and Mouse / Trackpad | User interaction with the workbench and filter controls |
| **Network Interface** | Standard Loopback (`127.0.0.1` / `localhost`) or 10/100 Mbps NIC | Local socket communication over TCP port 8765 / 8766 |

### 2.2 Recommended Hardware Requirements (Production / Benchmark Environment)
| Component | Specification | Description |
| :--- | :--- | :--- |
| **Processor (CPU)** | Intel Core i5 / i7 or AMD Ryzen 5 / 7 (Quad-Core or higher, 2.8+ GHz) | Parallel query processing and multi-threaded analytical joins |
| **System Memory (RAM)** | 8 GB or 16 GB DDR4/DDR5 | Optimal for in-memory column-vector caching during multi-iteration benchmarks |
| **Storage (Disk space)** | 10 GB NVMe SSD | Ultra-low latency I/O for large historical time-series datasets (> 100k rows) |
| **Display Resolution** | $1920 \times 1080$ Full HD | Optimal layout for simultaneous side-by-side geographic and chart views |

---

## 3. Software Requirements

| Category | Technology / Specification | Version / Standard |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 / 11 (64-bit), Ubuntu Linux 20.04+, or macOS Monterey+ | Cross-platform compatibility |
| **Database Management System**| **DuckDB** (Columnar Embedded Analytical Relational Database) | `v0.9.0` or higher |
| **Backend Runtime** | Python Runtime Environment | Python `3.9.x` to `3.12.x` |
| **Standard Libraries** | Python built-ins: `http.server`, `urllib`, `json`, `time`, `statistics`, `unittest` | Zero-dependency footprint |
| **Web Server / Architecture** | Multi-threaded HTTP Server (`ThreadingHTTPServer`) | Protocol: HTTP/1.1 (Ports: 8765, 8766) |
| **Frontend Technologies** | HTML5, CSS3 (CSS Variables, Responsive Flexbox/Grid), Vanilla JavaScript (ES6+) | No heavy external JS frameworks; zero build overhead |
| **Visualization Components** | Scalable Vector Graphics (SVG), WGS-84 Coordinate Mapper | Interactive SVG geometric plots |
| **IDE / Development Tools** | Visual Studio Code, Git Version Control | Python Extension, VS Code Tasks |

---

## 4. Functional Requirements (FR)

Functional requirements define the specific actions, workflows, and computations the system must execute.

- **FR-01: Multi-Entity Relational Data Storage**
  - The database must persist and enforce relational integrity constraints across 9 entities: `LOCATION`, `WATER_BODY`, `SENSOR`, `MEASUREMENT`, `WEATHER_RECORD`, `LAND_USE_FACTOR`, `HISTORICAL_STATE`, `POLLUTION_EVENT`, and `INSPECTION`.
  - All foreign keys must enforce referential integrity (`REFERENCES` constraints).

- **FR-02: Time-Series Telemetry Ingestion**
  - The system must capture chronological sensor observations including `sensor_id`, parameter name (e.g., Turbidity in NTU, pH), measured numerical value, timestamp, and boolean anomaly flag.

- **FR-03: Meteorological Correlation**
  - The system must record precipitation readings (`rainfall_mm`) per location and query for co-occurring rainfall in the preceding 24-hour interval (`INTERVAL '24 hours'`) of a recorded pollution incident.

- **FR-04: Multi-Year Window Trend Analysis (YoY Turbidity)**
  - The system must compute annual average turbidity per water body and calculate the Year-over-Year (YoY) percentage change using the SQL window function `LAG() OVER (PARTITION BY ... ORDER BY ...)`.

- **FR-05: Geodesic Spatial Proximity Calculation**
  - The system must compute spherical distances between water body coordinates and industrial land-use coordinates using the **Haversine trigonometric formula**:
    $$d = 2R \cdot \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$
  - The system must filter and identify facilities situated within $\le 2.0\text{ km}$.

- **FR-06: Algorithmic Anomaly Detection ($2\sigma$ Threshold)**
  - The system must dynamically compute sensor baseline statistics (mean $\mu$ and standard deviation $\sigma$) and flag time-series measurements where:
    $$\text{measured\_value} > \mu + 2\sigma$$

- **FR-07: Historical State & Validity Interval Tracking**
  - The system must maintain temporal validity intervals (`valid_from` to `valid_to`) for water body condition labels (`Stable`, `Deteriorating`, `Under observation`, `Recovering`). A `NULL` in `valid_to` represents a currently open active state.

- **FR-08: Field Inspection Register**
  - The system must allow recording field observations and linking qualitative findings to the corresponding water body.

- **FR-09: Interactive Dashboard & Filtering**
  - The web user interface must provide dynamic filtering by water body and observation year (2022–2026), updating statistics, SVG maps, and trend graphs without page reloads.

- **FR-10: Client-Side Data Export (CSV Export)**
  - The system must allow users to download the tabular data (sensors, pollution events, environmental factors, and analytical query outputs) directly as standardized `.csv` files.

- **FR-11: Custom Alert Threshold Configuration**
  - The dashboard must provide a user-configurable turbidity threshold (NTU) that immediately flags and highlights out-of-spec telemetry on the interface.

---

## 5. Non-Functional Requirements (NFR)

Non-functional requirements describe system qualities, performance benchmarks, and operational constraints.

- **NFR-01: Query Execution Performance (Latency)**
  - Analytical and relational queries against the in-memory or persisted DuckDB database must execute within **$< 50\text{ ms}$** under normal operating loads.
  - The web interface must render dataset changes in under **$100\text{ ms}$**.

- **NFR-02: Data Integrity & ACID Compliance**
  - The database engine must guarantee strict **ACID** (Atomicity, Consistency, Isolation, Durability) properties for all transactions.
  - Primary key uniqueness and foreign key references must be maintained without orphaned records.

- **NFR-03: Normalization Standard (Schema Quality)**
  - All 9 relational tables must strictly satisfy **Boyce-Codd Normal Form (BCNF)** and **Third Normal Form (3NF)**, ensuring zero insertion, update, or deletion anomalies.

- **NFR-04: Lightweight Footprint & Zero-Dependency Portability**
  - The system must require zero enterprise database installation (e.g., no bulky PostgreSQL/Oracle background daemon setup).
  - The entire stack must initialize and run with a single Python package (`pip install duckdb`).

- **NFR-05: Usability & User Experience (UX)**
  - The dashboard must be responsive across screen widths ranging from $700\text{ px}$ to $1920\text{ px}$.
  - Tables must provide visual cues (sorting arrows, color-coded status badges, and warning tags for deteriorating conditions).

- **NFR-06: Reliability & Availability**
  - The Python `ThreadingHTTPServer` must handle concurrent browser requests asynchronously without deadlocking or thread starvation.
  - Read-only database connection pooling (`read_only=True`) must prevent file-lock contention during multi-client read requests.

- **NFR-07: Testability & Maintainability**
  - The codebase must be modular with separated concerns (`01_schema.sql`, `02_seed.sql`, `server.py`, `demo.py`, `benchmark.py`).
  - An automated test suite (`test_queries.py`) must validate 100% of analytical queries and table schema counts with exit code 0.
