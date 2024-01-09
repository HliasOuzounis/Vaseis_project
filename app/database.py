import sqlite3

con = sqlite3.connect('app/database1.db')
cur = con.cursor()


def get_all_cities():
    return cur.execute('SELECT Name FROM Town').fetchall()


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
            where Flight_code = seat.Flight_code
            and Ticket_code not in (select Ticket_code from Cancels)
        )
    """, (flight_id, )).fetchall()


def cancel_ticket(ticket_code, user_id, date):
    cur.execute(
        'INSERT INTO Cancels VALUES (?, ?, ?)', (ticket_code, user_id, date))
    # subtract points
    # can be abused by buying a ticket, spending the points, and then cancelling the ticket
    cur.execute(
        'UPDATE User SET Points = Points - (SELECT Price FROM Ticket WHERE Ticket_code = ?) WHERE User_code = ?', (ticket_code, user_id))
    con.commit()


def buy_ticket(user_id, bank_details, seats, date):
    # seats = [(flight_id, seat_number), ...]
    # create ticket
    ticket_price = sum(cur.execute(
        'select price from seat where Flight_code = ? and number = ?', seat).fetchone()[0] for seat in seats)
    ticket_code = hash(str(user_id) + str(bank_details) + str(seats) + str(date))
    ticket_code = [ticket_code] * len(seats)
    cur.execute('INSERT INTO Ticket VALUES (?, ?, ?)', (ticket_code, ticket_price, 0))
    
    # award points
    cur.execute('UPDATE User SET Points = Points + ? WHERE User_code = ?', (ticket_price // 10, user_id))
    
    # save purchase
    user_id = [user_id] * len(seats)
    bank_details = [bank_details] * len(seats)
    date = [date] * len(seats)
    flights = [seat[0] for seat in seats]
    seat_numbers = [seat[1] for seat in seats]
    cur.executemany(
        'INSERT INTO Purchases VALUES (?, ?, ?, ?, ?, ?)', zip(ticket_code, user_id, bank_details, flights, seat_numbers, date))
    con.commit()

def check_for_user(name):
    return cur.execute('SELECT * FROM User WHERE User_code = ?', (hash(name),)).fetchone() is not None

def get_last_flight():
    result = cur.execute('SELECT * FROM Flight ORDER BY Flight_code DESC LIMIT 1').fetchone()
    if result is not None:
        return result[0]
    else:
        return None

def check_for_city(name):
    return cur.execute('SELECT * FROM Town WHERE Name = ?', (name,)).fetchone() is not None

def get_user_points(name):
    return cur.execute('SELECT Points FROM User WHERE User_code = ?', (hash(name),)).fetchone()[0]


def create_new_user(name, referred_by=None):
    cur.execute('INSERT INTO User VALUES (?, ?, ?, ?)',
                (hash(name), 0, name, referred_by))
    if referred_by is not None:
        cur.execute(
            'UPDATE User SET Points = Points + 10 WHERE User_code = ?', (referred_by,))
    con.commit()


def leave_review(user_id, flight_id, plane_rating, crew_rating, comment):
    cur.execute('INSERT INTO Reviews VALUES (?, ?, ?, ?, ?)',
                (user_id, flight_id, plane_rating, crew_rating, comment))
    airplane_id = cur.execute(
        'SELECT Airplane_code FROM Flight WHERE Flight_code = ?', (flight_id,)).fetchone()[0]
    crew_on_flight = cur.execute(
        'SELECT User_code FROM Mans WHERE Flight_code = ?', (flight_id,)).fetchall()

    # update airplane and crew rating
    cur.execute(
        'UPDATE Airplane SET Review = (SELECT AVG(Airplane_score) FROM Reviews WHERE Airplane_code = ?)', (airplane_id,))
    cur.executemany(
        'UPDATE Employee SET Review = (SELECT AVG(Employee_score) FROM Reviews WHERE User_code = ?)', crew_on_flight)
    con.commit()

def get_airplane_score(flight_id):
    return cur.execute('SELECT Review FROM Airplane WHERE Airplane_code = (SELECT Airplane_code FROM Flight WHERE Flight_code = ?)', (flight_id,)).fetchone()[0]

def get_crew_score(flight_id):
    return cur.execute('SELECT AVG(Review) FROM Employee WHERE User_code IN (SELECT User_code FROM Mans WHERE Flight_code = ?)', (flight_id,)).fetchone()[0]

def get_last_flight(name):
    return cur.execute('SELECT Flight_code FROM Purchases WHERE User_code = ? ORDER BY Date DESC LIMIT 1', (hash(name),)).fetchone()[0]

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

print(flight_id := get_all_flights('New York', 'Miami', '2024-01-06')[0][0])
print(seats := get_available_seats(flight_id))
# create_flight('A001', 'A002', '2024-01-06 10:00:00', '2024-01-06 18:00:00', 'AP001')

con.close()