
query_hour = """
select
    n.node_name as node_name,
    n.description as node_description,
    s.id as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as signal_res,
    pd.r2 as heater_res,
    pd.volt as volt,
    p.attrs::json->'P' as p,
    p.attrs::json->'T' as t,
    p.attrs::json->'RH' as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= current_date at time zone 'UTC' - interval '26 hours'
order by p.sensor_ts;
"""

query_day = """
select
    n.node_name as node_name,
    n.description as node_description,
    s.id as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as signal_res,
    pd.r2 as heater_res,
    pd.volt as volt,
    p.attrs::json->'P' as p,
    p.attrs::json->'T' as t,
    p.attrs::json->'RH' as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= current_date at time zone 'UTC' - interval '1 days'
order by p.sensor_ts;
"""
query_week = """
select
    n.node_name as node_name,
    n.description as node_description,
    s.id as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as signal_res,
    pd.r2 as heater_res,
    pd.volt as volt,
    p.attrs::json->'P' as p,
    p.attrs::json->'T' as t,
    p.attrs::json->'RH' as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= current_date at time zone 'UTC' - interval '7 days'
order by p.sensor_ts;
"""
query_mounth = """
select
    n.node_name as node_name,
    n.description as node_description,
    s.id as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as signal_res,
    pd.r2 as heater_res,
    pd.volt as volt,
    p.attrs::json->'P' as p,
    p.attrs::json->'T' as t,
    p.attrs::json->'RH' as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= current_date at time zone 'UTC' - interval '30 days'
order by p.sensor_ts;
"""
query_6mouths = """
select
    n.node_name as node_name,
    n.description as node_description,
    s.id as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as signal_res,
    pd.r2 as heater_res,
    pd.volt as volt,
    p.attrs::json->'P' as p,
    p.attrs::json->'T' as t,
    p.attrs::json->'RH' as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= current_date at time zone 'UTC' - interval '180 days'
order by p.sensor_ts;
"""

query_sensor = """
select
    id,
    name,
    description
from sensor pd;
"""