-- Hourly performance per segment: the backbone fact table for the BI
-- dashboards (executive overview, segment performance).
with readings as (
    select * from {{ ref('stg_readings') }}
)

select
    segment_id,
    event_date,
    event_hour,
    event_dow,
    count(*)                                    as reading_count,
    round(avg(avg_speed_kmh), 1)                as avg_speed_kmh,
    round(min(avg_speed_kmh), 1)                as min_speed_kmh,
    round(avg(occupancy_pct), 1)                as avg_occupancy_pct,
    sum(vehicle_count)                          as total_vehicles,
    -- A simple congestion index: how far below free-flow the hour ran.
    round(greatest(0, 1 - avg(avg_speed_kmh) / 60.0), 3) as congestion_index
from readings
group by segment_id, event_date, event_hour, event_dow
