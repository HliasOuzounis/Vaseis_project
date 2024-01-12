import sqlite3
import database
con = sqlite3.connect('app/databases/big_database.db')
cur = con.cursor()



def print_popular_airports(limit = 10):
    print("Popular airports:")
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
    print()

def print_well_reviewed_airplanes(limit = 10):
    print("Well reviewed airplanes:")
    for _airplane in cur.execute("""
        select Airplane_code, sum(Review)/count(*) as total_score
        from Airplane natural join Flight
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
        print(f"{airplane_code}: {airplane[1]} - score: {total_score}/5")
    print()

def print_well_reviewed_crew(limit = 10):
    print("Well reviewed crew:")
    for _employee in cur.execute("""
        select AFM, sum(Review)/count(*) as total_score
        from Employee natural join Mans
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
        print(f"{AFM}: {employee[1]} - score: {total_score}/5")
    print()

def print_popular_days(limit = 10):
    print("Days with most flights:")
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

def print_users_with_most_purchases(limit = 10):
    print("Users with most purchases:")
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
    print()

def print_users_with_most_referrals(limit = 10):
    print("Users with most referrals:")
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
    print()

def print_users_with_most_points(limit = 10):
    print("Users with most points:")
    for _user in cur.execute("""
        select Username, Points
        from User
        order by Points desc
        limit ?
    """, (limit,)).fetchall():
        username = _user[0]
        points = _user[1]
        print(f"{username}: {points} points")
    print()

def print_most_cancelled_flight(limit = 10):
    print("Most cancelled flights:")
    for _flight in cur.execute("""
        select Flight_code, count(*) as num_cancels
        from Flight natural join Ticket natural join Cancels
        group by Flight_code
        order by num_cancels desc
        limit ?
    """, (limit,)).fetchall():
        flight_code = _flight[0]
        num_cancels = _flight[1]
        print(f"{flight_code}: {num_cancels} cancellations")
    print()

# print_popular_airports(5)
# print_well_reviewed_airplanes(5)
# print_well_reviewed_crew(5)
# print_popular_days(5)
# print_users_with_most_purchases(5)
# print_users_with_most_referrals(5)
# print_users_with_most_points(5)
print_most_cancelled_flight(5)
