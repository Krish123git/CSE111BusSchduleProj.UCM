--Views all bus routes: 
-- 1
SELECT r.route_key, r.route_name, rs.description AS status
FROM route r
LEFT JOIN route_status rs
    ON r.status_key = rs.status_key;

-- Mod ver of 1 for testing: worked with route table:
SELECT r.route_key, r.route_name AS status
FROM route r;


--See route times:
-- 2 (Works: could be made more redable during Phase 3)
SELECT s.stop_name, rs.time
FROM route_stop rs
JOIN stop s ON rs.stop_key = s.stop_key
WHERE rs.route_key = :route_key
ORDER BY rs.time;

--all routes that are active:
--fix based on table scchema later
-- 3
SELECT * FROM route_status
WHERE description = 'ACTIVE';

-- 4
-- Create review function (insert function with id 1 higher than last)
-- insert with text gained from front-end
-- insert with review score
-- Tentative addition of ability to view reviews?
-- Possible python function below for when we do frontend:
-- def create_review(conn, text, score):
--    cursor = conn.cursor()
--    cursor.execute("""
--        INSERT INTO passenger_review (review_text, review_score)
--        VALUES (?, ?);
--    """, (text, score))
--    conn.commit()

--    return cursor.lastrowid   # return the new review_id

--  /////    To use it use this:    //////
-- new_id = create_review(conn, "Bus was clean and on time", 5)
-- print("Created review with ID:", new_id)

-- /////     Here is the code by itself so that it can be tested: ////

--INSERT INTO passenger_review (review_text, review_score)
--VALUES (?, ?);
--INSERT INTO route_driver_review (route_key, driver_key, review_id)
--VALUES (?, ?, ?);


-- /////     Below is a way to update reviews in python when we make backend: /////

--def update_review_secure(conn, review_id, old_score, new_score=None, new_text=None):
--    sql = """
--        UPDATE passenger_review
--        SET review_score = COALESCE(?, review_score),
--            review_text  = COALESCE(?, review_text)
--        WHERE review_id = ?
--        AND review_score = ?
--    """
--    cur = conn.execute(sql, (new_score, new_text, review_id, old_score))
--    conn.commit()
--    return cur.rowcount

-- /////     SQL by itself to test if it works: /////

--UPDATE passenger_review
--SET review_score = COALESCE(:new_score, review_score),
--    review_text  = COALESCE(:new_text,  review_text)
--WHERE review_id = :review_id
--  AND review_score = :old_score;

-- 5
SELECT s.stop_name, rs.time
FROM route_stop rs
JOIN stop s ON rs.stop_key = s.stop_key
WHERE rs.route_key = ?
  AND TIME(rs.time || ':00') <= TIME('now', 'localtime')
ORDER BY TIME(rs.time || ':00') DESC
LIMIT 1;


-- 6
-- Calculate price of passenger fare given passenger type -> done in #29

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


-- Trying something below regardless of above:


/* ============================================================
   1. Get all routes
   ============================================================ */
SELECT * FROM route;

/* ============================================================
   2. Get all stops
   ============================================================ */
SELECT * FROM stop;

/* ============================================================
   3. Get all stop times for a given route (parameterized)
   ============================================================ */
SELECT s.stop_name, rs.time
FROM route_stop rs
JOIN stop s ON rs.stop_key = s.stop_key
WHERE rs.route_key = :route_key
ORDER BY rs.time;

/* ============================================================
   4. Get all stops in correct order for a route (distinct list)
   ============================================================ */
SELECT DISTINCT s.stop_name
FROM route_stop rs
JOIN stop s ON rs.stop_key = s.stop_key
WHERE rs.route_key = :route_key
ORDER BY rs.stop_key;

/* ============================================================
   5. Count how many stop-times exist per route
   ============================================================ */
SELECT route_key, COUNT(*) AS total_times
FROM route_stop
GROUP BY route_key;

/* ============================================================
   6. List all routes that service a specific stop                           CHECKED WITH 45 stop_key, got something
   ============================================================ */
SELECT r.route_name, rs.time
FROM route_stop rs
JOIN route r ON r.route_key = rs.route_key
WHERE rs.stop_key = :stop_key
ORDER BY rs.time;

/* ============================================================
   7. Find duplicate stop entries (should be none)
   ============================================================ */
SELECT stop_key, stop_name, COUNT(*) AS count
FROM stop
GROUP BY stop_key, stop_name
HAVING COUNT(*) > 1;

/* ============================================================
   8. Find duplicate route_stop entries
   ============================================================ */
SELECT route_key, stop_key, time, COUNT(*) AS count
FROM route_stop
GROUP BY route_key, stop_key, time
HAVING COUNT(*) > 1;

/* ============================================================
   9. View full schedule for ALL routes, ordered neatly
   ============================================================ */
SELECT r.route_name, s.stop_name, rs.time
FROM route_stop rs
JOIN stop s ON rs.stop_key = s.stop_key
JOIN route r ON r.route_key = rs.route_key
ORDER BY r.route_key, rs.time;

/* ============================================================
   10. Show first stop time for each route
   ============================================================ */
SELECT route_key,
       MIN(
           CASE
               WHEN length(time) = 4 THEN '0' || time   -- "8:54" → "08:54"
               ELSE time                               -- "10:04" stays "10:04"
           END
       ) AS first_time
FROM route_stop
GROUP BY route_key;
-- This and the one below technically wont work as the data isn't formatted correctly.

/* ============================================================
   11. Show last stop time for each route
   ============================================================ */
SELECT route_key, MAX(time) AS last_time
FROM route_stop
GROUP BY route_key;

/* ============================================================
   12. Check stops that are never used by any route
   ============================================================ */
SELECT s.stop_key, s.stop_name
FROM stop s
LEFT JOIN route_stop rs ON s.stop_key = rs.stop_key
WHERE rs.stop_key IS NULL;

/* ============================================================
   13. Check routes that have no stops (should be none)
   ============================================================ */
SELECT r.route_key, r.route_name
FROM route r
LEFT JOIN route_stop rs ON r.route_key = rs.route_key
WHERE rs.route_key IS NULL;

/* ============================================================
   14. List stops and how many routes serve them                                               CHECKED, gests some result
   ============================================================ */
SELECT s.stop_name, COUNT(DISTINCT rs.route_key) AS routes_serving
FROM route_stop rs
JOIN stop s ON rs.stop_key = s.stop_key
GROUP BY s.stop_key
ORDER BY routes_serving DESC;

/* ============================================================
   15. Show all times at a stop throughout the day
   ============================================================ */
SELECT r.route_name, rs.time
FROM route_stop rs
JOIN route r ON rs.route_key = r.route_key
WHERE rs.stop_key = :stop_key
ORDER BY rs.time;

/* ============================================================
   16. Insert a new route_stop time (template)
   ============================================================ */
INSERT INTO route_stop (route_key, stop_key, time)
VALUES (:route_key, :stop_key, :time);



------------------------------------------------------------------
-- 17) QUERY #1:
--    List all drivers and the routes they are assigned to.
------------------------------------------------------------------
SELECT d.driver_name, dr.route_key
FROM driver d
LEFT JOIN driver_route dr ON d.driver_key = dr.driver_key
ORDER BY d.driver_key;



------------------------------------------------------------------
-- 18) QUERY #2:
--    Show all drivers who have NOT been assigned to any route.
------------------------------------------------------------------
SELECT d.driver_key, d.driver_name
FROM driver d
LEFT JOIN driver_route dr ON d.driver_key = dr.driver_key
WHERE dr.route_key IS NULL;



------------------------------------------------------------------
-- 19) QUERY #3:                                                                            CHECKED, gests some result
--    For each route, show the assigned driver.
------------------------------------------------------------------
SELECT r.route_key, r.route_name, d.driver_name
FROM route r
LEFT JOIN driver_route dr ON r.route_key = dr.route_key
LEFT JOIN driver d ON d.driver_key = dr.driver_key
ORDER BY r.route_key;



---------------------------------------------------------------------------
-- 20. Get all routes a driver has reviews for
-- Example: driver_key = 7
---------------------------------------------------------------------------
SELECT DISTINCT 
    rdr.route_key
FROM route_driver_review rdr
WHERE rdr.driver_key = 7;


---------------------------------------------------------------------------
-- 21. Find which driver has the highest-rated average score
---------------------------------------------------------------------------
SELECT 
    d.driver_key,
    d.driver_name,
    AVG(pr.review_score) AS avg_score
FROM driver d
JOIN route_driver_review rdr ON d.driver_key = rdr.driver_key
JOIN passenger_review pr ON rdr.review_id = pr.review_id
GROUP BY d.driver_key, d.driver_name
ORDER BY avg_score DESC
LIMIT 1;


---------------------------------------------------------------------------
-- 22. Find all reviews for a route made during poor performance (score ≤ 2)            CHECKED, gests some result
-- Example: route_key = 4
---------------------------------------------------------------------------
SELECT 
    pr.review_id,
    pr.review_score,
    pr.review_text
FROM route_driver_review rdr
JOIN passenger_review pr ON rdr.review_id = pr.review_id
WHERE rdr.route_key = 4
  AND pr.review_score <= 2;


---------------------------------------------------------------------------
-- 23. Count reviews per route
---------------------------------------------------------------------------
SELECT 
    rdr.route_key,
    COUNT(rdr.review_id) AS review_count
FROM route_driver_review rdr
GROUP BY rdr.route_key
ORDER BY review_count DESC;


---------------------------------------------------------------------------
-- 24. List drivers with no reviews
---------------------------------------------------------------------------
SELECT d.driver_key, d.driver_name
FROM driver d
LEFT JOIN route_driver_review rdr ON d.driver_key = rdr.driver_key
WHERE rdr.review_id IS NULL;


---------------------------------------------------------------------------
-- 25. Get routes with an average review score below 3
---------------------------------------------------------------------------
SELECT 
    r.route_key,
    r.route_name,
    AVG(pr.review_score) AS avg_score
FROM route r
JOIN route_driver_review rdr ON r.route_key = rdr.route_key
JOIN passenger_review pr ON rdr.review_id = pr.review_id
GROUP BY r.route_key, r.route_name
HAVING avg_score < 3;


---------------------------------------------------------------------------
-- 26. Get the highest-rated review for each route
---------------------------------------------------------------------------
SELECT r.route_key, r.route_name, pr.review_id, pr.review_score, pr.review_text
FROM route r
JOIN route_driver_review rdr ON r.route_key = rdr.route_key
JOIN passenger_review pr ON rdr.review_id = pr.review_id
WHERE pr.review_score = (
    SELECT MAX(pr2.review_score)
    FROM route_driver_review rdr2
    JOIN passenger_review pr2 ON rdr2.review_id = pr2.review_id
    WHERE rdr2.route_key = r.route_key
);


---------------------------------------------------------------------------
-- 27. Get the worst 5 reviews systemwide
---------------------------------------------------------------------------
SELECT review_id, review_score, review_text
FROM passenger_review
ORDER BY review_score ASC, review_id ASC
LIMIT 5;


---------------------------------------------------------------------------
-- 28. See which driver handled the most 5-star reviews
---------------------------------------------------------------------------
SELECT 
    d.driver_key,
    d.driver_name,
    COUNT(pr.review_id) AS five_star_reviews
FROM driver d
JOIN route_driver_review rdr ON d.driver_key = rdr.driver_key
JOIN passenger_review pr ON rdr.review_id = pr.review_id
WHERE pr.review_score = 5
GROUP BY d.driver_key, d.driver_name
ORDER BY five_star_reviews DESC;


-- 29. Payment:
DROP VIEW IF EXISTS payment_view;

CREATE VIEW payment_view AS
SELECT
    p.passenger_id,
    p.passenger_type,
    p.route_id,
    CASE
        WHEN p.passenger_type = 'student' THEN 0
        WHEN p.passenger_type = 'staff'
             AND p.route_id NOT IN (7, 8) THEN 0
        ELSE 1.50
    END AS fare
FROM payment AS p;


-- After Running the above, it will create a view, that will allow the use of the query below:

SELECT * FROM payment_view;



--Misc Stuff:
--INSERT INTO driver (driver_key, driver_name) VALUES (16, 'Sir Vivor');
--INSERT INTO driver (driver_key, driver_name) VALUES (17, 'Sir Prize');
--INSERT INTO driver (driver_key, driver_name) VALUES (18, 'Sir Valance');
--^ Just funny driver names c: