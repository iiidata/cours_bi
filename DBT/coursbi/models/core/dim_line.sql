{{ config(materialized='table') }}

with source as (select * from {{ref('smmag_lines')}})

select
    "gtfsid" as line_id,
	"shortname" as short_name,
    "longname" as long_name,
    color as line_color,
    "textcolor" as text_color,
    "mode" as transport_mode,
	"type" as transport_type,
	case
	    when "type" = 'FLEXO' THEN 20
	    when "type" = 'PROXIMO' THEN 40
	    when "type" = 'TRAM' THEN 200
	    when "type" = 'SCOL' THEN 60
	    when "type" = 'C38_AUTRE' THEN 60
	    else 0
	end as transport_capacity,
	substring(id,0,4) as reseau_code,
	case
		when substring(id,0,4) = 'SEM' then 'SEMITAG'
		when substring(id,0,4) = 'SNC' then 'SNCF'
		when substring(id,0,4) = 'GSV' then 'GRESIVAUDAN'
		when substring(id,0,4) = 'C38' then 'TRANSISERE'
		when substring(id,0,4) = 'TPV' then 'TRANSPORT PAYS VOIRONNAIS'
		when substring(id,0,4) = 'BUL' then 'TELEPHERIQUE BASTILLE'
		when substring(id,0,4) = 'FUN' then 'FUNICULAIRE DU TOUVET'
		when substring(id,0,4) = 'MCO' then 'MCO'
	    else 'AUTRE'
	end reseau_name,
	current_timestamp as integration_date
from source
