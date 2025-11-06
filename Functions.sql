--Views all bus routes:
SELECT 
    r.route_key,
    r.route_name,
    rs.description AS status
FROM route r
LEFT JOIN route_status rs
    ON r.status_key = rs.status_key;

--See route times:
SELECT 
    s.stop_name,
    rs.time
FROM route_stop rs
JOIN stop s ON rs.stop_key = s.stop_key
WHERE rs.route_key = :route_key
ORDER BY rs.time;
