# This was the library that chatGPT suggests to use, it looks simple but looks nice!

# If you run it on your machine, install streamlit with pip install streamlit first
# To run it, do python -m streamlit run app.py, or if you're in python do streamlit run app.py
import streamlit as st
import sqlite3
from datetime import datetime

# ----------------------------------
# CONNECT TO DATABASE
# ----------------------------------
conn = sqlite3.connect("BusDatabase.sqlite", check_same_thread=False)

st.title("School Bus System")
st.sidebar.write("Running file:", __file__)


# ----------------------------------
# SIDEBAR MENU (Split Cleanly)
# ----------------------------------
menu = st.sidebar.radio(
    "Menu",
    [
        "Routes & Schedule",
        "Stops",
        "Stop & Route Diagnostics",
        "Trip Planner",
        "Drivers",
        "Driver Analytics",
        "Leave Review",
        "View Reviews",
        "Review Analytics",
        "Admin: Insert Route Stop",
    ],
)

# ----------------------------------
# HELPER FUNCTIONS
# ----------------------------------

def get_all_routes():
    return conn.execute("SELECT route_key, route_name FROM route").fetchall()

def get_route_schedule(route_key):
    return conn.execute("""
        SELECT s.stop_name, rs.time
        FROM route_stop rs
        JOIN stop s ON rs.stop_key = s.stop_key
        WHERE rs.route_key = ?
        ORDER BY rs.time
    """, (route_key,)).fetchall()

def get_all_stops():
    return conn.execute("SELECT stop_key, stop_name FROM stop ORDER BY stop_key").fetchall()

def get_stops_for_route(route_key):
    return conn.execute("""
        SELECT DISTINCT s.stop_name
        FROM route_stop rs
        JOIN stop s ON rs.stop_key = s.stop_key
        WHERE rs.route_key = ?
        ORDER BY rs.stop_key
    """, (route_key,)).fetchall()

def get_stop_time_counts_by_route():
    return conn.execute("""
        SELECT route_key, COUNT(*) AS total_times
        FROM route_stop
        GROUP BY route_key
        ORDER BY route_key
    """).fetchall()

def get_routes_for_stop(stop_key):
    return conn.execute("""
        SELECT r.route_name, rs.time
        FROM route_stop rs
        JOIN route r ON r.route_key = rs.route_key
        WHERE rs.stop_key = ?
        ORDER BY rs.time
    """, (stop_key,)).fetchall()

def find_duplicate_stops():
    return conn.execute("""
        SELECT stop_key, stop_name, COUNT(*) AS count
        FROM stop
        GROUP BY stop_key, stop_name
        HAVING COUNT(*) > 1
    """).fetchall()

def find_duplicate_route_stop():
    return conn.execute("""
        SELECT route_key, stop_key, time, COUNT(*) AS count
        FROM route_stop
        GROUP BY route_key, stop_key, time
        HAVING COUNT(*) > 1
    """).fetchall()

def get_full_schedule():
    return conn.execute("""
        SELECT r.route_name, s.stop_name, rs.time
        FROM route_stop rs
        JOIN stop s ON rs.stop_key = s.stop_key
        JOIN route r ON r.route_key = rs.route_key
        ORDER BY r.route_key, rs.time
    """).fetchall()

def get_first_time_per_route():
    return conn.execute("""
        SELECT route_key, MIN(time)
        FROM route_stop
        WHERE time != 'REQ'
        GROUP BY route_key
        ORDER BY route_key
    """).fetchall()

def get_last_time_per_route():
    return conn.execute("""
        SELECT route_key, MAX(time)
        FROM route_stop
        WHERE time != 'REQ'
        GROUP BY route_key
        ORDER BY route_key
    """).fetchall()

def get_unused_stops():
    return conn.execute("""
        SELECT s.stop_key, s.stop_name
        FROM stop s
        LEFT JOIN route_stop rs ON s.stop_key = rs.stop_key
        WHERE rs.stop_key IS NULL
        ORDER BY s.stop_key
    """).fetchall()

def get_routes_without_stops():
    return conn.execute("""
        SELECT r.route_key, r.route_name
        FROM route r
        LEFT JOIN route_stop rs ON r.route_key = rs.route_key
        WHERE rs.route_key IS NULL
        ORDER BY r.route_key
    """).fetchall()

def get_routes_serving_each_stop():
    return conn.execute("""
        SELECT s.stop_name, COUNT(DISTINCT rs.route_key) AS routes_serving
        FROM route_stop rs
        JOIN stop s ON rs.stop_key = s.stop_key
        GROUP BY s.stop_key
        ORDER BY routes_serving DESC, s.stop_name
    """).fetchall()

def get_times_at_stop(stop_key):
    return conn.execute("""
        SELECT r.route_name, rs.time
        FROM route_stop rs
        JOIN route r ON rs.route_key = r.route_key
        WHERE rs.stop_key = ?
        ORDER BY rs.time
    """, (stop_key,)).fetchall()

def insert_route_stop(route_key, stop_key, time_str):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO route_stop (route_key, stop_key, time) VALUES (?, ?, ?)",
        (route_key, stop_key, time_str)
    )
    conn.commit()
    return cur.rowcount

def get_all_drivers():
    return conn.execute("SELECT driver_key, driver_name FROM driver").fetchall()

def create_review(route_key, driver_key, text, score):
    cur = conn.cursor()
    cur.execute("INSERT INTO passenger_review (review_text, review_score) VALUES (?, ?)", (text, score))
    review_id = cur.lastrowid
    cur.execute("INSERT INTO route_driver_review (route_key, driver_key, review_id) VALUES (?, ?, ?)",
                (route_key, driver_key, review_id))
    conn.commit()
    return review_id

def get_reviews_for_route(route_key):
    return conn.execute("""
        SELECT pr.review_id, pr.review_score, pr.review_text, d.driver_name
        FROM route_driver_review rdr
        JOIN passenger_review pr ON rdr.review_id = pr.review_id
        JOIN driver d ON rdr.driver_key = d.driver_key
        WHERE rdr.route_key = ?
        ORDER BY pr.review_score DESC
    """, (route_key,)).fetchall()

def get_all_driver_route_assignments():
    return conn.execute("""
        SELECT d.driver_name, dr.route_key
        FROM driver d
        LEFT JOIN driver_route dr ON d.driver_key = dr.driver_key
        ORDER BY d.driver_key, dr.route_key
    """).fetchall()

def get_drivers_without_routes():
    return conn.execute("""
        SELECT d.driver_key, d.driver_name
        FROM driver d
        LEFT JOIN driver_route dr ON d.driver_key = dr.driver_key
        WHERE dr.route_key IS NULL
        ORDER BY d.driver_key
    """).fetchall()

def get_route_driver_assignments():
    return conn.execute("""
        SELECT r.route_key, r.route_name, d.driver_name
        FROM route r
        LEFT JOIN driver_route dr ON r.route_key = dr.route_key
        LEFT JOIN driver d ON d.driver_key = dr.driver_key
        ORDER BY r.route_key
    """).fetchall()

def get_routes_with_reviews_for_driver(driver_key):
    return conn.execute("""
        SELECT DISTINCT rdr.route_key
        FROM route_driver_review rdr
        WHERE rdr.driver_key = ?
    """, (driver_key,)).fetchall()

def get_best_driver_by_avg_score():
    return conn.execute("""
        SELECT d.driver_key, d.driver_name, AVG(pr.review_score)
        FROM driver d
        JOIN route_driver_review rdr ON d.driver_key = rdr.driver_key
        JOIN passenger_review pr ON rdr.review_id = pr.review_id
        GROUP BY d.driver_key
        ORDER BY AVG(pr.review_score) DESC
        LIMIT 1
    """).fetchone()

def get_drivers_with_no_reviews():
    return conn.execute("""
        SELECT d.driver_key, d.driver_name
        FROM driver d
        LEFT JOIN route_driver_review rdr ON d.driver_key = rdr.driver_key
        WHERE rdr.review_id IS NULL
        ORDER BY d.driver_key
    """).fetchall()

def get_drivers_with_most_5star():
    return conn.execute("""
        SELECT d.driver_key, d.driver_name, COUNT(pr.review_id)
        FROM driver d
        JOIN route_driver_review rdr ON d.driver_key = rdr.driver_key
        JOIN passenger_review pr ON rdr.review_id = pr.review_id
        WHERE pr.review_score = 5
        GROUP BY d.driver_key
        ORDER BY COUNT(pr.review_id) DESC
    """).fetchall()

def get_low_score_reviews_for_route(route_key, threshold):
    return conn.execute("""
        SELECT pr.review_id, pr.review_score, pr.review_text
        FROM route_driver_review rdr
        JOIN passenger_review pr ON rdr.review_id = pr.review_id
        WHERE rdr.route_key = ? AND pr.review_score <= ?
    """, (route_key, threshold)).fetchall()

def count_reviews_per_route():
    return conn.execute("""
        SELECT route_key, COUNT(review_id)
        FROM route_driver_review
        GROUP BY route_key
        ORDER BY COUNT(review_id) DESC
    """).fetchall()

def get_poor_routes(avg_threshold):
    return conn.execute("""
        SELECT r.route_key, r.route_name, AVG(pr.review_score)
        FROM route r
        JOIN route_driver_review rdr ON r.route_key = rdr.route_key
        JOIN passenger_review pr ON rdr.review_id = pr.review_id
        GROUP BY r.route_key
        HAVING AVG(pr.review_score) < ?
    """, (avg_threshold,)).fetchall()

def get_best_review_per_route():
    return conn.execute("""
        SELECT r.route_key, r.route_name, pr.review_id, pr.review_score, pr.review_text
        FROM route r
        JOIN route_driver_review rdr ON r.route_key = rdr.route_key
        JOIN passenger_review pr ON rdr.review_id = pr.review_id
        WHERE pr.review_score = (
            SELECT MAX(pr2.review_score)
            FROM route_driver_review rdr2
            JOIN passenger_review pr2 ON rdr2.review_id = pr2.review_id
            WHERE rdr2.route_key = r.route_key
        )
        ORDER BY r.route_key
    """).fetchall()

def get_worst_reviews(limit):
    return conn.execute("""
        SELECT review_id, review_score, review_text
        FROM passenger_review
        ORDER BY review_score ASC, review_id ASC
        LIMIT ?
    """, (limit,))


# ----------------------------------
# ROUTES & SCHEDULE PAGE
# ----------------------------------
if menu == "Routes & Schedule":
    st.subheader("All Bus Routes (Query 1)")
    routes = get_all_routes()
    st.table(routes)

    st.markdown("---")
    st.subheader("View Route Schedule (Query 3)")
    route_dict = {f"{r[0]} — {r[1]}": r[0] for r in routes}

    col1, col2 = st.columns([1, 2])
    with col1:
        selected_label = st.selectbox("Choose a route:", list(route_dict.keys()))
        selected_route_key = route_dict[selected_label]

    with col2:
        st.write(f"**Schedule for Route {selected_route_key}:**")
        schedule = get_route_schedule(selected_route_key)
        st.table(schedule if schedule else [])


# ----------------------------------
# STOPS PAGE
# ----------------------------------
elif menu == "Stops":
    st.subheader("All Stops (Query 2)")
    st.table(get_all_stops())

    st.markdown("---")
    st.subheader("Stops for a Specific Route (Query 4)")
    all_routes = get_all_routes()
    route_dict = {f"{r[0]} — {r[1]}": r[0] for r in all_routes}

    selected_label = st.selectbox("Choose a route:", list(route_dict.keys()))
    rk = route_dict[selected_label]

    stops = get_stops_for_route(rk)
    st.table(stops if stops else [])


# ----------------------------------
# DIAGNOSTICS PAGE
# ----------------------------------
elif menu == "Stop & Route Diagnostics":
    st.subheader("Stop-Time Counts per Route (Query 5)")
    st.table(get_stop_time_counts_by_route())

    st.markdown("---")
    st.subheader("Routes that Serve a Given Stop (Query 6)")
    stop_list = get_all_stops()
    stop_dict = {f"{s[0]} — {s[1]}": s[0] for s in stop_list}
    stop_sel = st.selectbox("Select a stop:", list(stop_dict.keys()))
    stop_key = stop_dict[stop_sel]

    st.table(get_routes_for_stop(stop_key))

    st.markdown("---")
    st.subheader("Duplicate Stops (Query 7)")
    st.table(find_duplicate_stops())

    st.markdown("---")
    st.subheader("Duplicate Route_Stop Entries (Query 8)")
    st.table(find_duplicate_route_stop())

    st.markdown("---")
    st.subheader("Full Schedule (Query 9)")
    st.table(get_full_schedule())

    st.markdown("---")
    st.subheader("First/Last Times per Route (Queries 10 & 11)")
    col1, col2 = st.columns(2)
    with col1:
        st.write("First Times")
        st.table(get_first_time_per_route())
    with col2:
        st.write("Last Times")
        st.table(get_last_time_per_route())

    st.markdown("---")
    st.subheader("Unused Stops (Query 12)")
    st.table(get_unused_stops())

    st.markdown("---")
    st.subheader("Routes Without Stops (Query 13)")
    st.table(get_routes_without_stops())

    st.markdown("---")
    st.subheader("Routes Serving Each Stop (Query 14)")
    st.table(get_routes_serving_each_stop())

    st.markdown("---")
    st.subheader("Times at a Stop (Query 15)")
    stop_sel2 = st.selectbox("Select stop:", list(stop_dict.keys()), key="stop_time")
    sk2 = stop_dict[stop_sel2]
    st.table(get_times_at_stop(sk2))


# ----------------------------------
# TRIP PLANNER (FIXED VERSION)
# ----------------------------------
elif menu == "Trip Planner":
    st.subheader("Trip Planner")

    stops = get_all_stops()
    stop_dict = {f"{s[0]} — {s[1]}": s[0] for s in stops}
    reverse_stop_dict = {s[0]: s[1] for s in stops}

    start_label = st.selectbox("Starting Stop:", list(stop_dict.keys()))
    end_label = st.selectbox("Destination Stop:", list(stop_dict.keys()))

    start_key = stop_dict[start_label]
    end_key = stop_dict[end_label]

    def parse_time(tstr):
        try:
            return datetime.strptime(tstr, "%H:%M").time()
        except:
            return None  # REQ or invalid

    def next_bus_time(bus_times):
        now = datetime.now().time()
        # Convert all to times, skip invalid
        valid_times = [(t, parse_time(t)) for t in bus_times if t != "REQ"]
        if not valid_times:
            return None
        future_times = [(t, tt) for t, tt in valid_times if tt >= now]
        if future_times:
            return min(future_times, key=lambda x: x[1])
        else:
            # all earlier than now, pick earliest next day
            return min(valid_times, key=lambda x: x[1])

    if st.button("Plan Trip"):
        st.markdown("### 🚏 Trip Results")

        # Check for direct routes
        direct_routes = conn.execute("""
            SELECT DISTINCT r.route_key, r.route_name
            FROM route r
            JOIN route_stop rs1 ON r.route_key = rs1.route_key
            JOIN route_stop rs2 ON r.route_key = rs2.route_key
            WHERE rs1.stop_key = ? AND rs2.stop_key = ?
        """, (start_key, end_key)).fetchall()

        if direct_routes:
            rkey = direct_routes[0][0]
            rname = direct_routes[0][1]
            # Get all times for this route at start stop
            start_times = [row[0] for row in conn.execute("""
                SELECT time FROM route_stop
                WHERE route_key=? AND stop_key=?
            """, (rkey, start_key)).fetchall()]
            next_bus = next_bus_time(start_times)
            if next_bus:
                st.success(f"Direct route found: **Route {rkey} — {rname}**")
                st.write(f"Next departure from {reverse_stop_dict[start_key]} at **{next_bus[0]}**")
            else:
                st.warning("Direct route exists but no upcoming buses found.")
        else:
            st.info("No direct route — planning transfer via UTC...")
            # Find UTC stop
            utc_row = conn.execute("SELECT stop_key FROM stop WHERE stop_name LIKE '%UTC%'").fetchone()
            if utc_row is None:
                st.error("UTC stop not found in database!")
            else:
                utc_key = utc_row[0]
                # Next bus from start → UTC
                start_to_utc = conn.execute("""
                    SELECT r.route_key, r.route_name, rs.time
                    FROM route r
                    JOIN route_stop rs ON r.route_key = rs.route_key
                    WHERE rs.stop_key=?
                """, (utc_key,)).fetchall()
                # Filter by next time after now
                start_times = [row[2] for row in start_to_utc]
                next_start_bus = next_bus_time(start_times)
                # Next bus from UTC → end
                utc_to_end = conn.execute("""
                    SELECT r.route_key, r.route_name, rs.time
                    FROM route r
                    JOIN route_stop rs ON r.route_key = rs.route_key
                    WHERE rs.stop_key=?
                """, (end_key,)).fetchall()
                end_times = [row[2] for row in utc_to_end]
                next_end_bus = next_bus_time(end_times)

                st.success(f"Trip requires a transfer at UTC.")
                if next_start_bus:
                    st.write(f"Take Route {next_start_bus[0]} from {reverse_stop_dict[start_key]} at **{next_start_bus[0]}** towards UTC")
                else:
                    st.warning("No upcoming buses from start to UTC found.")
                if next_end_bus:
                    st.write(f"Then take Route {next_end_bus[0]} from UTC to {reverse_stop_dict[end_key]}")
                else:
                    st.warning("No upcoming buses from UTC to destination found.")


# ----------------------------------
# DRIVERS PAGE
# ----------------------------------
elif menu == "Drivers":
    st.subheader("Drivers & Their Route Assignments")
    drivers = get_all_drivers()
    for dk, name in drivers:
        routes = conn.execute("""
            SELECT r.route_name
            FROM route r
            JOIN driver_route dr ON r.route_key = dr.route_key
            WHERE dr.driver_key = ?
        """, (dk,)).fetchall()
        route_list = ", ".join(r[0] for r in routes) if routes else "No routes assigned"
        st.write(f"**{name} (ID {dk})** — {route_list}")


# ----------------------------------
# DRIVER ANALYTICS
# ----------------------------------
elif menu == "Driver Analytics":
    st.subheader("Driver–Route Assignments (Query 17)")
    st.table(get_all_driver_route_assignments())

    st.markdown("---")
    st.subheader("Drivers With No Routes (Query 18)")
    st.table(get_drivers_without_routes())

    st.markdown("---")
    st.subheader("Route → Driver Assignments (Query 19)")
    st.table(get_route_driver_assignments())

    st.markdown("---")
    st.subheader("Routes a Driver Has Reviews For (Query 20)")
    all_drivers = get_all_drivers()
    driver_dict = {f"{d[0]} — {d[1]}": d[0] for d in all_drivers}
    sel = st.selectbox("Choose a driver:", list(driver_dict.keys()))
    dk = driver_dict[sel]
    st.table(get_routes_with_reviews_for_driver(dk))

    st.markdown("---")
    st.subheader("Best Driver by Average Score (Query 21)")
    st.table([get_best_driver_by_avg_score()])

    st.markdown("---")
    st.subheader("Drivers With No Reviews (Query 24)")
    st.table(get_drivers_with_no_reviews())

    st.markdown("---")
    st.subheader("Drivers with Most 5-Star Reviews (Query 28)")
    st.table(get_drivers_with_most_5star())


# ----------------------------------
# LEAVE REVIEW
# ----------------------------------
elif menu == "Leave Review":
    st.subheader("Submit a Review")

    routes = get_all_routes()
    route_dict = {f"{r[0]} — {r[1]}": r[0] for r in routes}
    route_label = st.selectbox("Route:", list(route_dict.keys()))
    route_key = route_dict[route_label]

    drivers = get_all_drivers()
    driver_dict = {f"{d[0]} — {d[1]}": d[0] for d in drivers}
    driver_label = st.selectbox("Driver:", list(driver_dict.keys()))
    driver_key = driver_dict[driver_label]

    text = st.text_area("Review Text")
    score = st.slider("Score", 1, 5)

    if st.button("Submit"):
        create_review(route_key, driver_key, text, score)
        st.success("Review submitted!")


# ----------------------------------
# VIEW REVIEWS
# ----------------------------------
elif menu == "View Reviews":
    st.subheader("Reviews for a Route")

    route_dict = {f"{r[0]} — {r[1]}": r[0] for r in get_all_routes()}
    label = st.selectbox("Choose a route:", list(route_dict.keys()))
    route_key = route_dict[label]

    st.table(get_reviews_for_route(route_key))


# ----------------------------------
# REVIEW ANALYTICS
# ----------------------------------
elif menu == "Review Analytics":
    st.subheader("Low Score Reviews (Query 22)")
    route_dict = {f"{r[0]} — {r[1]}": r[0] for r in get_all_routes()}
    rlabel = st.selectbox("Select route:", list(route_dict.keys()))
    route_key = route_dict[rlabel]
    threshold = st.slider("Score threshold", 1, 5, 2)
    st.table(get_low_score_reviews_for_route(route_key, threshold))

    st.markdown("---")
    st.subheader("Review Counts (Query 23)")
    st.table(count_reviews_per_route())

    st.markdown("---")
    st.subheader("Poor Routes (Query 25)")
    st.table(get_poor_routes(3))

    st.markdown("---")
    st.subheader("Best Review per Route (Query 26)")
    st.table(get_best_review_per_route())

    st.markdown("---")
    st.subheader("Worst Reviews (Query 27)")
    limit = st.slider("How many?", 1, 20, 5)
    st.table(get_worst_reviews(limit))


# ----------------------------------
# ADMIN: INSERT ROUTE STOP
# ----------------------------------
elif menu == "Admin: Insert Route Stop":
    st.subheader("Insert Route Stop")

    routes = get_all_routes()
    route_dict = {f"{r[0]} — {r[1]}": r[0] for r in routes}
    route_sel = st.selectbox("Choose Route:", list(route_dict.keys()))
    route_key = route_dict[route_sel]

    stops = get_all_stops()
    stop_dict = {f"{s[0]} — {s[1]}": s[0] for s in stops}
    stop_sel = st.selectbox("Choose Stop:", list(stop_dict.keys()))
    stop_key = stop_dict[stop_sel]

    time_str = st.text_input("Time (HH:MM or REQ)")

    if st.button("Insert"):
        insert_route_stop(route_key, stop_key, time_str)
        st.success("Inserted!")
