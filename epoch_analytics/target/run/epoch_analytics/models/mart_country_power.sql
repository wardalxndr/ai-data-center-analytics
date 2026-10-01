

  create or replace view `epoch-ai-data-center`.`epoch_ai_dataset`.`mart_country_power`
  OPTIONS()
  as select country, sum(current_power_mw) as total_mw from `epoch-ai-data-center`.`epoch_ai_dataset`.`stg_data_centers` group by country order by total_mw desc;

