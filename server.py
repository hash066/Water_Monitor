from demo import ROOT, DB, QUERIES, setup, run_query
import duckdb, json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

def dataset():
    con=duckdb.connect(str(DB),read_only=True)
    def rows(sql):
        cur=con.execute(sql)
        keys=[d[0] for d in cur.description]
        return [dict(zip(keys,r)) for r in cur.fetchall()]
    data={
        'bodies':rows('SELECT wb.*, l.region, l.latitude, l.longitude, hs.condition FROM WATER_BODY wb JOIN LOCATION l USING(location_id) JOIN HISTORICAL_STATE hs ON wb.water_body_id=hs.water_body_id WHERE hs.valid_to IS NULL ORDER BY wb.water_body_id'),
        'measurements':rows('SELECT m.*, s.water_body_id FROM MEASUREMENT m JOIN SENSOR s USING(sensor_id) ORDER BY recorded_at'),
        'events':rows('SELECT pe.*, wb.name, hs.condition FROM POLLUTION_EVENT pe JOIN WATER_BODY wb USING(water_body_id) JOIN HISTORICAL_STATE hs USING(state_id) ORDER BY occurred_at DESC'),
        'weather':rows('SELECT * FROM WEATHER_RECORD ORDER BY recorded_at DESC'),
        'factors':rows('SELECT * FROM LAND_USE_FACTOR'),
        'states':rows('SELECT * FROM HISTORICAL_STATE ORDER BY valid_from DESC'),
        'inspections':rows('SELECT * FROM INSPECTION ORDER BY inspected_at DESC'),
        'sensors':rows('SELECT * FROM SENSOR'),
        'queries':QUERIES
    }
    con.close()
    return data

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path=='/api/data':
                content=json.dumps(dataset(),default=str).encode();kind='application/json'
            elif self.path.startswith('/api/query/'):
                i=int(self.path.rsplit('/',1)[-1])
                if not 0<=i<len(QUERIES): raise ValueError('Invalid query')
                content=json.dumps(run_query(i),default=str).encode();kind='application/json'
            else:
                content=(ROOT/'index.html').read_bytes();kind='text/html; charset=utf-8'
            self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(content)
        except Exception as e:self.send_error(500,str(e))
    def log_message(self,*args):pass

if __name__=='__main__':
    setup()
    ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
