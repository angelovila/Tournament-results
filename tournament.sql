-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

drop database if exists tournament;

create database tournament;
\c tournament;

create table Players (playerID serial primary key,
					PlayerName varchar(50)
					);

create table Tournament (tournamentID serial primary key,
					TournamentName varchar(50)
					);
					
create table Matches (MatchID serial primary key,
					TournamentID int references Tournament (tournamentID),
					playerID int references Players (playerID),
					win_lose_draw char(4)
					);

--added view for listing all players and its corresponding number of wins and wins
create view vPlayerStandings AS
    select a.playerID,
			a.playername,
			coalesce(c.total_wins,0) as wins,
			coalesce(b.total_matches,0) as matches 
		from players as a 
		left join (select playerid,
					count(*) as total_matches
				from matches group by playerid) as b
				on a.playerid = b.playerid
				left join (select playerid,
						count(*) as total_wins
					from matches
					where win_lose_draw = 'win'
					group by playerid) as c 
					on a.playerid = c.playerid;
