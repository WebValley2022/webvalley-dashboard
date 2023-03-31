def query_params(node) :
    return f"""
select
    n.description as node_description,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.attrs::json->'P' as p,
    p.attrs::json->'T' as t,
    p.attrs::json->'RH' as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where n.id ={node}
order by p.sensor_ts  DESC limit 8;
"""

query_hour = """
select
    n.description as node_description,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.attrs::json->'P' as p,
    p.attrs::json->'T' as t,
    p.attrs::json->'RH' as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= NOW() - INTERVAL '1 HOUR'
order by p.sensor_ts;
"""

query_day = """
select
    n.description as node_description,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.attrs::json->'P' as p,
    p.attrs::json->'T' as t,
    p.attrs::json->'RH' as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= NOW() - interval '24 hour'
order by p.sensor_ts;
"""
query_week = """
select
    n.description as node_description,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.attrs::json->'P' as p,
    p.attrs::json->'T' as t,
    p.attrs::json->'RH' as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= NOW() - interval '7 days'
order by p.sensor_ts;
"""

query_week_avg = """
select
    n.description as node_description,
    s.name as sensor_description,
    date_trunc('hour', p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    avg((p.attrs::json->>'P')::numeric) as p,
    avg((p.attrs::json->>'T')::numeric) as t,
    avg((p.attrs::json->>'RH')::numeric) as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= NOW() - interval '7 days'
group by date_trunc('hour', p.sensor_ts), n.description, s.name
order by date_trunc('hour', p.sensor_ts);
"""
query_month = """
select
    n.description as node_description,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.attrs::json->'P' as p,
    p.attrs::json->'T' as t,
    p.attrs::json->'RH' as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= NOW() - interval '30 days'
order by p.sensor_ts;
"""
query_month_avg = """
select
    n.description as node_description,
    s.name as sensor_description,
    date_trunc('hour', p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    avg((p.attrs::json->>'P')::numeric) as p,
    avg((p.attrs::json->>'T')::numeric) as t,
    avg((p.attrs::json->>'RH')::numeric) as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= NOW() - interval '30 days'
group by date_trunc('hour', p.sensor_ts), n.description, s.name
order by date_trunc('hour', p.sensor_ts);
"""
query_6moths = """
select
    n.description as node_description,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.attrs::json->'P' as p,
    p.attrs::json->'T' as t,
    p.attrs::json->'RH' as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= NOW() - interval '180 days'
order by p.sensor_ts;
"""
query_6moths_test= """
SELECT
    n.description as node_description,
    s.name as sensor_description,
    TIMESTAMP WITH TIME ZONE 'epoch' +
    INTERVAL '1 second' * round(extract('epoch' from p.sensor_ts) / 10800) * 10800 as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    avg((p.attrs::json->>'P')::numeric) as p,
    avg((p.attrs::json->>'T')::numeric) as t,
    avg((p.attrs::json->>'RH')::numeric) as rh
FROM packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= NOW() - interval '180 days'
GROUP BY round(extract('epoch' from p.sensor_ts) / 10800), n.description, s.name
ORDER BY round(extract('epoch' from p.sensor_ts) / 10800);
"""

query_6moths_avg = """
SELECT  n.description as node_description,
    s.name as sensor_description,
    min(p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    avg((p.attrs::json->>'P')::numeric) as p,
    avg((p.attrs::json->>'T')::numeric) as t,
    avg((p.attrs::json->>'RH')::numeric) as rh
FROM packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts >= NOW() - interval '180 days'
GROUP BY date_trunc('day', p.sensor_ts), 
    FLOOR(date_part('hour', p.sensor_ts) /3) , n.description, s.name
ORDER BY date_trunc('day', p.sensor_ts);"""

query_sensor = """
select
    id,
    name,
    description,
    active,
    node_id
from sensor pd;
"""

query_history_sensor = """
select
    name,
    description,
    active,
    node_id,
    attrs
from sensor pd;
"""

def q_custom_all(start, end):
    return f"""
    select
    n.description as node_description,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.attrs::json->'P' as p,
    p.attrs::json->'T' as t,
    p.attrs::json->'RH' as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts BETWEEN '{start}' AND '{end}'
order by p.sensor_ts;
    """
    
def q_custom_30min(start, end):
    return f"""
SELECT  n.description as node_description,
    s.name as sensor_description,
    min(p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    avg((p.attrs::json->>'P')::numeric) as p,
    avg((p.attrs::json->>'T')::numeric) as t,
    avg((p.attrs::json->>'RH')::numeric) as rh
FROM packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts BETWEEN '{start}' AND '{end}'
GROUP BY date_trunc('hour', p.sensor_ts), 
    FLOOR(date_part('minute', p.sensor_ts) /30) , n.description, s.name
ORDER BY date_trunc('hour', p.sensor_ts);"""

def q_custom_1H(start, end):
    return f"""
select
    n.description as node_description,
    s.name as sensor_description,
    date_trunc('hour', p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    avg((p.attrs::json->>'P')::numeric) as p,
    avg((p.attrs::json->>'T')::numeric) as t,
    avg((p.attrs::json->>'RH')::numeric) as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts BETWEEN '{start}' AND '{end}'
group by date_trunc('hour', p.sensor_ts), n.description, s.name
order by date_trunc('hour', p.sensor_ts);"""

def q_custom_H(start, end, H):
    return f"""
select
    n.description as node_description,
    s.name as sensor_description,
    min(p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    avg((p.attrs::json->>'P')::numeric) as p,
    avg((p.attrs::json->>'T')::numeric) as t,
    avg((p.attrs::json->>'RH')::numeric) as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
    left join node n on n.id = p.node_id
where p.sensor_ts BETWEEN '{start}' AND '{end}'
GROUP BY date_trunc('day', p.sensor_ts), 
    FLOOR(date_part('hour', p.sensor_ts) /{H}) , n.description, s.name
ORDER BY date_trunc('day', p.sensor_ts);"""

def general_query(avg: bool, time: str, start :str, end :str, interval :int):
    arr = {0: 'second', 1:'minute', 2:'hour', 3:'day'}
    
    key = {i for i in arr if arr[i]==time}

    if avg:
        return f"""
    SELECT
        n.description as node_description,
        s.name as sensor_description,
        min(p.sensor_ts) as ts,
        avg(pd.r1) as heater_res,
        avg(pd.r2) as signal_res,
        avg(pd.volt) as volt,
        avg((p.attrs::json->>'P')::numeric) as p,
        avg((p.attrs::json->>'T')::numeric) as t,
        avg((p.attrs::json->>'RH')::numeric) as rh
    FROM packet_data pd
        LEFT JOIN packet p ON p.id = pd.packet_id
        LEFT JOIN sensor s ON s.id = pd.sensor_id
        LEFT JOIN node n ON n.id = p.node_id
WHERE p.sensor_ts BETWEEN '{start}' AND '{end}'
GROUP BY date_trunc('{arr[key+1]}', p.sensor_ts), 
    FLOOR(date_part('{arr[key]}', p.sensor_ts) /{interval}) , n.description, s.name
ORDER BY date_trunc('{arr[key+1]}', p.sensor_ts);"""      
    