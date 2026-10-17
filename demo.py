from pathlib import Path
import json, threading, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import duckdb

ROOT = Path(__file__).parent
DB = ROOT / 'water_monitor.duckdb'
QUERIES = [
('Pollution after rainfall', '''-- Query 1: Pollution events associated with recent rainfall
SELECT
    wb.water_body_id,
    wb.name,
    pe.change_percent,
    w.rainfall_mm,
    pe.occurred_at
FROM WATER_BODY wb
JOIN POLLUTION_EVENT pe
    ON wb.water_body_id = pe.water_body_id
JOIN WEATHER_RECORD w
    ON pe.location_id = w.location_id
WHERE pe.change_percent > 30
  AND w.rainfall_mm > 0
  AND w.recorded_at <= pe.occurred_at
  AND w.recorded_at >= pe.occurred_at - INTERVAL '24 hours';'''),
('Repeated sensor anomalies', '''-- Query 2: Sensors with multiple anomalous readings
SELECT
    s.sensor_id,
    s.water_body_id,
    COUNT(m.measurement_id) AS anomaly_count
FROM SENSOR s
JOIN MEASUREMENT m
    ON s.sensor_id = m.sensor_id
WHERE m.is_anomalous = TRUE
GROUP BY s.sensor_id, s.water_body_id
HAVING COUNT(m.measurement_id) > 1
ORDER BY anomaly_count DESC;'''),
('Average measurements', '''-- Query 3: Average measurement for each water body
SELECT
    wb.water_body_id,
    wb.name,
    m.parameter_name,
    AVG(m.measured_value) AS average_value,
    COUNT(m.measurement_id) AS total_readings
FROM WATER_BODY wb
JOIN SENSOR s
    ON wb.water_body_id = s.water_body_id
JOIN MEASUREMENT m
    ON s.sensor_id = m.sensor_id
GROUP BY
    wb.water_body_id,
    wb.name,
    m.parameter_name
ORDER BY wb.name;'''),
('Industrial land-use factors', '''-- Query 4: Water bodies associated with industrial factors
SELECT
    wb.water_body_id,
    wb.name AS water_body_name,
    lf.factor_id,
    lf.name AS factor_name,
    lf.factor_type
FROM WATER_BODY wb
JOIN LAND_USE_FACTOR lf
    ON wb.location_id = lf.location_id
WHERE lf.factor_type = 'industrial'
ORDER BY wb.name;'''),
('Pollution and historical states', '''-- Query 5: Pollution events with historical states
SELECT
    pe.pollution_event_id,
    pe.water_body_id,
    pe.occurred_at,
    pe.change_percent,
    hs.valid_from,
    hs.valid_to,
    hs.condition
FROM POLLUTION_EVENT pe
JOIN HISTORICAL_STATE hs
    ON pe.state_id = hs.state_id
WHERE pe.change_percent > 0
ORDER BY pe.occurred_at DESC;'''),
('Year-over-year turbidity trend', '''-- Query 6: Year-over-year turbidity trend
SELECT
    wb.water_body_id,
    wb.name,
    EXTRACT(YEAR FROM m.recorded_at) AS year,
    AVG(m.measured_value) AS avg_turbidity,
    LAG(AVG(m.measured_value)) OVER (
        PARTITION BY wb.water_body_id
        ORDER BY EXTRACT(YEAR FROM m.recorded_at)
    ) AS prev_year_avg,
    ROUND(
        (AVG(m.measured_value) - LAG(AVG(m.measured_value)) OVER (
            PARTITION BY wb.water_body_id
            ORDER BY EXTRACT(YEAR FROM m.recorded_at)
        )) / NULLIF(LAG(AVG(m.measured_value)) OVER (
            PARTITION BY wb.water_body_id
            ORDER BY EXTRACT(YEAR FROM m.recorded_at)
        ), 0) * 100,
        2
    ) AS yoy_change_percent
FROM WATER_BODY wb
JOIN SENSOR s ON wb.water_body_id = s.water_body_id
JOIN MEASUREMENT m ON s.sensor_id = m.sensor_id
WHERE m.parameter_name = 'Turbidity (NTU)'
GROUP BY wb.water_body_id, wb.name, EXTRACT(YEAR FROM m.recorded_at)
ORDER BY wb.name, year;'''),
('Spatial proximity to industry', '''-- Query 7: Water bodies within 2 km of industrial land-use factors (Haversine)
SELECT
    wb.water_body_id,
    wb.name AS water_body_name,
    lf.name AS factor_name,
    lf.factor_type,
    ROUND(
        6371 * 2 * ASIN(SQRT(
            POWER(SIN(RADIANS(l_wb.latitude - l_lf.latitude) / 2), 2) +
            COS(RADIANS(l_wb.latitude)) * COS(RADIANS(l_lf.latitude)) *
            POWER(SIN(RADIANS(l_wb.longitude - l_lf.longitude) / 2), 2)
        )),
        3
    ) AS distance_km
FROM WATER_BODY wb
JOIN LOCATION l_wb ON wb.location_id = l_wb.location_id
CROSS JOIN LAND_USE_FACTOR lf
JOIN LOCATION l_lf ON lf.location_id = l_lf.location_id
WHERE lf.factor_type = 'industrial'
  AND 6371 * 2 * ASIN(SQRT(
        POWER(SIN(RADIANS(l_wb.latitude - l_lf.latitude) / 2), 2) +
        COS(RADIANS(l_wb.latitude)) * COS(RADIANS(l_lf.latitude)) *
        POWER(SIN(RADIANS(l_wb.longitude - l_lf.longitude) / 2), 2)
    )) <= 2
ORDER BY distance_km;'''),
('Computed anomaly detection', '''-- Query 8: Computed anomaly detection — readings > 2 standard deviations above sensor mean
SELECT
    s.sensor_id,
    wb.name AS water_body_name,
    m.parameter_name,
    m.measured_value,
    m.recorded_at,
    m.is_anomalous AS stored_flag,
    ROUND(sensor_stats.mean_val, 2) AS sensor_mean,
    ROUND(sensor_stats.std_val, 2) AS sensor_std,
    CASE WHEN m.measured_value > sensor_stats.mean_val + 2 * sensor_stats.std_val
         THEN TRUE ELSE FALSE END AS computed_anomaly
FROM MEASUREMENT m
JOIN SENSOR s ON m.sensor_id = s.sensor_id
JOIN WATER_BODY wb ON s.water_body_id = wb.water_body_id
JOIN (
    SELECT sensor_id, AVG(measured_value) AS mean_val, STDDEV(measured_value) AS std_val
    FROM MEASUREMENT
    GROUP BY sensor_id
) sensor_stats ON m.sensor_id = sensor_stats.sensor_id
WHERE m.measured_value > sensor_stats.mean_val + 2 * sensor_stats.std_val
ORDER BY s.sensor_id, m.recorded_at;''')]

SCHEMA = (ROOT / '01_schema.sql').read_text(encoding='utf-8')
SEED_MAIN = (ROOT / '02_seed.sql').read_text(encoding='utf-8').split('\nINSERT INTO MEASUREMENT')[0]  # just the non-measurement seed

def setup():
    if DB.exists():
        return
    con = duckdb.connect(str(DB))
    con.execute(SCHEMA)
    con.execute(SEED_MAIN)
    rows = []
    for sensor, base, anomalies in [(101,24,3),(102,6.8,0),(201,19,2),(301,8,1),(401,11,0)]:
        for year in range(2022,2027):
            for n in range(4):
                flag = year == 2026 and n < anomalies
                value = round(base + (year-2022)*(.15 if sensor==102 else 1.2) + n*(.04 if sensor==102 else 1.7) + (12 if flag else 0),2)
                rows.append((len(rows)+1,sensor,'pH' if sensor==102 else 'Turbidity (NTU)',value,f'{year}-10-{10+n:02d} 10:00:00',flag))
    con.executemany('INSERT INTO MEASUREMENT VALUES (?,?,?,?,?,?)', rows)
    con.close()

def run_query(index):
    import time
    con = duckdb.connect(str(DB),read_only=True)
    start = time.perf_counter()
    result = con.execute(QUERIES[index][1])
    columns = [c[0] for c in result.description]
    rows = result.fetchall()
    elapsed = (time.perf_counter()-start)*1000
    con.close()
    return dict(columns=columns,rows=rows,ms=round(elapsed,2),sql=QUERIES[index][1],title=QUERIES[index][0])

HTML = '''<!doctype html><html><head><meta charset="utf-8"><title>AquaTrace | SQL Workbench</title><style>
*{box-sizing:border-box}body{margin:0;background:#0b1220;color:#e6edf6;font:15px 'Segoe UI',sans-serif}header{padding:25px 40px;border-bottom:1px solid #263248;display:flex;justify-content:space-between;align-items:center}.brand{font-size:25px;font-weight:700;color:#55ddd0}.sub{color:#8fa3be;font-size:13px;margin-top:6px}.status{color:#70e0b2;font-size:13px}main{padding:24px 40px}.stats{display:flex;gap:16px;margin-bottom:26px}.stat{background:#121f32;border:1px solid #263248;border-radius:10px;padding:15px 24px;flex:1}.stat b{font-size:26px;display:block}.stat span{font-size:12px;color:#9caec5}.layout{display:grid;grid-template-columns:245px 1fr;gap:24px}nav button{display:block;width:100%;padding:17px 15px;text-align:left;background:#121f32;color:#c7d5e8;border:1px solid #263248;margin-bottom:10px;border-radius:8px;cursor:pointer}nav button.active{border-color:#42cbbd;background:#123337;color:#7eeadd}h2{margin:0 0 6px;font-size:23px}.explain{color:#a2b4cd;margin:0 0 18px;line-height:1.6}.panel{background:#101c2e;border:1px solid #27364c;border-radius:10px;overflow:hidden}.bar{padding:12px 18px;background:#17263b;display:flex;justify-content:space-between;align-items:center}pre{margin:0;padding:18px 24px;color:#9cd8ef;line-height:1.45;font:13px Consolas,monospace;max-height:320px;overflow:auto}#run{border:0;border-radius:6px;background:#43d3bf;color:#092426;font-weight:700;padding:10px 22px;cursor:pointer}.results{margin-top:20px;overflow:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:13px 15px;border-bottom:1px solid #263248;white-space:nowrap}th{color:#8ca5c4;font-size:11px;text-transform:uppercase;background:#142339}td{color:#d8e6f6}tr:hover{background:#192b40}.note{color:#92a9c5;font-size:12px;margin-top:14px}#meta{color:#70e0b2;font-size:13px}
</style></head><body><header><div><div class="brand">◉ AquaTrace</div><div class="sub">Spatiotemporal Database for Intelligent Water Body Monitoring and Anomaly Analysis</div></div><div class="status">● Local database connected · DuckDB</div></header><main><div class="stats"><div class="stat"><b>4</b><span>WATER BODIES</span></div><div class="stat"><b>5</b><span>ACTIVE SENSORS</span></div><div class="stat"><b>100</b><span>MEASUREMENTS · 2022–2026</span></div><div class="stat"><b>8</b><span>ANALYTICAL QUERIES</span></div></div><div class="layout"><nav id="nav"></nav><section><h2 id="title"></h2><p class="explain" id="explain"></p><div class="panel"><div class="bar"><span>SQL editor · queries.sql</span><button id="run" onclick="execute()">▶ Execute query</button></div><pre id="sql"></pre></div><div class="panel results"><div class="bar"><b>Query results</b><span id="meta"></span></div><div id="output"></div></div><p class="note" id="note"></p></section></div></main><script>
const queries=__QUERIES__;
const descriptions=['Joins pollution events with rainfall at the same location during the preceding 24 hours. Filters for pollution increases above 30%.','Groups anomalous measurements by sensor and retains sensors with more than one flagged reading.','Calculates the average for each water body and parameter across all recorded measurements.','Finds industrial land-use factors sharing the water body’s registered location.','Links each pollution event to its historical state, including the state’s validity period.','Calculates annual average turbidity per water body and computes Year-over-Year (YoY) percentage change using window functions.','Computes geodesic distance using the Haversine formula to identify industrial factors within 2 km of water bodies.','Performs statistical anomaly detection using mean + 2σ threshold per sensor across time-series measurements.'];
const notes=['A temporal association indicates co-occurrence; it does not establish rainfall as the cause.','Anomaly flags are stored in MEASUREMENT; this query counts them rather than computing them.','Parameters are grouped separately so different measurement units are never averaged together.','This query uses matching location IDs. A 2 km proximity search would require a distance predicate.','NULL valid_to denotes a currently open historical state.','Uses LAG() OVER PARTITION BY to evaluate year-over-year water quality trajectory.','Accurately calculates spherical distance on WGS84 coordinates without GIS extensions.','Demonstrates computed statistical detection rather than relying strictly on stored flags.'];
let selected=0;
function esc(s){return String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')}
function select(i){selected=i;document.querySelectorAll('nav button').forEach((b,j)=>b.classList.toggle('active',j===i));document.getElementById('title').textContent=`Query ${i+1} · ${queries[i][0]}`;document.getElementById('explain').textContent=descriptions[i]||'';document.getElementById('sql').textContent=queries[i][1];document.getElementById('note').textContent=notes[i]||'';execute()}
async function execute(){const i=selected;document.getElementById('meta').textContent='Executing…';try{const response=await fetch('/api/query/'+i);if(!response.ok)throw Error(await response.text());const data=await response.json();if(i!==selected)return;document.getElementById('meta').textContent=`✓ ${data.rows.length} rows · ${data.ms} ms · Executed successfully`;document.getElementById('output').innerHTML='<table><thead><tr>'+data.columns.map(c=>'<th>'+esc(c)+'</th>').join('')+'</tr></thead><tbody>'+data.rows.map(r=>'<tr>'+r.map(v=>'<td>'+esc(v===null?'NULL':typeof v==='number'&&!Number.isInteger(v)?v.toFixed(2):v)+'</td>').join('')+'</tr>').join('')+'</tbody></table>'}catch(e){document.getElementById('meta').textContent='Error: '+e.message}}
document.getElementById('nav').innerHTML=queries.map((q,i)=>`<button onclick="select(${i})">0${i+1} &nbsp; ${q[0]}</button>`).join('');select(0);
</script></body></html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/query/'):
            try:
                index=int(self.path.rsplit('/',1)[-1])
                if not 0 <= index < len(QUERIES): raise ValueError('Invalid query')
                data=json.dumps(run_query(index),default=str).encode()
                self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data)
            except Exception as e:
                self.send_error(400,str(e))
        else:
            self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(HTML.replace('__QUERIES__',json.dumps(QUERIES)).encode())
    def log_message(self,*args): pass

if __name__=='__main__':
    import sys
    setup()
    (ROOT/'queries.sql').write_text('\n\n'.join(q[1] for q in QUERIES),encoding='utf-8')
    reports=[]
    for i in range(len(QUERIES)):
        result=run_query(i)
        assert result['rows'], f'Query {i+1} produced no rows'
        print(f"Query {i+1}: {result['title']} - {len(result['rows'])} rows ({result['ms']} ms)",flush=True)
        reports.append(result)
    assert [len(r['rows']) for r in reports] == [2, 2, 5, 3, 5, 20, 3, 5]
    (ROOT/'results.json').write_text(json.dumps(reports,default=str,indent=2),encoding='utf-8')
    if '--check' not in sys.argv:
        print('Open http://127.0.0.1:8765 — Ctrl+C to stop',flush=True)
        ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
