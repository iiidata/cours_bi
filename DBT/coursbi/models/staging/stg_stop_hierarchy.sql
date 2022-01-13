{{ config(materialized='table') }}

with stop_per_line as (
    select id,name,lat,lon,"clustergtfsid",city,cluster from {{ref('smmag_line_stops')}}
    group by id,name,lat,lon,"clustergtfsid",city,cluster
),
stops as (
    select * from {{ ref('stops') }}
),
clusters as (
    select id,code,city,name,visible,lat,lon
    from {{ref('smmag_line_clusters')}}
    group by id,code,city,name,visible,lat,lon
),
cities as (
    select * from {{ref('cities')}}
)

select
    spl.id as stop_id,
    upper(spl.name) as stop_name,
    spl.lat as latitude,
    spl.lon as longitude,
    case
        when coalesce(st.wheelchair_boarding,2) = 1 then 'OUI'
        when coalesce(st.wheelchair_boarding,2) = 0 then 'NON'
        else 'INCONNU'
    end as pmr_access,
    spl."clustergtfsid" as cluster_code,
    upper(cl.name) as cluster_name,
    cast(cl.visible as boolean) as top_visible_cluster,
    cl.lat as cluster_latitude,
    cl.lon as cluster_longitude,
    ci.ref_insee as city_code,
    ci.commune as city_name,
    ci.surf_ha as city_surface,
    ci.epci as city_epci,
    ci.bassin_air as city_area,
    current_timestamp as integration_date
from stop_per_line spl
left outer join stops st on st.stop_code = split_part(spl.id,':',2)
left outer join clusters cl on cl.code = spl.cluster
left outer join cities ci on upper(ci.commune) = upper(spl.city)

where ci.ref_insee is not null