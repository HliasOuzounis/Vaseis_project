import sqlite3
con = sqlite3.connect('databases/sample_database.db')
cur = con.cursor()
import time


def print_popular_airports(limit = 10):
    print("Popular airports:")
    start_time = time.time()
    for _airport in cur.execute("""
        select Arrival_airport_code, count(*) as num_flights
        from flight
        group by Arrival_airport_code
        order by num_flights desc
        limit ?
    """, (limit,)).fetchall():
        airport_code = _airport[0]
        num_flights = _airport[1]
        airport = cur.execute("""
            select *
            from Airport
            where Airport_Code = ?
        """, (airport_code,)).fetchone()
        city = cur.execute("""
            select Name
            from City
            where City_code = ?
        """, (airport[2],)).fetchone()[0]
        print(f"{airport_code}: {city} - {num_flights} flights")
    print("Execution time:", format((time.time() - start_time) * 1000, ".1f"), "milliseconds")
    print()

def print_well_reviewed_airplanes(limit = 10):
    print("Well reviewed airplanes:")
    start_time = time.time()
    for _airplane in cur.execute("""
        select Airplane_code, sum(Airplane_score)/count(*) as total_score
        from Airplane natural join Flight natural join Reviews
        group by Airplane_code
        order by total_score desc
        limit ?
    """, (limit,)).fetchall():
        airplane_code = _airplane[0]
        total_score = _airplane[1]
        airplane = cur.execute("""
            select *
            from Airplane
            where Airplane_code = ?
        """, (airplane_code,)).fetchone()
        print(f"{airplane_code}: {airplane[1]} - score: {total_score:.2f}/5")
    print("Execution time:", format((time.time() - start_time) * 1000, ".1f"), "milliseconds")
    print()

def print_well_reviewed_crew(limit = 10):
    print("Well reviewed crew:")
    start_time = time.time()
    for _employee in cur.execute("""
        select AFM, sum(Employee_score)/count(*) as total_score
        from Employee natural join Mans natural join Flight natural join Reviews
        group by AFM
        order by total_score desc
        limit ?
    """, (limit,)).fetchall():
        AFM = _employee[0]
        total_score = _employee[1]
        employee = cur.execute("""
            select *
            from Employee
            where AFM = ?
        """, (AFM,)).fetchone()
        print(f"{AFM}: {employee[1]} - score: {total_score:.2f}/5")
    print("Execution time:", format((time.time() - start_time) * 1000, ".1f"), "milliseconds")
    print()

def print_popular_days(limit = 10):
    print("Days with most flights:")
    start_time = time.time()
    for _day in cur.execute("""
        select strftime('%w', Scheduled_departure_datetime) as day, count(*) as num_flights
        from Flight
        group by day
        order by num_flights desc
        limit ?
    """, (limit,)).fetchall():
        day = _day[0]
        day = {
            "0": "Sunday",
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wednesday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Saturday"
        }[day]
        num_flights = _day[1]
        print(f"{day}: {num_flights} flights\n")
    print("Execution time:", format((time.time() - start_time) * 1000, ".1f"), "milliseconds")
    print()

def print_users_with_most_purchases(limit = 10):
    print("Users with most purchases:")
    start_time = time.time()
    for _user in cur.execute("""
        select Username, count(*) as num_purchases
        from User natural join Purchases
        where Ticket_code not in (select Ticket_code from Cancels) 
        group by Username
        order by num_purchases desc
        limit ?
    """, (limit,)).fetchall():
        username = _user[0]
        num_purchases = _user[1]
        print(f"{username}: {num_purchases} purchases")
    print("Execution time:", format((time.time() - start_time) * 1000, ".1f"), "milliseconds")
    print()

def print_users_with_most_referrals(limit = 10):
    print("Users with most referrals:")
    start_time = time.time()
    for _user in cur.execute("""
        select Username, count(*) as num_refers
        from User
        where Referred_by is not null
        group by Username
        order by num_refers desc
        limit ?
    """, (limit,)).fetchall():
        username = _user[0]
        num_refers = _user[1]
        print(f"{username}: {num_refers} referrals")
    print("Execution time:", format((time.time() - start_time) * 1000, ".1f"), "milliseconds")
    print()

def print_users_with_most_points(limit = 10):
    print("Users with most points:")
    start_time = time.time()
    for _user in cur.execute("""
        select Username, Points
        from User
        order by Points desc
        limit ?
    """, (limit,)).fetchall():
        username = _user[0]
        points = _user[1]
        print(f"{username}: {points} points")
    print("Execution time:", format((time.time() - start_time) * 1000, ".1f"), "milliseconds")
    print()

def print_most_cancelled_flights(limit = 10):
    print("Most cancelled flights:")
    start_time = time.time()
    for _flight in cur.execute("""
        select Flight.Flight_code, count(*) as num_cancels
        from Purchases natural join Flight, Cancels
        where Cancels.Ticket_code = Purchases.Ticket_code
        group by Flight.Flight_code
        order by num_cancels desc
        limit ?
    """, (limit,)).fetchall():
        flight_code = _flight[0]
        num_cancels = _flight[1]
        print(f"{flight_code}: {num_cancels} cancellations")
    print("Execution time:", format((time.time() - start_time) * 1000, ".1f"), "milliseconds")
    print()


def main():
    print_popular_airports(5)
    print_well_reviewed_airplanes(5)
    print_well_reviewed_crew(5)
    print_popular_days(5)
    print_users_with_most_purchases(5)
    print_users_with_most_referrals(5)
    print_users_with_most_points(5)
    print_most_cancelled_flights()
    print()


if __name__ == "__main__":
    main()
