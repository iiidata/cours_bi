{{ config(materialized='table') }}

with freq_per_stop as (
    select up_cluster_name,down_cluster_name,passengers_count,line_direction,timelaps,goal,line
    from
    where goal <> 'ALL'
)