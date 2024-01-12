import sqlite3
from datetime import datetime

con = sqlite3.connect('app/databases/big_database.db')
cur = con.cursor()


def get_all_cities():
    return cur.execute('SELECT Name FROM City').fetchall()


def get_all_flights(depart_city, arrival_city, depart_day):
    departure_city_code = cur.execute(
        'SELECT City_code FROM City WHERE Name = ?', (depart_city,)).fetchone()[0]
    arrival_city_code = cur.execute(
        'SELECT City_code FROM City WHERE Name = ?', (arrival_city,)).fetchone()[0]

    return cur.execute("""
		select *
		from flight
		where Departure_airport_code in (select Airport_Code from Airport where City_code == ?)
		and Arrival_airport_code in (select Airport_Code from Airport where City_code == ?)
		and date(Scheduled_departure_datetime) == date(?)
	""", (departure_city_code, arrival_city_code, depart_day)).fetchall()


def get_available_seats(flight_id):
    return cur.execute("""
        select * 
        from seat
        where Flight_code = ?
        and seat.number not in (
            select Seat_number from purchases 
            where Flight_code = seat.Flight_code
            and Ticket_code not in (select Ticket_code from Cancels)
        )
    """, (flight_id, )).fetchall()


def cancel_ticket(ticket_code, username, date):
    cur.execute(
        'INSERT INTO Cancels VALUES (?, ?, ?)', (ticket_code, username, date))
    # subtract points
    # can be abused by buying a ticket, spending the points, and then cancelling the ticket
    cur.execute(
        'UPDATE User SET Points = Points - (SELECT Price FROM Ticket WHERE Ticket_code = ?) WHERE username = ?', (ticket_code, username))
    con.commit()


def buy_ticket(username, bank_details, seats, date):
    # seats = [(flight_id, seat_number), ...]
    # create ticket
    ticket_price = sum(cur.execute(
        'select price from seat where Flight_code = ? and number = ?', seat).fetchone()[0] for seat in seats)
    ticket_code = hash(str(username) + str(bank_details) + str(seats) + str(date))
    ticket_code = [ticket_code] * len(seats)
    cur.execute('INSERT INTO Ticket VALUES (?, ?, ?)', (ticket_code, ticket_price, 0))
    
    # award points
    cur.execute('UPDATE User SET Points = Points + ? WHERE username = ?', (ticket_price // 10, username))
    
    # save purchase
    username = [username] * len(seats)
    bank_details = [bank_details] * len(seats)
    date = [date] * len(seats)
    flights = [seat[0] for seat in seats]
    seat_numbers = [seat[1] for seat in seats]
    cur.executemany(
        'INSERT INTO Purchases VALUES (?, ?, ?, ?, ?, ?)', zip(ticket_code, username, bank_details, flights, seat_numbers, date))
    con.commit()

def check_for_user(username):
    return cur.execute('SELECT * FROM User WHERE Username = ?', (username,)).fetchone() is not None

def get_last_flight():
    result = cur.execute('SELECT * FROM Flight ORDER BY Actual_arrival_datetime DESC LIMIT 1').fetchone()
    if result is not None:
        return result[0]
    else:
        return None


def get_upcoming_flight(username):
    current_datetime = datetime.now()
    res = cur.execute('SELECT * FROM Flight WHERE Flight_code IN (SELECT Flight_code FROM Purchases WHERE Username = ?) AND Scheduled_departure_datetime > ? ORDER BY Scheduled_departure_datetime', (username, current_datetime)).fetchall()
    if len(res) > 0:
        return res[0]
    else:
        return None
    

def check_for_city(name):
    return cur.execute('SELECT * FROM City WHERE Name = ?', (name,)).fetchone() is not None

def get_user_points(username):
    return cur.execute('SELECT Points FROM User WHERE Username = ?', (username,)).fetchone()[0]


def create_new_user(username, password, salt, name, referred_by=None):
    cur.execute('INSERT INTO User VALUES (?, ?, ?, ?, ?, ?)',
                (username, password, salt, 0, name,  referred_by))
    if referred_by is not None:
        cur.execute(
            'UPDATE User SET Points = Points + 10 WHERE Username = ?', (referred_by,))
    con.commit()

def get_user_salt(username):
    return cur.execute('SELECT Salt FROM User WHERE Username = ?', (username,)).fetchone()[0]

def get_user_password(username):
    return cur.execute('SELECT Password FROM User WHERE Username = ?', (username,)).fetchone()[0]

def leave_review(username, flight_id, plane_rating, crew_rating, comment):
    cur.execute('INSERT INTO Reviews VALUES (?, ?, ?, ?, ?)',
                (username, flight_id, plane_rating, crew_rating, comment))
    airplane_id = cur.execute(
        'SELECT Airplane_code FROM Flight WHERE Flight_code = ?', (flight_id,)).fetchone()[0]
    crew_on_flight = cur.execute(
        'SELECT AFM FROM Mans WHERE Flight_code = ?', (flight_id,)).fetchall()

    # update airplane and crew rating
    cur.execute(
        'UPDATE Airplane SET Review = (SELECT AVG(Airplane_score) FROM Reviews WHERE Airplane_code = ?)', (airplane_id,))
    cur.executemany(
        'UPDATE Employee SET Review = (SELECT AVG(Employee_score) FROM Reviews WHERE AFM = ?)', crew_on_flight)
    con.commit()

def get_airplane_score(flight_id):
    return cur.execute('SELECT Review FROM Airplane WHERE Airplane_code = (SELECT Airplane_code FROM Flight WHERE Flight_code = ?)', (flight_id,)).fetchone()[0]

def get_crew_score(flight_id):
    return cur.execute('SELECT AVG(Review) FROM Employee WHERE AFM IN (SELECT AFM FROM Mans WHERE Flight_code = ?)', (flight_id,)).fetchone()[0]



def create_flight(departure_airport_code, arrival_airport_code, scheduled_departure_datetime, scheduled_arrival_datetime, airplane_code):
    
    flight_code = abs(hash(f"{departure_airport_code}{arrival_airport_code}{scheduled_departure_datetime}{scheduled_arrival_datetime}{airplane_code}"))
    cur.execute('INSERT INTO Flight VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (flight_code, 1000, airplane_code, departure_airport_code, arrival_airport_code, scheduled_departure_datetime, None,
                                                                scheduled_arrival_datetime, None))
    

    seat_numbers = cur.execute('SELECT First_class_seats, Business_class_seats, Economy_class_seats FROM Airplane WHERE Airplane_code = ?', (airplane_code,)).fetchone()
    for seat_class, ind in zip(("First Class", "Business", "Economy"), (0,1,2)):
        for seat_number in range(1, seat_numbers[ind]):
            print(seat_class, f"{seat_class[0]}{seat_number:03}", 50*(3-ind), flight_code)
            cur.execute('INSERT INTO Seat VALUES (?, ?, ?, ?)', (seat_class, f"{seat_class[0]}{seat_number:03}", 50*(3-ind), flight_code))
        
    con.commit()
    return

# print(flight_id := get_all_flights('New York', 'Miami', '2024-01-06')[0][0])
# print(seats := get_available_seats(flight_id))
# create_flight('A001', 'A002', '2024-01-06 10:00:00', '2024-01-06 18:00:00', 'AP001')

# con.close()
