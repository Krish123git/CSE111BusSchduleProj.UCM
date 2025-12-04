import sqlite3

def get_all_routes(conn):
    cur = conn.cursor()
    cur.execute("SELECT route_key, route_name FROM route")
    return cur.fetchall()

def get_route_schedule(conn, route_key):
    cur = conn.cursor()
    cur.execute("""
        SELECT s.stop_name, rs.time
        FROM route_stop rs
        JOIN stop s ON rs.stop_key = s.stop_key
        WHERE rs.route_key = ?
        ORDER BY rs.time
    """, (route_key,))
    return cur.fetchall()

def create_review(conn, route_key, driver_key, text, score):
    cur = conn.cursor()
    cur.execute("INSERT INTO passenger_review (review_text, review_score) VALUES (?, ?)", (text, score))
    review_id = cur.lastrowid
    cur.execute("INSERT INTO route_driver_review (route_key, driver_key, review_id) VALUES (?, ?, ?)", (route_key, driver_key, review_id))
    conn.commit()
    return review_id


# Connect to your DB
conn = sqlite3.connect("BusDatabase.sqlite")
cursor = conn.cursor()

# Example: fetch all routes
cursor.execute("SELECT route_key, route_name FROM route")
routes = cursor.fetchall()
for r in routes:
    print(r)

conn.close()
