

  create or replace view `epoch-ai-data-center`.`epoch_ai_dataset`.`mart_yearly_power`
  OPTIONS()
  as select extract(year from date) as tahun, sum(power_mw) as total_mw
from `epoch-ai-data-center`.`epoch_ai_dataset`.`timelines`
where date is not null
group by tahun order by tahun;

