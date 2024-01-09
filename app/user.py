import database
import login_handling


def leave_review(username):
    print("Enter your review for your last flight")
    flight_id = database.get_last_flight(username)
    user_code = database.get_user_code(username)
    plane_rating = input("Plane rating: ")
    crew_rating = input("Crew rating: ")
    comment = input("Comment: ")
    database.leave_review(user_code, flight_id, plane_rating, crew_rating, comment)

def book_flight(username):
    user_code = database.get_user_code(username)

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


    available_flights = database.get_available_flights(departure_city, arrival_city, date)
    if not available_flights:
        print("No flights available")
        return
    
    print("Available flights:")
    for index, flight in enumerate(available_flights):
        crew_score = database.get_crew_score(flight[0])
        plane_score = database.get_airplane_score(flight[0])
        seats = database.get_available_seats(flight[0])
        first_class_seats = len([seat for seat in seats if seat[0] == "First Class"])
        business_class_seats = len([seat for seat in seats if seat[0] == "Business Class"])
        economy_class_seats = len([seat for seat in seats if seat[0] == "Economy Class"])
        seats_info = f"{first_class_seats} first clas, {business_class_seats} business, {economy_class_seats} economy class"


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
    seat_classes = {"1": "First Class", "2": "Business Class", "3": "Economy Class"}
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
    database.buy_ticket(user_code, bank_details, seats, date)

    print("Purchase successful!")
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

    print(f"\nYou have {database.get_user_points(username)} points!")
    print("Select an option:")
    print("1. Book a flight")
    print("2. Leave a review for your last flight")
    print("3. Exit")
    while True:
        choice = input("Enter your choice: ")
        if choice == "1":
            # database.book_flight(username)
            break
        elif choice == "2":
            database.leave_review(username)
            break
        elif choice == "3":
            break
        else:
            print("Invalid choice")


    



    
if __name__ == "__main__":
    main()