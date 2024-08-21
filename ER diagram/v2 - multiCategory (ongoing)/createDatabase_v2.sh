# Shell script that creates the database 'autocreated_v2.db' from scratch, prefilled with some data
# Warning: any existing database with that name is removed first!

rm autocreated_v2.db
sqlite3 autocreated_v2.db < createDatabase_v2.sql
