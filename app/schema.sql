CREATE TABLE IF NOT EXISTS "User" (
	"Username" varchar,
	"Password" varchar,
	"Salt" varchar,
	"Points" integer,
	"Name" string,
	"Referred_by " varchar,
	PRIMARY KEY ("Username"),
	FOREIGN KEY ("Referred_by ") REFERENCES "User" ("Username")
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

CREATE TABLE IF NOT EXISTS "City" (
	"City_code" varchar,
	"Name" varchar,
	PRIMARY KEY ("City_code")
);

CREATE TABLE IF NOT EXISTS "Airport" (
	"Airport_code" varchar,
	"Name" varchar,
	"City_code" varchar,
	PRIMARY KEY ("Airport_code"),
	FOREIGN KEY ("City_code") REFERENCES "City" ("City_code")
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
	"Bank_details" varchar,
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
	"Username" varchar,
	"Seat_number" varchar,
	"Flight_code" varchar,
	"Date" datetime,
	PRIMARY KEY ("Ticket_code", "Username", "Seat_number", "Flight_code"),
	FOREIGN KEY ("Ticket_code") REFERENCES "Ticket" ("Ticket_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Username") REFERENCES "User" ("Username")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Seat_number") REFERENCES "Seat" ("Number")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
	FOREIGN KEY ("Flight_code") REFERENCES "Flight" ("Flight_code")
			ON UPDATE RESTRICT
			ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "Cancels" (
	"Ticket_code" varchar,
	"Username" varchar,
	"Date" datetime,
	PRIMARY KEY ("Ticket_code", "Username"),
	FOREIGN KEY ("Ticket_code") REFERENCES "Ticket" ("Ticket_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Username") REFERENCES "User" ("Username")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "Reviews" (
	"Username" varchar,
	"Flight_code" varchar,
	"Airplane_score" float,
	"Employee_score" float,
	"Comments" varchar,
	PRIMARY KEY ("Username", "Flight_code"),
	FOREIGN KEY ("Username") REFERENCES "User" ("Username")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Flight_code") REFERENCES "Flight" ("Flight_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "Mans" (
	"AFM" varchar,
	"Flight_code" varchar,
	PRIMARY KEY ("AFM", "Flight_code"),
	FOREIGN KEY ("AFM") REFERENCES "Employee" ("AFM")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
	FOREIGN KEY ("Flight_code") REFERENCES "Flight" ("Flight_code")
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
);

