{{ config(materialized='table') }}

with stop_times as (
	select
		st.trip_id,
		st.stop_id,
		st.arrival_time,
	 	st.departure_time,
	 	cast(split_part(st.departure_time,':',1) as integer)*10000+cast(split_part(st.departure_time,':',2) as integer)*100+cast(split_part(st.departure_time,':',3) as integer) as departure_time_number,
		cast(split_part(st.arrival_time,':',1) as integer)*10000+cast(split_part(st.arrival_time,':',2) as integer)*100+cast(split_part(st.arrival_time,':',3) as integer) as arrival_time_number,
		st.stop_sequence
	from {{ ref('stop_times') }} st
),
stop_times_indic as (
	select
		st.*,
		st.departure_time_number - st.arrival_time_number as stop_duration,
		st.arrival_time_number - max(st.departure_time_number) over(partition by st.trip_id order by st.stop_sequence rows between 1 preceding and 1 preceding) as from_prev_stop_duration,
		st.arrival_time_number - min(st.arrival_time_number) over(partition by st.trip_id order by st.stop_sequence rows between unbounded preceding and 1 preceding) as cum_trip_duration,
		max(st.arrival_time_number) over(partition by st.trip_id) - min(st.departure_time_number) over(partition by st.trip_id) as total_trip_duration
	from stop_times st
)

select * from stop_times_indic