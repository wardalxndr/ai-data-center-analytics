select owner, sum(current_power_mw) as total_mw
from {{ ref('stg_data_centers') }}
where owner is not null
group by owner order by total_mw desc limit 10