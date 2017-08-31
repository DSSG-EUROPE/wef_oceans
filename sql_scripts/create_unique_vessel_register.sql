CREATE SCHEMA unique_vessel;
create table unique_vessel.aggregated_register
as(
	SELECT mmsi, COUNT(*) as count_ais_position_yr 
	FROM ais_messages.full_year_position
	GROUP BY mmsi
	ORDER BY count_ais_position_yr desc
	);
	
create table unique_vessel.aggregated_register_static
as(
	SELECT mmsi, COUNT(*) as count_ais_static_yr 
	FROM ais_messages.full_year_static
	GROUP BY mmsi
	ORDER BY count_ais_static_yr desc
	);

create table unique_vessel.aggregated_register
as(
	SELECT p.count_ais_position_yr, s.count_ais_static_yr, coalesce (p.mmsi, s.mmsi) as mmsi, 
	case when p.mmsi is not null then 1 else 0 end as mmsi_in_position,
	case when s.mmsi is not null then 1 else 0 end as mmsi_in_static
	FROM unique_vessel.aggregated_register_position p
	full OUTER JOIN unique_vessel.aggregated_register_static s ON p.mmsi = s.mmsi
	);	

CREATE INDEX index_mmsi
ON unique_vessel.aggregated_register (mmsi);

	
select COUNT(distinct mmsi) from unique_vessel.aggregated_register;

select COUNT(distinct mmsi) from ais_messages.full_year_static;
