import sqlite3

con = sqlite3.connect('app/database1.db')
cur = con.cursor()

cities = cur.execute('SELECT Name FROM Town').fetchall()


def get_all_flights(depart_city, arrival_city, depart_day):
    departure_town_code = cur.execute(
        'SELECT Town_code FROM Town WHERE Name = ?', (depart_city,)).fetchone()[0]
    arrival_town_code = cur.execute(
        'SELECT Town_code FROM Town WHERE Name = ?', (arrival_city,)).fetchone()[0]

    return cur.execute("""
		select *
		from flight
		where Departure_airport_code in (select Airport_Code from Airport where Town_code == ?)
		and Arrival_airport_code in (select Airport_Code from Airport where Town_code == ?)
		and date(Scheduled_departure_datetime) == date(?)
	""", (departure_town_code, arrival_town_code, depart_day)).fetchall()

def get_available_seats(flight_id):
    return cur.execute("""
        select * 
        from seat
        where Flight_code = ?
        and seat.number not in (
            select Seat_number from purchases 
            where Flight_code = ? 
            and Ticket_code not in (select Ticket_code from Cancels)
        )
    """, (flight_id, flight_id)).fetchall()


print(flight_id := get_all_flights('New York', 'Miami', '2024-01-06')[0][0])
print(seats := get_available_seats(flight_id))