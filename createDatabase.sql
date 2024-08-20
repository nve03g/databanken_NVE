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
