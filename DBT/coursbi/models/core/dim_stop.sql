{{ config(materialized='table') }}

select * from {{ ref('stg_stop_hierarchy') }}