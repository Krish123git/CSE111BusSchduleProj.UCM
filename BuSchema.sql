-- ROUTE TABLE
CREATE TABLE IF NOT EXISTS route (
    route_key      INTEGER PRIMARY KEY,
    route_name     TEXT NOT NULL,
    status_key     INTEGER,
    FOREIGN KEY(status_key) REFERENCES route_status(status_key)
);
-- The table storing the bus name, id, and active status

-- STOP TABLE
CREATE TABLE IF NOT EXISTS stop (
    stop_key       INTEGER PRIMARY KEY,
    stop_name      TEXT NOT NULL
);
-- The table storing the IDs of the places in which the busses will stop + their name

-- ROUTE_STOP (Many–Many between Routes and Stops + time)
CREATE TABLE IF NOT EXISTS route_stop (
    route_key      INTEGER NOT NULL,
    stop_key       INTEGER NOT NULL,
    time           TEXT NOT NULL,
    PRIMARY KEY (route_key, stop_key), 
    FOREIGN KEY(route_key) REFERENCES route(route_key),
    FOREIGN KEY(stop_key)  REFERENCES stop(stop_key)
);
-- The table storing the individual stop + time on a route

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
    PRIMARY KEY (driver_key, route_key),
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

--
CREATE TABLE IF NOT EXISTS passenger_review (
    review_id INTEGER PRIMARY KEY,
    review_text TEXT NOT NULL,
    review_score INTEGER
)


-- TODO
-- Create payment, events/breaks, route status

-- Events -> Have keys for events, holidays, weekends, etc, which define what the status is, each route we should add
-- a portion that defines when the route will be active/inactive (i.e. if the route is down for weekends, or it's up during finals or other things)
