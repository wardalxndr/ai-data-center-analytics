select
  name,
  split(owner, ' #')[offset(0)] as owner,
  country, current_power_mw
from `epoch-ai-data-center`.`epoch_ai_dataset`.`data_centers`
where country is not null