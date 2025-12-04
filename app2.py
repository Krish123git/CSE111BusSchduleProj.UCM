def main():
    conn = sqlite3.connect("BusDatabase.sqlite")
    while True:
        print("\n1. View all routes")
        print("2. View route schedule")
        print("3. Leave a review")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            for r in get_all_routes(conn):
                print(r)
        elif choice == "2":
            route_id = int(input("Enter route ID: "))
            schedule = get_route_schedule(conn, route_id)
            for stop, time in schedule:
                print(stop, time)
        elif choice == "3":
            route_id = int(input("Route ID: "))
            driver_id = int(input("Driver ID: "))
            text = input("Review text: ")
            score = int(input("Score 1-5: "))
            review_id = create_review(conn, route_id, driver_id, text, score)
            print("Review added with ID:", review_id)
        elif choice == "4":
            break
    conn.close()

if __name__ == "__main__":
    main()
