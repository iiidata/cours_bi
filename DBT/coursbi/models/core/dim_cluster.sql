{{ config(materialized='table') }}


select
    distinct
    cluster_code,
    cluster_name,
    top_visible_cluster,
    cluster_latitude,
    cluster_longitude,
    city_code,
    city_name,
    city_surface,
    city_epci,
    city_area,
    current_timestamp as integration_date

from {{ ref('stg_stop_hierarchy') }}
