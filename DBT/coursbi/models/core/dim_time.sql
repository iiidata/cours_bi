{{ config(materialized='table') }}

with seq_time as (
    SELECT
        distinct timelaps
    FROM {{ ref('updown_per_cluster_and_mode') }}
    WHERE timelaps <> 'ALL'
    GROUP BY timelaps
),
splited_timelaps as (
	select
	    sq.timelaps as timelaps_label,
	    cast(to_timestamp(regexp_replace(split_part(sq.timelaps,'-', 1),'H',':'),'HH24:MI') as time) as start_hour,
	    cast(to_timestamp(regexp_replace(split_part(sq.timelaps,'-', 2),'H',':'),'HH24:MI') as time)  as end_hour

	from seq_time sq
)


select
    row_number() over(order by sq.timelaps_label) as timelaps_id,
    sq.timelaps_label,
    sq.start_hour,
    sq.end_hour,
    case
    	when sq.end_hour between cast('07:30:00' as time) and cast('11:30:00' as time) then 'MATIN'
    	when sq.end_hour between cast('11:30:00' as time) and cast('13:30:00' as time) then 'MIDI'
    	when sq.end_hour between cast('13:30:00' as time) and cast('18:30:00' as time) then 'APRES-MIDI'
    	when sq.end_hour between cast('18:30:00' as time) and cast('21:30:00' as time) then 'SOIR'
    	else 'NUIT'
    end as hour_class

from splited_timelaps sq