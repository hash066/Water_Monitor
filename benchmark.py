"""Benchmark analytical query performance with and without secondary indexes."""
import time
import statistics
import duckdb
from demo import QUERIES, ROOT

def load_db(with_indexes=True):
    con = duckdb.connect(':memory:')
    schema = (ROOT / '01_schema.sql').read_text(encoding='utf-8')
    seed = (ROOT / '02_seed.sql').read_text(encoding='utf-8')
    
    if not with_indexes:
        schema_lines = [line for line in schema.splitlines() if not line.strip().startswith('CREATE INDEX')]
        schema = '\n'.join(schema_lines)
    
    con.execute(schema)
    for statement in seed.split(';'):
        statement = statement.strip()
        if statement:
            con.execute(statement + ';')
    return con

def bench(con, iterations=50):
    results = []
    for title, sql in QUERIES:
        # Warmup
        con.execute(sql).fetchall()
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            con.execute(sql).fetchall()
            times.append((time.perf_counter() - start) * 1000)
        results.append((title, statistics.mean(times), statistics.stdev(times)))
    return results

if __name__ == '__main__':
    print('=' * 85)
    print('AQUATRACE QUERY PERFORMANCE BENCHMARK (DuckDB in-memory, 50 iterations)')
    print('=' * 85)
    
    con_no = load_db(with_indexes=False)
    no_idx = bench(con_no)
    con_no.close()
    
    con_yes = load_db(with_indexes=True)
    with_idx = bench(con_yes)
    con_yes.close()
    
    print(f"{'#':<3} {'Query Title':<35} {'No Index (ms)':>15} {'With Index (ms)':>16} {'Ratio':>10}")
    print('-' * 85)
    for i, ((title, no_mean, no_std), (_, yes_mean, yes_std)) in enumerate(zip(no_idx, with_idx), 1):
        ratio = no_mean / yes_mean if yes_mean > 0 else 1.0
        print(f"Q{i:<2} {title:<35} {no_mean:>11.3f} ms {yes_mean:>12.3f} ms {ratio:>9.2f}x")
    print('=' * 85)
    print("Note: On small demonstration datasets (100 rows), in-memory scan speeds dominate.")
    print("Secondary index benefits scale significantly as measurement tables grow > 100k rows.")
