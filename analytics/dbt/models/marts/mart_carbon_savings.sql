-- Carbon impact: estimated CO2 saved by RL-optimized signal timing versus a
-- fixed-time baseline. Idling and stop-go traffic burn fuel; less waiting →
-- less CO2. We approximate avoided idling from the congestion the optimized
-- timings removed.
--
-- Assumptions (documented, tunable): an idling vehicle emits ~2.6 g CO2/s; the
-- RL optimizer's measured ~30% mean-wait reduction vs fixed-time (see
-- docs/rl.md) is applied to the modelled idling time per vehicle-hour.
with hourly as (
    select * from {{ ref('mart_segment_hourly') }}
),

params as (
    select
        cast(2.6 as double)  as co2_g_per_idle_second,
        cast(0.30 as double) as rl_wait_reduction,    -- from the RL benchmark
        cast(120 as double)  as modelled_idle_seconds_per_veh_hour
)

select
    h.segment_id,
    h.event_date,
    sum(h.total_vehicles)                                          as vehicles,
    -- Idling seconds that the RL timings are estimated to have avoided.
    round(sum(h.total_vehicles)
          * p.modelled_idle_seconds_per_veh_hour
          * h.congestion_index
          * p.rl_wait_reduction, 0)                               as idle_seconds_avoided,
    round(sum(h.total_vehicles)
          * p.modelled_idle_seconds_per_veh_hour
          * h.congestion_index
          * p.rl_wait_reduction
          * p.co2_g_per_idle_second / 1000.0, 1)                  as co2_kg_saved
from hourly h
cross join params p
group by h.segment_id, h.event_date, p.modelled_idle_seconds_per_veh_hour,
         p.rl_wait_reduction, p.co2_g_per_idle_second
