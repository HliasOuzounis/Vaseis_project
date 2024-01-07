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
    pass


print(get_all_flights('New York', 'Miami', '2024-01-06'))
