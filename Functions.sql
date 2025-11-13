--Initials can be removed later for submission if needed. Currently added for better teamwork
-- Completed: 3
-- Planned: 3(4?)
-- # more needed: 14 (13?)

--Views all bus routes: (RT)
-- 1
SELECT r.route_key, r.route_name, rs.description AS status
FROM route r
LEFT JOIN route_status rs
    ON r.status_key = rs.status_key;

--See route times:  (RT)
-- 2
SELECT s.stop_name, rs.time
FROM route_stop rs
JOIN stop s ON rs.stop_key = s.stop_key
WHERE rs.route_key = :route_key
ORDER BY rs.time;

--all routes that are active:  (KV)
--fix based on table scchema later
-- 3
SELECT * FROM route_status
WHERE description = 'ACTIVE';

-- 4
-- Create review function (insert function with id 1 higher than last)
-- insert with text gained from front-end
-- insert with review score
-- Tentative addition of ability to view reviews?

-- 5
-- Find the location of the bus
-- do this via getting the current time, 
-- then looking at the route, and choosing
-- the closest timed stop (rounding down)

-- 6
-- Calculate price of passenger fare given passenger type

-- 7
-- View Drivers Information
SELECT r.route_name, d.driver_name
FROM route r
JOIN driver_route dr 
    ON r.route_key = dr.route_key
JOIN driver d 
    ON dr.driver_key = d.driver_key
WHERE r.route_name = ?; -- 



-- Obviously we also need to add insert statements to put the stop times into the db
-- We have said that we may use an AI tool to extract the data from the timetable PDFs

-- test