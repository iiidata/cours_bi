{{ config(materialized='table') }}

with trips as (
    select 
    
    	sti.trip_id, 
    	min(sti.departure_time) as departure_time,
        max(sti.arrival_time) as arrival_time,        
        count(distinct sti.stop_sequence) as nb_stops,
        sum(sti.stop_duration) as cum_break_duration,
        max(sti.total_trip_duration) as trip_duration,
        avg(sti.from_prev_stop_duration) as avg_duration_between_two_stops,
        max(sti.stop_sequence) as arrival_seq
    
    from {{ ref('stg_trip_indic') }}  sti
    --inner join "cours_bi"."smmag_staging"."stg_trip_indic" sti_stop_dep on sti_stop_dep.trip_id = sti.trip_id and sti_stop_dep.stop_sequence = 1 
    --inner join "cours_bi"."smmag_staging"."stg_trip_indic" sti_stop_arr on sti_stop_arr.trip_id = sti.trip_id and sti_stop_arr.stop_sequence = (select max(stop_sequence) from "cours_bi"."smmag_staging"."stg_trip_indic" where trip_id = sti.trip_id)
    group by sti.trip_id
),
trips_with_dep_and_arr as (
	select t.*, sls2.id as departure_stop_id, sls3.id as arrival_stop_id from trips t
	inner join {{ ref('stg_trip_indic') }} sti_stop_dep on sti_stop_dep.trip_id = t.trip_id and sti_stop_dep.stop_sequence = 1
    inner join {{ ref('smmag_line_stops') }} sls2 on sls2.code = right('0000'||cast(sti_stop_dep.stop_id as varchar(4)),4)
	inner join {{ ref('stg_trip_indic') }} sti_stop_arr on sti_stop_arr.trip_id = t.trip_id and sti_stop_arr.stop_sequence = t.arrival_seq
	inner join {{ ref('smmag_line_stops') }} sls3 on sls3.code = right('0000'||cast(sti_stop_arr.stop_id as varchar(4)),4)
),
services as (

    select
        sti.trip_id,
        sls.id as line_id,
        sti.departure_time,
        sti.arrival_time,
        sti.nb_stops,
        sti.cum_break_duration,
        sti.trip_duration,
        sti.avg_duration_between_two_stops,
        sti.departure_stop_id,
        sti.arrival_stop_id,
        t.service_id,
        bikes_allowed as top_bikes_allowed,
        cast(to_timestamp(cast(cd.date as char(8)),'YYYYMMDD') as date) as service_date
    from trips_with_dep_and_arr sti
    inner join {{ ref('trips') }} t on t.trip_id =sti.trip_id
    inner join {{ ref('calendar_dates') }} cd on cd.service_id = t.service_id
    inner join {{ ref('smmag_lines') }} sls on sls.shortname = t.route_id

)

select
    distinct
    dt.id as service_date_id,
    dsd.stop_id as departure_stop_id,
    dsa.stop_id as arrival_stop_id,
    dl.line_id as line_id,
    s.trip_id,
    s.service_id,
    s.departure_time,
    s.arrival_time,
    s.nb_stops,
    s.cum_break_duration,
    s.trip_duration,
    s.avg_duration_between_two_stops,
    s.top_bikes_allowed
from services s
inner join {{ ref('dim_calendar') }} dt on dt.date_actual = s.service_date
inner join {{ ref('dim_stop') }} dsd on dsd.stop_id = s.departure_stop_id
inner join {{ ref('dim_stop') }} dsa on dsa.stop_id = s.arrival_stop_id
inner join {{ ref('dim_line') }} dl on dl.line_id = s.line_id
