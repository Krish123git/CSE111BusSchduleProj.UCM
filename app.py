# This was the library that chatGPT suggests to use, it looks simple but looks nice!


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
    return conn.execute("""
        SELECT pr.review_id, pr.review_score, pr.review_text, d.driver_name
        FROM route_driver_review rdr
        JOIN passenger_review pr ON rdr.review_id = pr.review_id
        JOIN driver d ON rdr.driver_key = d.driver_key
        WHERE rdr.route_key = ?
        ORDER BY pr.review_score DESC
    """, (route_key,)).fetchall()

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
