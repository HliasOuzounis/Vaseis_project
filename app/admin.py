import database
import stats
import datetime

def print_help():
    print("Commands:")
    print("help - print this help message")
    print("exit - exit the program")
    print("create - create a new flight")
    print("stats - print statistics about the database")
    print()

def create():
    print("Enter the following information:")
    choice = input("Departure airport code or city: ")
    if database.get_airport(choice):
        departure_airport_code = choice
    else:
        airports = database.get_airports_from_city(choice)
        if len(airports) == 0:
            print("No airports or cities found.")
            print()
            return
        elif len(airports) == 1:
            departure_airport_code = airports[0]
        else:
            print("Multiple airports found:")
            for airport in airports:
                print(airport)
            departure_airport_code = input("Departure airport code: ")
    # arrival_airport_code = input("Arrival airport code: ")
    choice = input("Arrival airport code or city: ")
    if database.get_airport(choice):
        arrival_airport_code = choice
    else:
        airports = database.get_airports_from_city(choice)
        if len(airports) == 0:
            print("No airports or cities found.")
            print()
            return
        elif len(airports) == 1:
            arrival_airport_code = airports[0]
        else:
            print("Multiple airports found:")
            for airport in airports:
                print(airport)
            arrival_airport_code = input("Arrival airport code: ")
    scheduled_departure_datetime = input("Scheduled departure datetime (YYYY-MM-DD HH:MM:SS): ")
    scheduled_arrival_datetime = input("Scheduled arrival datetime (YYYY-MM-DD HH:MM:SS): ")
    available_airplanes = database.get_available_airplanes(scheduled_departure_datetime, scheduled_arrival_datetime)
    print("Some available airplanes:")
    for ind, plane in enumerate(available_airplanes[:15]):
        print(f"Airplane code: {plane[0]} - {plane[1]}")
    airplane_code = input("Airplane code: ")
    database.create_flight(
        departure_airport_code,
        arrival_airport_code,
        scheduled_departure_datetime,
        scheduled_arrival_datetime,
        airplane_code,
    )
    print("Flight created successfully.")
    print()


def stats_menu():
    stats_dict = {
        "Popular airports": stats.print_popular_airports,
        "Well reviewed airplanes": stats.print_well_reviewed_airplanes,
        "Well reviewed crew": stats.print_well_reviewed_crew,
        "Popular days": stats.print_popular_days,
        "Users with most purchases": stats.print_users_with_most_purchases,
        "Users with most referrals": stats.print_users_with_most_referrals,
        "Users with most points": stats.print_users_with_most_points,
        "Most cancelled flights": stats.print_most_cancelled_flights
    }
    
    print("Stats Menu:")
    for i, stat in enumerate(stats_dict.keys()):
        print(f"{i+1}. {stat}")
    
    while True:
        choice = input("Enter the number of the stat you want to view (or 'exit' to go back): ")
        
        if choice == "exit":
            break
        
        try:
            choice = int(choice)
            if 1 <= choice <= len(stats_dict):
                stat_chosen = list(stats_dict.keys())[choice-1]
                stats_dict[stat_chosen]()
                
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid choice. Please try again.")

def user_info():
    print("Enter the following information:")
    username = input("Username: ")
    user_info = database.get_user_info(username)
    if user_info:
        pass
    else:
        print("User not found.")
        return
    number_of_purchases = database.get_number_of_purchases(username)
    number_of_cancels = database.get_number_of_cancels(username)
    number_of_reviews = database.get_number_of_reviews(username)
    print("\nUser found!")
    print(f"Username: {user_info[0]}")
    print(f"Points: {user_info[1]}")
    print(f"Name: {user_info[2]}")
    print(f"Referred by: {user_info[3]}")
    print(f"Number of purchases: {number_of_purchases}")
    print(f"Number of cancels: {number_of_cancels}")
    print(f"Number of reviews: {number_of_reviews}")
    print()


def main():
    print("You are now connected to the database.")
    print("Type 'help' for a list of commands.")
    print("Type 'exit' to exit the program.")
    print()
    while True:
        command = input("> ")
        if command == "help":
            print_help()
        elif command == "exit":
            break
        elif command == "create":
            create()
        elif command == "stats":
            stats_menu()
        elif command == "user info":
            user_info()
        else:
            print("Invalid command. Type 'help' for a list of commands.")


if __name__ == "__main__":
    main()
