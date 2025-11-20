-- ROUTE TABLE
CREATE TABLE IF NOT EXISTS route (
    route_key      INTEGER PRIMARY KEY,
    route_name     TEXT NOT NULL,
    status_key     INTEGER,
    FOREIGN KEY(status_key) REFERENCES route_status(status_key)
);
-- The table storing the bus name, id, and active status
-- DROP TABLE IF EXISTS route;

-- STOP TABLE
CREATE TABLE IF NOT EXISTS stop (
    stop_key       INTEGER PRIMARY KEY,
    stop_name      TEXT NOT NULL
);
-- The table storing the IDs of the places in which the busses will stop + their name
-- DROP TABLE IF EXISTS stop;

-- ROUTE_STOP (Many–Many between Routes and Stops + time)
CREATE TABLE IF NOT EXISTS route_stop (
    route_key      INTEGER NOT NULL,
    stop_key       INTEGER NOT NULL,
    time           TEXT NOT NULL, 
    FOREIGN KEY(route_key) REFERENCES route(route_key),
    FOREIGN KEY(stop_key)  REFERENCES stop(stop_key)
);
-- The table storing the individual stop + time on a route
-- DROP TABLE IF EXISTS route_stop;

-- DRIVER TABLE
CREATE TABLE IF NOT EXISTS driver (
    driver_key     INTEGER PRIMARY KEY,
    driver_name    TEXT NOT NULL
);
--Just a table for the driver information

-- DRIVER_ROUTE (Many–Many between Drivers and Routes)
CREATE TABLE IF NOT EXISTS driver_route (
    driver_key     INTEGER NOT NULL,
    route_key      INTEGER NOT NULL,
    FOREIGN KEY(driver_key) REFERENCES driver(driver_key),
    FOREIGN KEY(route_key)  REFERENCES route(route_key)
);
-- will denote which driver is on which route

-- ROUTE STATUS TABLE
CREATE TABLE IF NOT EXISTS route_status (
    status_key     INTEGER PRIMARY KEY,
    description    TEXT NOT NULL
);
-- Perhaps we can use 0 for inactive, and 1 for active?

-- Passenger Review Storage
CREATE TABLE IF NOT EXISTS passenger_review (
    review_id INTEGER PRIMARY KEY,
    review_text TEXT NOT NULL,
    review_score INTEGER
);

-- m-m to link drivers and routes with reviews
CREATE TABLE IF NOT EXISTS route_driver_review (
    route_key   INTEGER NOT NULL,
    driver_key  INTEGER NOT NULL,
    review_id   INTEGER NOT NULL,

    -- Foreign keys
    FOREIGN KEY(route_key) REFERENCES route(route_key),
    FOREIGN KEY(driver_key) REFERENCES driver(driver_key),
    FOREIGN KEY(review_id) REFERENCES passenger_review(review_id)
);

-- Create payment
CREATE TABLE IF NOT EXISTS payment (
    passenger_id INTEGER PRIMARY KEY, -- not sure but best option (like student id num. best unique key for payment?)
    passenger_type TEXT NOT NULL, -- I think the passenger type (could be an integer btw) should be the primary key, we don't need to save each
    -- passenger, and instead just have them input the type of passenger they are (staff, student, etc.) 
    route_key INTEGER,
    cost INTEGER
);

-- TODO

-- Create events/breaks, route status

-- Events -> Have keys for events, holidays, weekends, etc, which define what the status is, each route we should add
-- a portion that defines when the route will be active/inactive (i.e. if the route is down for weekends, or it's up during finals or other things)




-------------------------------------
       -- Data Bulk Loading --
-------------------------------------
-- ALWAYS comment out after use to not cause 
-- mess up when running the whole file.

--.mode csv
--.separator ","

--.import data/route.csv route
--.import data/stop.csv stop
--.import data/route_stop.csv route_stop
--.import data/route_status.csv route_status
--.import data/driver.csv driver
--.import data/driver_route.csv driver_route
--.import data/passenger_review.csv passenger_review
--.import data/route_driver_review.csv route_driver_review

--DELETE FROM route_stop;
--DELETE FROM stop;
--DELETE FROM route;
--DELETE FROM route_status;
--DELETE FROM driver;
--DELETE FROM driver_route;
--DELETE FROM passenger_review;
--DELETE FROM route_driver_review;

-- ONLY IMPORTED DATA FROM ALL THE SCHOOL BUSSES. M1-M7 EXCLUDED AS DATA EXTRACTION WAS COMPLICATED.

--Below I have an insert used only to test the "payment" part within #29 in Functions.sql:
--INSERT INTO payment (passenger_id, passenger_type, route_key)
--VALUES
--    (201, 'student', 1),        -- should be free
--    (202, 'staff',   8),        -- should cost 1.50 
--    (203, 'public',  7),        -- should cost 1.50 
--    (204, 'student', 7),        -- free, even if route 4 is a Loop
--    (205, 'visitor', 2);        -- non-student but NOT a loop 
