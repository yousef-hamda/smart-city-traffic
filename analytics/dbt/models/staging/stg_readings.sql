-- Cleaned, typed view over raw readings: drop nulls, clamp obviously bad
-- values, and add calendar columns the marts group by.
with source as (
    select * from {{ source('raw', 'readings') }}
)

select
    segment_id,
    sensor_id,
    cast(vehicle_count as integer)              as vehicle_count,
    cast(avg_speed_kmh as double)               as avg_speed_kmh,
    cast(occupancy_pct as double)               as occupancy_pct,
    event_time,
    date(event_time)                            as event_date,
    hour(event_time)                            as event_hour,
    day_of_week(event_time)                     as event_dow
from source
where segment_id is not null
  and avg_speed_kmh between 0 and 200
  and occupancy_pct between 0 and 100
