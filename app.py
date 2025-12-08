# This was the library that chatGPT suggests to use, it looks simple but looks nice!

# If you run it on your machine, install streamlit with pip install streamlit first
import streamlit as st
import sqlite3


# Connect to SQLite database
conn = sqlite3.connect("BusDatabase.sqlite", check_same_thread=False)

st.title("School Bus System")

menu = st.sidebar.selectbox("Menu", ["View Routes", "Route Schedule", "View Drivers", "Leave Review", "View Reviews"])

# ---------- Helper Functions ----------
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
    return conn.execute("""A
        SELECT pr.review_id, pr.review_score, pr.review_text, d.driver_name
        FROM route_driver_review rdr
        JOIN passenger_review pr ON rdr.review_id = pr.review_id
        JOIN driver d ON rdr.driver_key = d.driver_key
        WHERE rdr.route_key = ?
        ORDER BY pr.review_score DESC
    """, (route_key,)).fetchall()

#--------------------------------------------------
# 2. Get all stops
def get_all_stops():
    """Query 2: Get all stops."""
    return conn.execute("SELECT stop_key, stop_name FROM stop ORDER BY stop_key").fetchall()


# 4. Get all stops in correct order for a route (distinct list)
def get_stops_for_route(route_key: int):
    """Query 4: Distinct ordered list of stops for a route."""
    return conn.execute(
        """
        SELECT DISTINCT s.stop_name
        FROM route_stop rs
        JOIN stop s ON rs.stop_key = s.stop_key
        WHERE rs.route_key = ?
        ORDER BY rs.stop_key
        """,
        (route_key,),
    ).fetchall()


# 5. Count how many stop-times exist per route
def get_stop_time_counts_by_route():
    """Query 5: Count how many stop-times exist per route."""
    return conn.execute(
        """
        SELECT route_key, COUNT(*) AS total_times
        FROM route_stop
        GROUP BY route_key
        ORDER BY route_key
        """
    ).fetchall()


# 6. List all routes that service a specific stop
def get_routes_for_stop(stop_key: int):
    """Query 6: List all routes that service a specific stop."""
    return conn.execute(
        """
        SELECT r.route_name, rs.time
        FROM route_stop rs
        JOIN route r ON r.route_key = rs.route_key
        WHERE rs.stop_key = ?
        ORDER BY rs.time
        """,
        (stop_key,),
    ).fetchall()


# 7. Find duplicate stop entries
def find_duplicate_stops():
    """Query 7: Find duplicate stop entries (should be none)."""
    return conn.execute(
        """
        SELECT stop_key, stop_name, COUNT(*) AS count
        FROM stop
        GROUP BY stop_key, stop_name
        HAVING COUNT(*) > 1
        """
    ).fetchall()


# 8. Find duplicate route_stop entries
def find_duplicate_route_stop():
    """Query 8: Find duplicate route_stop entries."""
    return conn.execute(
        """
        SELECT route_key, stop_key, time, COUNT(*) AS count
        FROM route_stop
        GROUP BY route_key, stop_key, time
        HAVING COUNT(*) > 1
        """
    ).fetchall()


# 9. View full schedule for ALL routes
def get_full_schedule():
    """Query 9: View full schedule for all routes, ordered neatly."""
    return conn.execute(
        """
        SELECT r.route_name, s.stop_name, rs.time
        FROM route_stop rs
        JOIN stop s ON rs.stop_key = s.stop_key
        JOIN route r ON r.route_key = rs.route_key
        ORDER BY r.route_key, rs.time
        """
    ).fetchall()


# 10. Show first stop time for each route
def get_first_time_per_route():
    """
    Query 10: Show first stop time for each route.
    Assumes times are now in 24-hour HH:MM format and 'REQ' was left as-is.
    """
    return conn.execute(
        """
        SELECT route_key, MIN(time) AS first_time
        FROM route_stop
        WHERE time != 'REQ'
        GROUP BY route_key
        ORDER BY route_key
        """
    ).fetchall()


# 11. Show last stop time for each route
def get_last_time_per_route():
    """Query 11: Show last stop time for each route."""
    return conn.execute(
        """
        SELECT route_key, MAX(time) AS last_time
        FROM route_stop
        WHERE time != 'REQ'
        GROUP BY route_key
        ORDER BY route_key
        """
    ).fetchall()


# 12. Check stops that are never used by any route
def get_unused_stops():
    """Query 12: Stops that are never used in route_stop."""
    return conn.execute(
        """
        SELECT s.stop_key, s.stop_name
        FROM stop s
        LEFT JOIN route_stop rs ON s.stop_key = rs.stop_key
        WHERE rs.stop_key IS NULL
        ORDER BY s.stop_key
        """
    ).fetchall()


# 13. Check routes that have no stops
def get_routes_without_stops():
    """Query 13: Routes that have no stops."""
    return conn.execute(
        """
        SELECT r.route_key, r.route_name
        FROM route r
        LEFT JOIN route_stop rs ON r.route_key = rs.route_key
        WHERE rs.route_key IS NULL
        ORDER BY r.route_key
        """
    ).fetchall()


# 14. List stops and how many routes serve them
def get_routes_serving_each_stop():
    """Query 14: List stops and how many routes serve them."""
    return conn.execute(
        """
        SELECT s.stop_name, COUNT(DISTINCT rs.route_key) AS routes_serving
        FROM route_stop rs
        JOIN stop s ON rs.stop_key = s.stop_key
        GROUP BY s.stop_key
        ORDER BY routes_serving DESC, s.stop_name
        """
    ).fetchall()


# 15. Show all times at a stop throughout the day
def get_times_at_stop(stop_key: int):
    """Query 15: Show all times at a stop throughout the day."""
    return conn.execute(
        """
        SELECT r.route_name, rs.time
        FROM route_stop rs
        JOIN route r ON rs.route_key = r.route_key
        WHERE rs.stop_key = ?
        ORDER BY rs.time
        """,
        (stop_key,),
    ).fetchall()


# 16. Insert a new route_stop time
def insert_route_stop(route_key: int, stop_key: int, time_str: str):
    """Query 16: Insert a new route_stop time."""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO route_stop (route_key, stop_key, time) VALUES (?, ?, ?)",
        (route_key, stop_key, time_str),
    )
    conn.commit()
    return cur.rowcount


# 17. List all drivers and the routes they are assigned to
def get_all_driver_route_assignments():
    """Query 17: List all drivers and the routes they are assigned to."""
    return conn.execute(
        """
        SELECT d.driver_name, dr.route_key
        FROM driver d
        LEFT JOIN driver_route dr ON d.driver_key = dr.driver_key
        ORDER BY d.driver_key, dr.route_key
        """
    ).fetchall()


# 18. Show all drivers who have NOT been assigned to any route
def get_drivers_without_routes():
    """Query 18: Drivers with no route assignment."""
    return conn.execute(
        """
        SELECT d.driver_key, d.driver_name
        FROM driver d
        LEFT JOIN driver_route dr ON d.driver_key = dr.driver_key
        WHERE dr.route_key IS NULL
        ORDER BY d.driver_key
        """
    ).fetchall()


# 19. For each route, show the assigned driver
def get_route_driver_assignments():
    """Query 19: For each route, show the assigned driver."""
    return conn.execute(
        """
        SELECT r.route_key, r.route_name, d.driver_name
        FROM route r
        LEFT JOIN driver_route dr ON r.route_key = dr.route_key
        LEFT JOIN driver d ON d.driver_key = dr.driver_key
        ORDER BY r.route_key
        """
    ).fetchall()


# 20. Get all routes a driver has reviews for
def get_routes_with_reviews_for_driver(driver_key: int):
    """Query 20: Get all routes a driver has reviews for."""
    return conn.execute(
        """
        SELECT DISTINCT rdr.route_key
        FROM route_driver_review rdr
        WHERE rdr.driver_key = ?
        """,
        (driver_key,),
    ).fetchall()


# 21. Find which driver has the highest-rated average score
def get_best_driver_by_avg_score():
    """Query 21: Driver with the highest-rated average score."""
    return conn.execute(
        """
        SELECT 
            d.driver_key,
            d.driver_name,
            AVG(pr.review_score) AS avg_score
        FROM driver d
        JOIN route_driver_review rdr ON d.driver_key = rdr.driver_key
        JOIN passenger_review pr ON rdr.review_id = pr.review_id
        GROUP BY d.driver_key, d.driver_name
        ORDER BY avg_score DESC
        LIMIT 1
        """
    ).fetchone()


# 22. All low-score reviews (score <= 2) for a route
def get_low_score_reviews_for_route(route_key: int, threshold: int = 2):
    """Query 22: Reviews for a route with score <= threshold."""
    return conn.execute(
        """
        SELECT 
            pr.review_id,
            pr.review_score,
            pr.review_text
        FROM route_driver_review rdr
        JOIN passenger_review pr ON rdr.review_id = pr.review_id
        WHERE rdr.route_key = ?
          AND pr.review_score <= ?
        """,
        (route_key, threshold),
    ).fetchall()


# 23. Count reviews per route
def count_reviews_per_route():
    """Query 23: Count reviews per route."""
    return conn.execute(
        """
        SELECT 
            rdr.route_key,
            COUNT(rdr.review_id) AS review_count
        FROM route_driver_review rdr
        GROUP BY rdr.route_key
        ORDER BY review_count DESC
        """
    ).fetchall()


# 24. List drivers with no reviews
def get_drivers_with_no_reviews():
    """Query 24: Drivers with no reviews."""
    return conn.execute(
        """
        SELECT d.driver_key, d.driver_name
        FROM driver d
        LEFT JOIN route_driver_review rdr ON d.driver_key = rdr.driver_key
        WHERE rdr.review_id IS NULL
        ORDER BY d.driver_key
        """
    ).fetchall()


# 25. Get routes with an average review score below 3
def get_poor_routes(avg_threshold: int = 3):
    """Query 25: Routes with average review score below threshold."""
    return conn.execute(
        """
        SELECT 
            r.route_key,
            r.route_name,
            AVG(pr.review_score) AS avg_score
        FROM route r
        JOIN route_driver_review rdr ON r.route_key = rdr.route_key
        JOIN passenger_review pr ON rdr.review_id = pr.review_id
        GROUP BY r.route_key, r.route_name
        HAVING avg_score < ?
        ORDER BY avg_score ASC
        """,
        (avg_threshold,),
    ).fetchall()


# 26. Get the highest-rated review for each route
def get_best_review_per_route():
    """Query 26: Highest-rated review for each route."""
    return conn.execute(
        """
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
        ORDER BY r.route_key, pr.review_id
        """
    ).fetchall()


# 27. Get the worst 5 reviews systemwide
def get_worst_reviews(limit: int = 5):
    """Query 27: Worst N reviews systemwide."""
    return conn.execute(
        """
        SELECT review_id, review_score, review_text
        FROM passenger_review
        ORDER BY review_score ASC, review_id ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


# 28. See which driver handled the most 5-star reviews
def get_drivers_with_most_5star():
    """Query 28: Drivers with counts of 5-star reviews."""
    return conn.execute(
        """
        SELECT 
            d.driver_key,
            d.driver_name,
            COUNT(pr.review_id) AS five_star_reviews
        FROM driver d
        JOIN route_driver_review rdr ON d.driver_key = rdr.driver_key
        JOIN passenger_review pr ON rdr.review_id = pr.review_id
        WHERE pr.review_score = 5
        GROUP BY d.driver_key, d.driver_name
        ORDER BY five_star_reviews DESC
        """
    ).fetchall()

# ---------- Menu ----------
if menu == "View Routes":
    st.subheader("All Bus Routes")
    routes = get_all_routes()
    st.table(routes)

elif menu == "Route Schedule":
    st.subheader("Route Schedule")
    route_key = st.number_input("Enter Route ID", min_value=1)
    if st.button("Show Schedule"):
        schedule = get_route_schedule(route_key)
        if schedule:
            st.table(schedule)
        else:
            st.warning("No schedule found for this route.")

elif menu == "View Drivers":
    st.subheader("Drivers and their Routes")
    drivers = get_all_drivers()
    for dk, name in drivers:
        routes = conn.execute("""
            SELECT r.route_name
            FROM route r
            JOIN driver_route dr ON r.route_key = dr.route_key
            WHERE dr.driver_key = ?
        """, (dk,)).fetchall()
        route_list = ", ".join(r[0] for r in routes) if routes else "No routes assigned"
        st.write(f"{name} (ID {dk}): {route_list}")

elif menu == "Leave Review":
    st.subheader("Leave a Review for a Driver on a Route")
    route_key = st.number_input("Route ID", min_value=1)
    driver_key = st.number_input("Driver ID", min_value=1)
    review_text = st.text_area("Review Text")
    score = st.slider("Score (1-5)", 1, 5)
    if st.button("Submit Review"):
        review_id = create_review(route_key, driver_key, review_text, score)
        st.success(f"Review added with ID {review_id}")

elif menu == "View Reviews":
    st.subheader("View Reviews for a Route")
    route_key = st.number_input("Route ID", min_value=1)
    if st.button("Show Reviews"):
        reviews = get_reviews_for_route(route_key)
        if reviews:
            st.table(reviews)
        else:
            st.warning("No reviews for this route.")
