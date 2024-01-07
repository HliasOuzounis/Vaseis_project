CREATE TABLE IF NOT EXISTS "User" (
	"User_code" varchar,
	"Points" integer,
	"Name" string,
	"Referred_by " varchar,
	PRIMARY KEY ("User_code"),
	FOREIGN KEY ("Referred_by ") REFERENCES "User" ("User_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "Seat" (
	"Class" varchar,
	"Number" varchar,
	"Price" float,
	"Flight_code" varchar,
	PRIMARY KEY ("Number", "Flight_code"),
	FOREIGN KEY ("Flight_code") REFERENCES "Flight" ("Flight_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "Town" (
	"Town_code" varchar,
	"Name" varchar,
	PRIMARY KEY ("Town_code")
);

CREATE TABLE IF NOT EXISTS "Airport" (
	"Airport_code" varchar,
	"Name" varchar,
	"Town_code" varchar,
	PRIMARY KEY ("Airport_code"),
	FOREIGN KEY ("Town_code") REFERENCES "Town" ("Town_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "Flight" (
	"Flight_code" varchar,
	"Distance" float,
	"Airplane_code" varchar,
	"Departure_airport_code" varchar,
	"Arrival_airport_code" varchar,
	"Scheduled_departure_datetime" datetime,
	"Actual_departure_datetime" datetime,
	"Scheduled_arrival_datetime" datetime,
	"Actual_arrival_datetime" datetime,
	PRIMARY KEY ("Flight_code"),
	FOREIGN KEY ("Airplane_code") REFERENCES "Airplane" ("Airplane_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Departure_airport_code") REFERENCES "Airport" ("Airport_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Arrival_airport_code") REFERENCES "Airport" ("Airport_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "Airplane" (
	"Airplane_code" varchar,
	"Company" varchar,
	"Review" float,
	"First_class_seats" integer,
	"Business_class_seats" integer,
	"Economy_class_seats" integer,
	PRIMARY KEY ("Airplane_code")
);

CREATE TABLE IF NOT EXISTS "Employee" (
	"AFM" varchar,
	"Name" varchar,
	"Review" float,
	PRIMARY KEY ("AFM")
);

CREATE TABLE IF NOT EXISTS "Ticket" (
	"Ticket_code" varchar,
	"Price" float,
	"Discount" float,
	PRIMARY KEY ("Ticket_code")
);

CREATE TABLE IF NOT EXISTS "Pilot" (
	"License" varchar,
	"AFM" ,
	PRIMARY KEY ("AFM"),
	FOREIGN KEY ("AFM") REFERENCES "Employee" ("AFM")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "Flight_attendant" (
	"AFM" varchar,
	PRIMARY KEY ("AFM"),
	FOREIGN KEY ("AFM") REFERENCES "Employee" ("AFM")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "Purchases" (
	"Ticket_code" varchar,
	"User_code" varchar,
	"Bank_details" varchar,
	"Seat_number" varchar,
	"Date" datetime,
	PRIMARY KEY ("Ticket_code", "User_code", "Seat_number"),
	FOREIGN KEY ("Ticket_code") REFERENCES "Ticket" ("Ticket_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("User_code") REFERENCES "User" ("User_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Seat_number") REFERENCES "Seat" ("Number")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "Cancels" (
	"Ticket_code" varchar,
	"User_code" varchar,
	"Date" datetime,
	PRIMARY KEY ("Ticket_code", "User_code"),
	FOREIGN KEY ("Ticket_code") REFERENCES "Ticket" ("Ticket_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("User_code") REFERENCES "User" ("User_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "Reviews" (
	"User_code" varchar,
	"Flight_code" varchar,
	"Airplane_score" float,
	"Employee_score" float,
	"Comments" varchar,
	PRIMARY KEY ("User_code", "Flight_code"),
	FOREIGN KEY ("User_code") REFERENCES "User" ("User_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Flight_code") REFERENCES "Flight" ("Flight_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "Mans" (
	"AFM" varchar,
	"Flight_code" varchar,
	PRIMARY KEY ("AFM"),
	FOREIGN KEY ("AFM") REFERENCES "Employee" ("AFM")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Flight_code") REFERENCES "Flight" ("Flight_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

