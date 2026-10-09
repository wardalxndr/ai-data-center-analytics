with first_seen as (
  select data_center, min(cast(date as date)) as start_date from {{ source('epoch','timelines') }} group by data_center
),
peak as (
  select data_center, max(power_mw) as peak_mw from {{ source('epoch','timelines') }} group by data_center
),
peak_date as (
  select t.data_center, min(cast(t.date as date)) as peak_date from {{ source('epoch','timelines') }} t
  join peak p on t.data_center=p.data_center and t.power_mw=p.peak_mw
  group by t.data_center
)
select extract(year from f.start_date) as tahun, avg(date_diff(p.peak_date, f.start_date, day)) as avg_days
from first_seen f join peak_date p on f.data_center=p.data_center
group by tahun order by tahun