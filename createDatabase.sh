# Shell script that creates the database 'autocreated.db' from scratch, prefilled with some data
# Warning: any existing database with that name is removed first!

rm autocreated.db
sqlite3 autocreated.db < createDatabase.sql
