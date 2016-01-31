
program helps user in setting up a tournament by doing the following
	- store players standings in the database
	- generate matchups by using the swiss-pairing method
	

to run the program:
	1. put all files into one folder
	2. import the sql script (tournament.sql) - this will create the necessary tables and views that the file tournament.py will use
		a. using gitbash, type command below to open postgreSQL.
			psql
		b. once in postgreSQL, type command below to import script tournament.sql to create the tournament database, inside are tables and views .
			\i tournament.sql
	3. edit tournament.py and add the desired functions to run
		a. using a text editor, open tournament.py
		b. review the functions that can update the database
		c. at the end of tournament.py, use a new line to enter desired functions
			example:
				user would like to register a new player
				on line 242, enter "registerPlayer(name)"
				player'sname would then be added to the database
		d. save tournament.py with the functions user would want to use
	4. run the program
		a. on git bash, go to folder where tournament.py is located
			i. type the command below to change to the specified folder
				cd /folder/
		b. once in the proper folder type command below to run the program
			python tournament.py 
	

	
	
 