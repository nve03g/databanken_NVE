-- SQL commands to create tables and prefill them with some data

-- Step 1: create tables
--   Note: for an existing sqlite database, you can generate the CREATE TABLE statements by asking for the database's schema.
--   You can do this from the command line as follows: `sqlite3 autocreated.db .schema`

CREATE TABLE IF NOT EXISTS "User" (
	"userID"	INTEGER NOT NULL UNIQUE,
	"username"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
	"email"	TEXT NOT NULL,
	PRIMARY KEY("userID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Customer" (
	"customerID"	INTEGER NOT NULL UNIQUE,
	"userID"	INTEGER NOT NULL,
	"firstName"	TEXT NOT NULL,
	"lastName"	TEXT NOT NULL,
	FOREIGN KEY("userID") REFERENCES "User"("userID"),
	PRIMARY KEY("customerID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Host" (
	"hostID"	INTEGER NOT NULL UNIQUE,
	"userID"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	FOREIGN KEY("userID") REFERENCES "User"("userID"),
	PRIMARY KEY("hostID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Location" (
	"locationID"	INTEGER NOT NULL UNIQUE,
	"hostID"	INTEGER NOT NULL,
	"address"	TEXT NOT NULL,
	"zipcode"	TEXT NOT NULL,
	"city"	TEXT NOT NULL,
	"country"	TEXT NOT NULL,
	FOREIGN KEY("hostID") REFERENCES "Host"("hostID"),
	PRIMARY KEY("locationID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "TicketTier" (
	"ticketTierID"	INTEGER NOT NULL UNIQUE,
	"eventID"	INTEGER NOT NULL,
	"description"	TEXT NOT NULL,
	"price"	REAL NOT NULL,
	"totalAmount"	INTEGER NOT NULL,
	"remainingAmount"	INTEGER NOT NULL,
	FOREIGN KEY("eventID") REFERENCES "Event"("eventID"),
	PRIMARY KEY("ticketTierID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "PurchaseItem" (
	"purchaseItemID"	INTEGER NOT NULL UNIQUE,
	"customerID"	INTEGER NOT NULL,
	"ticketTierID"	INTEGER NOT NULL,
	"quantity"	INTEGER NOT NULL,
	"purchaseDate"	TEXT,
	FOREIGN KEY("customerID") REFERENCES "Customer"("customerID"),
	FOREIGN KEY("ticketTierID") REFERENCES "TicketTier"("ticketTierID"),
	PRIMARY KEY("purchaseItemID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Ticket" (
	"ticketID"	INTEGER NOT NULL UNIQUE,
	"purchaseItemID"	INTEGER NOT NULL,
	FOREIGN KEY("purchaseItemID") REFERENCES "PurchaseItem"("purchaseItemID"),
	PRIMARY KEY("ticketID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Event" (
	"eventID"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"date"	TEXT,
	"time"	TEXT,
	"locationID"	INTEGER NOT NULL,
	"hostID"	INTEGER NOT NULL,
	"posterURL"	TEXT,
	"category"	TEXT,
	"onSale"	INTEGER NOT NULL,
	"artists"	TEXT,
	FOREIGN KEY("locationID") REFERENCES "Location"("locationID"),
	FOREIGN KEY("hostID") REFERENCES "Host"("hostID"),
	PRIMARY KEY("eventID" AUTOINCREMENT)
);

-- Step 2: prefill with some data

INSERT INTO User VALUES(1,'nellie','passwN','nellie@gmail.com');
INSERT INTO User VALUES(2,'livenation','passwLN','live@nation.com');
INSERT INTO User VALUES(3,'tomorrowland','passwTL','tomorrow@land.com');

INSERT INTO Host VALUES(1,2,'Live Nation');
INSERT INTO Host VALUES(2,3,'Tomorrowland');

INSERT INTO Customer VALUES(1,1,'Nellie','Van Eeckhaute');

INSERT INTO Location VALUES(1,1,'Haachtsesteenweg 23','3118','Rotselaar','België');
INSERT INTO Location VALUES(2,1,'Robert Orlentpromenade','8620','Nieuwpoort','België');
INSERT INTO Location VALUES(3,2,'Schommelei 1','2850','Boom','België');

INSERT INTO Event VALUES(1,'Rock Werchter 2024','2024/07/04-2024/07/07','12:00',1,1,'https://www.rockwerchter.be/en/','Rock',0,'Avril Lavigne, The Beaches, Benjamin Clementine, The Breeders, ...');
INSERT INTO Event VALUES(2,'Nieuwpoort Beach Festival 2025','2025/07/18-2025/07/20','12:00',2,1,'https://www.beachfestival.be','Pop, Rock',1,'Who Knows');
INSERT INTO Event VALUES(3,'Tomorrowland 2024','2024/07/19-2024/07/28','12:00',3,2,'https://www.tomorrowland.com/home/','Dance',0,'DJ Mars, Bosart, Dietro, ...');

INSERT INTO TicketTier VALUES(1,1,'dagticket',134,20000,0);
INSERT INTO TicketTier VALUES(2,1,'combiticket',309,10000,0);
INSERT INTO TicketTier VALUES(3,2,'weekend',156,5000,5000);
INSERT INTO TicketTier VALUES(4,2,'weekend VIP',300,200,200);
INSERT INTO TicketTier VALUES(5,3,'one-day pass',129,50000,0);
INSERT INTO TicketTier VALUES(6,3,'Full Madness pass',5460,500,0);

INSERT INTO PurchaseItem VALUES(1,1,3,4,NULL);
