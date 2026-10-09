select extract(year from cast(date as date)) as tahun, sum(power_mw) as total_mw
from {{ source('epoch','timelines') }}
where date is not null
group by tahun order by tahun