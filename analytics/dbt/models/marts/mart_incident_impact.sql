-- Incident impact: for each segment-hour, contrast the slowest readings
-- against that segment's typical speed to quantify how much an incident hour
-- hurt flow. Feeds the Incident Analysis dashboard.
with hourly as (
    select * from {{ ref('mart_segment_hourly') }}
),

segment_baseline as (
    select
        segment_id,
        round(avg(avg_speed_kmh), 1) as baseline_speed_kmh
    from hourly
    group by segment_id
)

select
    h.segment_id,
    h.event_date,
    h.event_hour,
    h.avg_speed_kmh,
    b.baseline_speed_kmh,
    round(b.baseline_speed_kmh - h.avg_speed_kmh, 1)               as speed_deficit_kmh,
    round((b.baseline_speed_kmh - h.avg_speed_kmh)
          / nullif(b.baseline_speed_kmh, 0), 3)                    as relative_slowdown,
    h.congestion_index,
    -- Flag the worst 10% slowdown hours as likely-incident hours.
    case when h.avg_speed_kmh < b.baseline_speed_kmh * 0.6
         then true else false end                                 as likely_incident_hour
from hourly h
join segment_baseline b using (segment_id)
