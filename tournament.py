#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#
import psycopg2
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("delete from Matches;")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("delete from Players;")
    DB.commit()
    DB.close()


def deleteTournament():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("delete from Tournament;")
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()
    c.execute("select count(*) from Players;")
    count_value = c.fetchall()
    DB.close()
    return count_value[0][len(count_value[0])-2]
    # constant "-2" is because of character "L" and
    # how len is counting starting from 1.
    # note: fetchall for count aggregate returns with a value and an L
    # ex: 2 entries on table, count(*) returns (2L)


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    query = "INSERT INTO Players (PlayerName) VALUES (%s);"
    c.execute(query, (bleach.clean(name),))
    DB.commit()
    DB.close()


def registerTournament(name):
    """Adds a tournament on the tournament table

    This will allow the entry of multiple tournaments
	without needing to clearing matches

    Args:
      name: name of the tournament
    """
    DB = connect()
    c = DB.cursor()
    query = "INSERT INTO Tournament (TournamentName) VALUES (%s);"
    c.execute(query, (bleach.clean(name),))
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.
    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()
    query = "SELECT * FROM vPlayerStandings ORDER BY wins DESC;"
    c.execute(query)
    standings = [(str(row[0]),
                 str(row[1]),
                 int(row[2]),
                 int(row[3])) for row in c.fetchall()]
    DB.close()
    return standings


def tournamentlist():
    """Returns a list of all tournaments registered

    Returns:
    a list of tuples for every entry in the tournament table
    (id, tournamentname)
    """
    DB = connect()
    c = DB.cursor()
    query = "SELECT * FROM Tournament;"
    c.execute(query)
    tournaments = [(str(row[0]), str(row[1])) for row in c.fetchall()]
    DB.close()
    return tournaments


def reportMatch(tournamentID, winner, loser, draw=0):
    """Records the outcome of a single match between two players.

    Args:
      tournamentID: id number of tournament
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
          enter 'bye' if player gets a win by not having an opponent
      draw: if value is 1, match is a draw. players entered in the
          argument as winner or loser will be recorded as "draw"
    """
    DB = connect()
    c = DB.cursor()
    sql_draw = """
        INSERT INTO Matches (tournamentID,
                             playerID,
                             win_lose_draw)
        VALUES (%s, %s, 'draw');
        """
    sql_win = """
        INSERT INTO Matches (tournamentID,
                             playerID,
                             win_lose_draw)
        VALUES (%s, %s, 'win');
        """
    sql_lose = """
        INSERT INTO Matches (tournamentID,
                             playerID,
                             win_lose_draw)
        VALUES (%s, %s, 'lose');
        """
    if draw:
        # if draw is declared as 1, both players entered
        # (winner,loser) will get a draw
        c.execute(sql_draw,
                  (bleach.clean(tournamentID),
                   bleach.clean(winner)))
        c.execute(sql_draw,
                  (bleach.clean(tournamentID),
                   bleach.clean(loser)))
    elif loser == 'bye':
        # if a player doesn't have an opponent,
        # enter "bye" in the loser argument
        c.execute(sql_win,
                  (bleach.clean(tournamentID),
                   bleach.clean(winner)))
    else:
        # if a match is not a draw or not bye,
        # winner and loser will be recorded accordingly
        c.execute(sql_win,
                  (bleach.clean(tournamentID),
                   bleach.clean(winner)))
        c.execute(sql_lose,
                  (bleach.clean(tournamentID),
                   bleach.clean(loser)))
    DB.commit()
    DB.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    DB = connect()
    c = DB.cursor()
    query = """
        select playerid,
              playername,
              wins,
              matches
        from vPlayerStandings
        order by wins DESC;
        """
    c.execute(query)
    standings = [(str(row[0]), str(row[1])) for row in c.fetchall()]
    matches = []
    matchup = []
    # for loop runs through every bit of single player's
    # information (playerid, playername) respectively one by one
    for player in standings:
        for bit in player:
            matchup.append(bit)
            # it then append it into a list
            if len(matchup) >= 4:
                # once there are 2 players on the list (4 bits of
                # information (playerid1, playername1, playerid2, playername2))
                matches.append(tuple(matchup))
                # it makes the list into a tuple then add it to
                # the matches variable, it then repeats the loop
                matchup = []
    if len(matchup) == 2:
        # if the number of players is odd, one player will not have any
        # opponent (only 2 "bits" of information
        # (playerid1,playername1)), but it should have 4
        matchup.append('bye')
        matchup.append('bye')
        # adding a "dummy" player to follow the format and have 4 "bits" of
        # information per tuple (playerid1, playernam1, 'bye', 'bye')
        matches.append(tuple(matchup))
        matchup = []
    return matches
