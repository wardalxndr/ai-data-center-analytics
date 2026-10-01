select
  name,
  split(owner, ' #')[offset(0)] as owner,
  country, current_power_mw
from {{ source('epoch','data_centers') }}
where country is not null