DROP_TABLE_ARTISTS_SQL = ("""DROP table IF EXISTS public.artists;""")

DROP_TABLE_SONGPLAYS_SQL = ("""DROP table IF EXISTS public.songplays;""")

DROP_TABLE_SONGS_SQL = ("""DROP table IF EXISTS public.songs;""")

DROP_STAGING_EVENTS_SQL = ("""DROP table IF EXISTS public.staging_events;""")

DROP_STAGING_SONGS_SQL = ("""DROP table IF EXISTS public.staging_songs;""")

DROP_TABLE_TIME_SQL = ("""DROP table IF EXISTS public."time";""")

DROP_TABLE_USERS_SQL = ("""DROP table IF EXISTS public.users;""")

CREATE_TABLE_ARTISTS_SQL = ("""CREATE TABLE public.artists (
	artistid varchar(256) NOT NULL,
	name varchar(512),
	location varchar(512),
	lattitude numeric(18,0),
	longitude numeric(18,0)
);""")


CREATE_TABLE_SONGPLAYS_SQL = ("""CREATE TABLE public.songplays (
	playid varchar(32) NOT NULL,
	start_time timestamp NOT NULL,
	userid int4 NOT NULL,
	"level" varchar(256),
	songid varchar(256),
	artistid varchar(256),
	sessionid int4,
	location varchar(256),
	user_agent varchar(256),
	CONSTRAINT songplays_pkey PRIMARY KEY (playid)
);""")


CREATE_TABLE_SONGS_SQL = ("""CREATE TABLE public.songs (
	songid varchar(256) NOT NULL,
	title varchar(512),
	artistid varchar(256),
	"year" int4,
	duration numeric(18,0),
	CONSTRAINT songs_pkey PRIMARY KEY (songid)
);""")


CREATE_STAGING_EVENTS_SQL = ("""CREATE TABLE public.staging_events (
	artist varchar(256),
	auth varchar(256),
	firstname varchar(256),
	gender varchar(256),
	iteminsession int4,
	lastname varchar(256),
	length numeric(18,0),
	"level" varchar(256),
	location varchar(256),
	"method" varchar(256),
	page varchar(256),
	registration numeric(18,0),
	sessionid int4,
	song varchar(256),
	status int4,
	ts int8,
	useragent varchar(256),
	userid int4
);""")

CREATE_STAGING_SONGS_SQL = ("""CREATE TABLE public.staging_songs (
	song_id varchar(256),
    num_songs int4,
    title varchar(512),
	artist_name varchar(512),
    artist_latitude numeric(18,0),
    "year" int4,
	duration numeric(18,0),
    artist_id varchar(256),
	artist_longitude numeric(18,0),
	artist_location varchar(512)
);""")


CREATE_TABLE_TIME_SQL = ("""CREATE TABLE public."time" (
	start_time timestamp NOT NULL,
	"hour" int4,
	"day" int4,
	week int4,
	"month" varchar(256),
	"year" int4,
	weekday varchar(256),
	CONSTRAINT time_pkey PRIMARY KEY (start_time)
) ;""")


CREATE_TABLE_USERS_SQL = ("""CREATE TABLE public.users (
	userid int4 NOT NULL,
	first_name varchar(256),
	last_name varchar(256),
	gender varchar(256),
	"level" varchar(256),
	CONSTRAINT users_pkey PRIMARY KEY (userid)
);""")

create_table_queries = [CREATE_STAGING_EVENTS_SQL, 
                        CREATE_STAGING_SONGS_SQL, 
                        CREATE_TABLE_SONGPLAYS_SQL, 
                        CREATE_TABLE_ARTISTS_SQL, 
                        CREATE_TABLE_SONGS_SQL, 
                        CREATE_TABLE_USERS_SQL, 
                        CREATE_TABLE_TIME_SQL]

drop_table_queries = [DROP_STAGING_EVENTS_SQL,
                      DROP_STAGING_SONGS_SQL,
                      DROP_TABLE_SONGPLAYS_SQL,
                      DROP_TABLE_ARTISTS_SQL,
                      DROP_TABLE_SONGS_SQL,
                      DROP_TABLE_USERS_SQL,
                      DROP_TABLE_TIME_SQL
					  ]