"""Execute the project queries and display their actual database results."""
import argparse
from demo import QUERIES, setup, run_query

def display(value):
    if value is None:
        return 'NULL'
    if isinstance(value, float):
        return f'{value:.2f}'
    return str(value)

def print_table(columns, rows):
    values = [[display(v) for v in row] for row in rows]
    widths = [max(len(column), *(len(row[i]) for row in values)) if values else len(column)
              for i, column in enumerate(columns)]
    rule = '+' + '+'.join('-' * (width + 2) for width in widths) + '+'
    def line(row):
        return '| ' + ' | '.join(v.ljust(w) for v, w in zip(row, widths)) + ' |'
    print(rule)
    print(line(columns))
    print(rule)
    for row in values:
        print(line(row))
    print(rule)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', type=int, choices=range(1, len(QUERIES) + 1), help=f'Run one query (1–{len(QUERIES)})')
    parser.add_argument('--step', action='store_true', help='Press Enter before each query')
    args = parser.parse_args()
    setup()
    print('\nWATER BODY MONITORING | SQL EXECUTION\nDatabase: water_monitor.duckdb | Engine: DuckDB\n')
    for index in ([args.query - 1] if args.query else range(len(QUERIES))):
        if args.step:
            input(f'Press Enter to execute Query {index + 1}...')
        print('=' * 90)
        print(QUERIES[index][1])
        print('\nRESULT')
        result = run_query(index)
        print_table(result['columns'], result['rows'])
        print(f"{len(result['rows'])} rows returned | {result['ms']:.2f} ms | SUCCESS\n")
