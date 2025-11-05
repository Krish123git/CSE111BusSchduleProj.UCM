-- ROUTE TABLE
CREATE TABLE route (
    route_key      INTEGER PRIMARY KEY,
    route_name     TEXT NOT NULL,
    status_key     INTEGER,
    FOREIGN KEY(status_key) REFERENCES route_status(status_key)
);

-- STOP TABLE
CREATE TABLE stop (
    stop_key       INTEGER PRIMARY KEY,
    stop_name      TEXT NOT NULL
);

-- ROUTE_STOP (Many–Many between Routes and Stops + time)
CREATE TABLE route_stop (
    route_key      INTEGER NOT NULL,
    stop_key       INTEGER NOT NULL,
    time           TEXT NOT NULL,
    PRIMARY KEY (route_key, stop_key), 
    FOREIGN KEY(route_key) REFERENCES route(route_key),
    FOREIGN KEY(stop_key)  REFERENCES stop(stop_key)
);

-- DRIVER TABLE
CREATE TABLE driver (
    driver_key     INTEGER PRIMARY KEY,
    driver_name    TEXT NOT NULL
);
--Just a table for the driver information

-- DRIVER_ROUTE (Many–Many between Drivers and Routes)
CREATE TABLE driver_route (
    driver_key     INTEGER NOT NULL,
    route_key      INTEGER NOT NULL,
    PRIMARY KEY (driver_key, route_key),
    FOREIGN KEY(driver_key) REFERENCES driver(driver_key),
    FOREIGN KEY(route_key)  REFERENCES route(route_key)
);
-- will denote which driver is on which route

-- ROUTE STATUS TABLE
CREATE TABLE route_status (
    status_key     INTEGER PRIMARY KEY,
    description    TEXT NOT NULL
);
-- Perhaps we can use 0 for inactive, and 1 for active?
