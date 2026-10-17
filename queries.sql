-- Query 1: Pollution events associated with recent rainfall
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
  AND w.recorded_at >= pe.occurred_at - INTERVAL '24 hours';

-- Query 2: Sensors with multiple anomalous readings
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
ORDER BY anomaly_count DESC;

-- Query 3: Average measurement for each water body
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
ORDER BY wb.name;

-- Query 4: Water bodies associated with industrial factors
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
ORDER BY wb.name;

-- Query 5: Pollution events with historical states
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
ORDER BY pe.occurred_at DESC;

-- Query 6: Year-over-year turbidity trend
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
ORDER BY wb.name, year;

-- Query 7: Water bodies within 2 km of industrial land-use factors (Haversine)
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
ORDER BY distance_km;

-- Query 8: Computed anomaly detection — readings > 2 standard deviations above sensor mean
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
ORDER BY s.sensor_id, m.recorded_at;