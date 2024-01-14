import database
import login_handling
import json

def leave_review(username):
    flight_id = database.get_last_flight(username)
    if flight_id is None:
        print("You have not booked a flight yet")
        return
    print("Enter your review for your last flight")
    
    plane_rating = input("Plane rating: ")
    crew_rating = input("Crew rating: ")
    comment = input("Comment: ")
    database.leave_review(username, flight_id, plane_rating, crew_rating, comment)


def book_connecting_flight(username, departure_city, arrival_city, date):
    connecting_flights = database.get_connecting_flights(departure_city, arrival_city, date)
    if not connecting_flights:
        print("No connecting flights available")
        return
    print("Available connecting flights:")


    for index, flight_codes in enumerate(connecting_flights[:5]):
        flight_code1 = flight_codes[0]
        flight_code2 = flight_codes[1]
        flight1 = database.get_flight(flight_code1)
        flight2 = database.get_flight(flight_code2)
        intermediate_city = database.get_city_from_airport(flight1[4])
        crew_score1 = database.get_crew_score(flight_code1)
        crew_score1 = "-" if crew_score1 is None else f"{crew_score1:.2f}"
        plane_score1 = database.get_airplane_score(flight_code1)
        plane_score1 = "-" if plane_score1 is None else f"{plane_score1:.2f}"
        seats1 = database.get_available_seats(flight_code1)
        first_class_seats1 = len([seat for seat in seats1 if seat[0] == "First_Class"])
        business_class_seats1 = len([seat for seat in seats1 if seat[0] == "Business_Class"])
        economy_class_seats1 = len([seat for seat in seats1 if seat[0] == "Economy_Class"])

        print(f"Option {index}: (intermediate city: {intermediate_city}))")
        print(f"Flight Code: {flight_code1}")
        print(f"Crew Score: {crew_score1}")
        print(f"Plane Score: {plane_score1}")
        print("Number of Seats:")
        print(f"First Class: {first_class_seats1}")
        print(f"Business Class: {business_class_seats1}")
        print(f"Economy Class: {economy_class_seats1}")
        print()

        crew_score2 = database.get_crew_score(flight_code2)
        crew_score2 = "-" if crew_score2 is None else f"{crew_score2:.2f}"
        plane_score2 = database.get_airplane_score(flight_code2)
        plane_score2 = "-" if plane_score2 is None else f"{plane_score2:.2f}"
        seats2 = database.get_available_seats(flight_code2)
        first_class_seats2 = len([seat for seat in seats2 if seat[0] == "First_Class"])
        business_class_seats2 = len([seat for seat in seats2 if seat[0] == "Business_Class"])
        economy_class_seats2 = len([seat for seat in seats2 if seat[0] == "Economy_Class"])

        print(f"Flight Code: {flight_code2}")
        print(f"Crew Score: {crew_score2}")
        print(f"Plane Score: {plane_score2}")
        print("Number of Seats:")
        print(f"First Class: {first_class_seats2}")
        print(f"Business Class: {business_class_seats2}")
        print(f"Economy Class: {economy_class_seats2}")
        print()
        print("-------")
        print()

        
    print("Enter the flight you want to book")
    flight = input("Flight: ")
    if not flight.isdigit() or int(flight) >= len(connecting_flights):
        print("Invalid flight")
        return
    flight_code1, flight_code2 = connecting_flights[int(flight)]
    flight1 = database.get_flight(flight_code1)
    flight2 = database.get_flight(flight_code2)
    print("Enter the class you want to book")
    print("1. First Class")
    print("2. Business Class")
    print("3. Economy Class")
    seat_class = input("Class: ")
    seat_classes = {"1": "First_Class", "2": "Business_Class", "3": "Economy_Class"}
    if seat_class not in seat_classes:
        print("Invalid class")
        return
    seat_class = seat_classes[seat_class]
    seats1 = database.get_available_seats(flight_code1)
    seats1 = [seat for seat in seats1 if seat[0] == seat_class]
    seats2 = database.get_available_seats(flight_code2)
    seats2 = [seat for seat in seats2 if seat[0] == seat_class]
    if len(seats1) == 0 or len(seats2) == 0:
        print("No seats available")
        return

    print(f"How many seats would you like to book? Must be less than {min(len(seats1), len(seats2))}.")
    num_seats = input("Number of seats: ")
    if not num_seats.isdigit() or int(num_seats) > len(seats1) or int(num_seats) > len(seats2):
        print("Invalid number of seats")
        return
    num_seats = int(num_seats)
    seats1 = seats1[:num_seats]
    seats2 = seats2[:num_seats]
    price1, points1 =database.buy_ticket(username, bank_details, list((seat[3], seat[1]) for seat in seats1), date)
    price2 , points2 = database.buy_ticket(username, bank_details, list((seat[3], seat[1]) for seat in seats2), date)
    print("Purchase successful!")
    print(f"Total price: {price1 + price2}")
    print(f"Total points awarded: {points1 + points2}")
    return


def book_flight(username):

    print("Enter your bank details")
    bank_details = input("Bank details: ")
    
    print("Enter the date you want to fly")
    date = input("Date: ")

    print("enter the city of departure")
    departure_city = input("City of Departure: ")
    if not database.check_for_city(departure_city):
        print("City does not exist")
        return

    print("enter the city of arrival")
    arrival_city = input("City of Arrival: ")
    if not database.check_for_city(arrival_city):
        print("City does not exist")
        return


    available_flights = database.get_all_flights(departure_city, arrival_city, date)
    if not available_flights:
        print("No flights available, checking for connecting flights")
        print()
        book_connecting_flight(username, departure_city, arrival_city, date)
        return
    
    print("Available flights:")
    for index, flight in enumerate(available_flights):
        crew_score = database.get_crew_score(flight[0])
        crew_score = "-" if crew_score is None else f"{crew_score:.2f}"
        plane_score = database.get_airplane_score(flight[0])
        plane_score = "-" if plane_score is None else f"{plane_score:.2f}"
        seats = database.get_available_seats(flight[0])
        first_class_seats = len([seat for seat in seats if seat[0] == "First_Class"])
        business_class_seats = len([seat for seat in seats if seat[0] == "Business_Class"])
        economy_class_seats = len([seat for seat in seats if seat[0] == "Economy_Class"])

        seats_info = f"{first_class_seats} first class, {business_class_seats} business, {economy_class_seats} economy class"


        print(f"{index}. Available seats: {seats_info}, Crew score: {crew_score}, Plane score: {plane_score}")
    
    
    print("Enter the flight you want to book")
    flight = input("Flight: ")
    if not flight.isdigit() or int(flight) >= len(available_flights):
        print("Invalid flight")
        return
    flight = available_flights[int(flight)]
    flight_code = flight[0]

    print("Enter the class you want to book")
    print("1. First Class")
    print("2. Business Class")
    print("3. Economy Class")
    seat_class = input("Class: ")
    seat_classes = {"1": "First_Class", "2": "Business_Class", "3": "Economy_Class"}
    if seat_class not in seat_classes:
        print("Invalid class")
        return
    seat_class = seat_classes[seat_class]
    seats = database.get_available_seats(flight_code)
    seats = [seat for seat in seats if seat[0] == seat_class]
    if len(seats) == 0:
        print("No seats available")
        return
    print(f"How many seats would you like to book? Must be less than {len(seats)}.")
    num_seats = input("Number of seats: ")
    if not num_seats.isdigit() or int(num_seats) > len(seats):
        print("Invalid number of seats")
        return
    num_seats = int(num_seats)
    seats = seats[:num_seats]

    price, points = database.buy_ticket(username, flight_code, seat_class, (seats[3], seats[1]), bank_details)

    print("Purchase successful!")
    print(f"Price: {price}")
    print(f"Points awarded: {points}")
    return 



def main():
    username = None

    print("Welcome to the app, select an option:")
    print("1. Login")
    print("2. Register")
    while True:
        choice = input("Enter your choice: ")
        if choice == "1":
            username = login_handling.login()
            break
        elif choice == "2":
            username = login_handling.register()
            break
        else:
            print("Invalid choice")

    print(f"\nYou have {int(database.get_user_points(username)[0])} points!")
    print("Select an option:")
    print("1. Book a flight")
    print("2. Leave a review for your last flight")
    print("3. Exit")
    while True:
        choice = input("Enter your choice: ")
        if choice == "1":
            book_flight(username)
            break
        elif choice == "2":
            leave_review(username)
            break

        elif choice == "3":
            break
        else:
            print("Invalid choice")


    



    
if __name__ == "__main__":
    # print(database.get_airplane_score(1))
    main()
    # Tokyo Lima 2024-01-19
    # book_connecting_flight("tttt","São Paulo", "Lisbon", "2024-01-09")
    # cities = database.get_all_cities()
    # for city1 in cities:
    #     city1 = city1[0]
    #     for city2 in cities:
    #         city2 = city2[0]
    #         if city1 == city2:
    #             continue
    #         if database.get_all_flights(city1, city2, "2024-01-19"):
    #             continue
    #         if not database.get_connecting_flights(city1, city2, "2024-01-19"):
    #             continue
    #         if not database.get_airplane_score(database.get_connecting_flights(city1, city2, "2024-01-19")[0][0]):
    #             continue
    #         print(city1, city2, "2024-01-19")
    #         print("-------")
    #         print()

    
