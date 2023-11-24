def query_params(node) :
    return f"""
select
    p.node_id,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.p,
    p.t,
    p.rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.node_id ={node}
order by p.sensor_ts  DESC limit 8;
"""

query_hour = """
select
    p.node_id,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.p,
    p.t,
    p.rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts >= NOW() - INTERVAL '1 HOUR'
order by p.sensor_ts;
"""

query_day = """
select
    p.node_id,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.p,
    p.t,
    p.rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts >= NOW() - interval '24 hour'
order by p.sensor_ts;
"""
query_week = """
select
    p.node_id,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.p,
    p.t,
    p.rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts >= NOW() - interval '7 days'
order by p.sensor_ts;
"""

query_week_avg = """
select
    p.node_id,
    s.name as sensor_description,
    date_trunc('hour', p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    cast(avg(p.p) as decimal(9,2)) as p,
    cast(avg(p.t) as decimal(9,2)) as t,
    cast(avg(p.rh) as decimal(9,2)) as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts >= NOW() - interval '7 days'
group by date_trunc('hour', p.sensor_ts), p.node_id, s.name
order by date_trunc('hour', p.sensor_ts);
"""
query_month = """
select
    p.node_id,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.p,
    p.t,
    p.rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts >= NOW() - interval '30 days'
order by p.sensor_ts;
"""
query_month_avg = """
select
    p.node_id,
    s.name as sensor_description,
    date_trunc('hour', p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    cast(avg(p.p) as decimal(9,2)) as p,
    cast(avg(p.t) as decimal(9,2)) as t,
    cast(avg(p.rh) as decimal(9,2)) as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts >= NOW() - interval '30 days'
group by date_trunc('hour', p.sensor_ts), p.node_id, s.name
order by date_trunc('hour', p.sensor_ts);
"""
query_6moths = """
select
    p.node_id,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.p,
    p.t,
    p.rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts >= NOW() - interval '180 days'
order by p.sensor_ts;
"""
query_6moths_test= """
SELECT
    p.node_id,
    s.name as sensor_description,
    TIMESTAMP WITH TIME ZONE 'epoch' +
    INTERVAL '1 second' * round(extract('epoch' from p.sensor_ts) / 32400) * 32400 as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    cast(avg(p.p) as decimal(9,2)) as p,
    cast(avg(p.t) as decimal(9,2)) as t,
    cast(avg(p.rh) as decimal(9,2)) as rh
FROM packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts >= NOW() - interval '180 days'
GROUP BY round(extract('epoch' from p.sensor_ts) / 32400), p.node_id, s.name
ORDER BY round(extract('epoch' from p.sensor_ts) / 32400);
"""

query_6moths_avg = """
SELECT  p.node_id,GROUP BY date_trunc('day', p.sensor_ts), 

    s.name as sensor_description,
    max(p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    cast(avg(p.p) as decimal(9,2)) as p,
    cast(avg(p.t) as decimal(9,2)) as t,
    cast(avg(p.rh) as decimal(9,2)) as rh
FROM packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts >= NOW() - interval '180 days'
GROUP BY date_trunc('day', p.sensor_ts), 
    FLOOR(date_part('hour', p.sensor_ts) /8) , p.node_id, s.name
ORDER BY date_trunc('day', p.sensor_ts);"""

query_6moths_avg_node_1 = """
SELECT  p.node_id,
    s.name as sensor_description,
    max(p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    cast(avg(p.p) as decimal(9,2)) as p,
    cast(avg(p.t) as decimal(9,2)) as t,
    cast(avg(p.rh) as decimal(9,2)) as rh
FROM packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts >= NOW() - interval '180 days' and p.node_id = 1
GROUP BY date_trunc('day', p.sensor_ts), 
    FLOOR(date_part('hour', p.sensor_ts) /8) , p.node_id, s.name
ORDER BY date_trunc('day', p.sensor_ts);"""

query_6moths_avg_node_6 = """
SELECT  p.node_id,
    s.name as sensor_description,
    max(p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    cast(avg(p.p) as decimal(9,2)) as p,
    cast(avg(p.t) as decimal(9,2)) as t,
    cast(avg(p.rh) as decimal(9,2)) as rh
FROM packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts >= NOW() - interval '180 days' and p.node_id = 6
GROUP BY date_trunc('day', p.sensor_ts), 
    FLOOR(date_part('hour', p.sensor_ts) /8) , p.node_id, s.name
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
    p.node_id,
    s.name as sensor_description,
    p.sensor_ts as ts,
    pd.r1 as heater_res,
    pd.r2 as signal_res,
    pd.volt as volt,
    p.p,
    p.t,
    p.rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts BETWEEN '{start}' AND '{end}'
order by p.sensor_ts;
    """
    
def q_custom_30min(start, end):
    return f"""
SELECT  p.node_id,
    s.name as sensor_description,
    max(p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    cast(avg(p.p) as decimal(9,2)) as p,
    cast(avg(p.t) as decimal(9,2)) as t,
    cast(avg(p.rh) as decimal(9,2)) as rh
FROM packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts BETWEEN '{start}' AND '{end}'
GROUP BY date_trunc('hour', p.sensor_ts), 
    FLOOR(date_part('minute', p.sensor_ts) /30) , p.node_id, s.name
ORDER BY date_trunc('hour', p.sensor_ts);"""

def q_custom_1H(start, end):
    return f"""
select
    p.node_id,
    s.name as sensor_description,
    date_trunc('hour', p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    cast(avg(p.p) as decimal(9,2)) as p,
    cast(avg(p.t) as decimal(9,2)) as t,
    cast(avg(p.rh) as decimal(9,2)) as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts BETWEEN '{start}' AND '{end}'
group by date_trunc('hour', p.sensor_ts), p.node_id, s.name
order by date_trunc('hour', p.sensor_ts);"""

def q_custom_H(start, end, H):
    return f"""
select
    p.node_id,
    s.name as sensor_description,
    max(p.sensor_ts) as ts,
    avg(pd.r1) as heater_res,
    avg(pd.r2) as signal_res,
    avg(pd.volt) as volt,
    cast(avg(p.p) as decimal(9,2)) as p,
    cast(avg(p.t) as decimal(9,2)) as t,
    cast(avg(p.rh) as decimal(9,2)) as rh
from packet_data pd
    left join packet p on p.id = pd.packet_id
    left join sensor s on s.id = pd.sensor_id
where p.sensor_ts BETWEEN '{start}' AND '{end}'
GROUP BY date_trunc('day', p.sensor_ts), 
    FLOOR(date_part('hour', p.sensor_ts) /{H}) , p.node_id, s.name
ORDER BY date_trunc('day', p.sensor_ts);"""


def query_appa_compare_years(s_day, s_month, e_day, e_month):
    return f"""
       SELECT 
            stazione,
            inquinante,
            ts,
            valore
        FROM appa_data
        WHERE date_part('month', ts) * 100 + date_part('day', ts) >= '{s_month}{s_day}'::integer -- filter by starting day of period
        AND date_part('month', ts) * 100 + date_part('day', ts) <= '{e_month}{e_day}'::integer  -- filter by ending day of period

    """

def q_custom_appa_from_now(times, H):
    return f"""
select
    stazione,
    inquinante,
    min(ts) as ts,
    avg(valore) as valore
from appa_data
where ts >= NOW() - interval '{times}'
GROUP BY date_trunc('day', ts), 
    FLOOR(date_part('hour', ts) /{H}) , stazione, inquinante
ORDER BY date_trunc('day', ts);"""

def q_custom_appa(start, end, H=1):
    return f"""
select
    stazione,
    inquinante,
    min(ts),
    avg(valore)
from appa_data
where ts BETWEEN '{start}' AND '{end}'
GROUP BY date_trunc('day', ts), 
    FLOOR(date_part('hour', ts) /{H}) , stazione, inquinante
ORDER BY date_trunc('day', ts);"""

query_appa_one_data_per_week =  """
select
    stazione,
    inquinante,
    date_trunc('week', ts) as ts,
    avg(valore) as valore
from appa_data
group by date_trunc('week', ts),stazione, inquinante
order by date_trunc('week', ts);"""



def general_query(avg: bool, time: str, start :str, end :str, interval :int):
    arr = {0: 'second', 1:'minute', 2:'hour', 3:'day'}
    
    key = {i for i in arr if arr[i]==time}

    if avg:
        return f"""
    SELECT
        p.node_id,
        s.name as sensor_description,
        max(p.sensor_ts) as ts,
        avg(pd.r1) as heater_res,
        avg(pd.r2) as signal_res,
        avg(pd.volt) as volt,
        avg((p.attrs::json->>'P')::numeric) as p,
        avg((p.attrs::json->>'T')::numeric) as t,
        avg((p.attrs::json->>'RH')::numeric) as rh
    FROM packet_data pd
        LEFT JOIN packet p ON p.id = pd.packet_id
        LEFT JOIN sensor s ON s.id = pd.sensor_id

WHERE p.sensor_ts BETWEEN '{start}' AND '{end}'
GROUP BY date_trunc('{arr[key+1]}', p.sensor_ts), 
    FLOOR(date_part('{arr[key]}', p.sensor_ts) /{interval}) , p.node_id, s.name
ORDER BY date_trunc('{arr[key+1]}', p.sensor_ts);"""      
    