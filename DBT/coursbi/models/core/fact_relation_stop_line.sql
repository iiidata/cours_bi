{{ config(materialized='table') }}

select
    dl.line_id,
    ds.stop_id
from {{ ref('smmag_line_stops')}} as sms
inner join {{ ref('dim_line')}} as dl on dl.line_id = sms.line_id
inner join {{ ref('dim_stop')}} as ds on ds.stop_id = sms.id