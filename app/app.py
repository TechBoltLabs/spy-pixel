# app.py - version: v0.7.2

import datetime
import json
import os
import urllib.request

import mysql.connector
from flask import Flask, send_file, request

# define some global variables for later use
## logging destination
LOG_TO_DB = False
## db related variables
db = None
db_host = None
db_user = None
db_password = None
db_name = None
## File path and name for 1 x 1 pixel. Must be an absolute path to pixel.
pixel_filepath = "/app/images/pixel.png"

## variables for logging to json file
### define the names for the log file
log_source_directory_name = None
log_file_name_source = None
log_file_name_all = None



# read variables from the environment
def read_env_vars():
    # define variables as reference to their global representatives
    global db_host, db_user, db_password, db_name, LOG_TO_DB
    # Read environment variables
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    # set the logging to db based on the presence of all environment variables for the database
    if all([db_host, db_user, db_password, db_name]) and os.getenv("NO_DB_LOGGING") != 'True':
        LOG_TO_DB = True


# set up the db connection
def init_db():
    # define variable as reference to its global representative
    global db
    # assertions for Null-checking
    assert db_host is not None, "variable 'db_host' is not initialized"
    assert db_user is not None, "variable 'db_user' is not initialized"
    assert db_password is not None, "variable 'db_password' is not initialized"
    assert db_name is not None, "variable 'db_name' is not initialized"

    try:
        # Database connection
        db = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        db.connect()
        print(
            f"Connected to database '{db_name}' on host '{db_host}' as user '{db_user}'"
        )
    # catch any uninitialized variable
    except AssertionError as err:
        print(f"Failed to initialize database: {err}")
    # catch any problems with the db connection
    except mysql.connector.Error as err:
        print(f"Failed to initialize database: {err}")


# prepare the db for its use in production
def create_db_assets():
    # use global variables
    global db
    # ensure variables are not None
    assert db is not None, "variable 'db' is not initialized"
    try:
        cursor = db.cursor()
        print("Creating table 'requests' ...")
        cursor.execute("""create table requests
        (
            id                  int primary key auto_increment,
            time                datetime,
            event               varchar(255),
            source              varchar(255),
            identifier          varchar(255),
            user_agent          varchar(1024),
            referrer            varchar(1024),
            accept_language     varchar(255),
            hostname            varchar(255),
            secure_connection   varchar(255),
            ip_address          varchar(255),
            id_based_info       varchar(1024),
            cookies             varchar(16348)
        ) engine = InnoDB
          default charset = utf8;""")

        print("Table 'requests' created")
        # close the connection to the db
        cursor.close()

    # catch any uninitialized variable
    except AssertionError as err:
        print(f"Failed to create table: {err}")
    # catch any problems with the db connection
    except mysql.connector.Error as err:
        print(f"Failed to create table: {err}")


# check, if all necessary tables are present in the db
def check_table_presence():
    # use global variables
    global db
    # ensure variables are not None
    assert db is not None, "variable 'db' is not initialized"
    try:
        cursor = db.cursor()
        print("checking db ...")
        # check the existence of table 'requests'
        cursor.execute("SHOW TABLES like 'requests';")

        # run the query
        result = cursor.fetchone()

        # act based on the existence of 'requests'
        if result:
            print("Table 'requests' exists")
        else:
            print("Table 'requests' does not exist")
            create_db_assets()

        # close the connection to the db
        cursor.close()

    # catch any uninitialized variable
    except AssertionError as err:
        print(f"Failed to check table: {err}")
    # catch any problems with the db connection
    except mysql.connector.Error as err:
        print(f"Failed to check table: {err}")


# initialize the program (primarily for db usage)
def initialize():
    read_env_vars()
    init_db()
    check_table_presence()


## ----------------- ##
##   helper methods  ##
## ----------------- ##

### ---------------- ###
### database logging ###
### ---------------- ###

def add_db_log_entry(event, source, identifier, timestamp, user_agent, referrer, accept_language, cookies,
                     secure_connection, hostname, ip_raw, ip_info):
    # use global variable(s)
    global db
    # db shall not be None
    assert db is not None, "variable 'db' is not initialized"

    try:
        # creating the prepared statement for querying the db
        sql_query = """insert into requests(time, event, source, identifier, user_agent, referrer, accept_language, hostname, secure_connection, ip_address, id_based_info, cookies)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        # defining, which data shall be passed to the query
        query_data = (timestamp, event, source, identifier, user_agent, referrer, accept_language, hostname, secure_connection, ip_raw, ip_info, cookies)
        # open a session for the execution of a prepared statement
        cursor = db.cursor(prepared=True)
        # just a console message
        print("Adding log entry to db ...")
        # execute the prepared statement
        cursor.execute(sql_query, query_data)
        # commit the changes so the log entry actually persists
        db.commit()
        # just a console message
        print("Log entry added to db")

        # close the db session
        cursor.close()

    # error handling
    except AssertionError as err:
        print(f"Failed to add log entry to db - variable not set: {err}")
    except mysql.connector.Error as err:
        print(f"Failed to add log entry to db due to db connection error: {err}")


### ---------------- ###
###   json logging   ###
### ---------------- ###

# create log entry in json format
def create_json_log_entry(event, source, identifier, timestamp, user_agent, referrer, accept_language, cookies,
                          secure_connection, hostname, ip_raw, ip_info):
    log_entry_json = {
        "event": event,
        "source": source,
        "identifier": identifier,
        "timestamp": timestamp,
        "user_agent": user_agent,
        "referrer": referrer,
        "accept_language": accept_language,
        "cookies": cookies,
        "secure_connection": secure_connection,
        "hostname": hostname,
        "ip_raw": ip_raw,
        "ip_info": ip_info
    }
    return log_entry_json


def ensure_dir_structure(source):
    # use the global variables
    global log_source_directory_name, log_file_name_source, log_file_name_all

    ### set the names for the log files and directories
    log_source_directory_name = f'/app/logs/sources/_{source}_'
    log_file_name_source = f'{log_source_directory_name}/spy_pixel_logs.log'
    log_file_name_all = '/app/logs/spy_pixel_logs_all.log'

    # create log files and its directories if they do not exist
    os.makedirs(log_source_directory_name, exist_ok=True)
    if not os.path.exists(log_file_name_all):
        open(log_file_name_all, 'a').close()
    if not os.path.exists(log_file_name_source):
        open(log_file_name_source, 'a').close()


def write_json_logs(source, log_entry_json):
    # use global variables
    global log_file_name_source, log_file_name_all

    # check, if directory and files are present (and create them if not)
    ensure_dir_structure(source)

    # ensure variables are not None
    assert log_file_name_all is not None, "variable 'log_file_name_all' is not initialized"
    assert log_file_name_source is not None, "variable 'log_file_name_source' is not initialized"
    # ensure variables have the correct format
    assert isinstance(log_file_name_all, (str, bytes, os.PathLike))
    assert isinstance(log_file_name_source, (str, bytes, os.PathLike))

    try:
        # Write log to the log files
        # just a logging message
        print(f"Writing log entry to file '{log_file_name_source}' and '{log_file_name_all}' ...")
        # source specific log file
        with open(log_file_name_source, 'a') as f:
            f.write(json.dumps(log_entry_json) + '\n')
        # file for all logs
        with open(log_file_name_all, 'a') as f:
            f.write(json.dumps(log_entry_json) + '\n')
    except AssertionError as err:
        print(f"Failed to write log to file - variable not set or invalid path (format): {err}")

## ----------------
## flask app
## ----------------
app = Flask(__name__)


# Serve a default page. This function is not required. Serving up a spy.gif for the homepage.
# @app.route('/')
# def my_function():
#     spy_meme = "/app/images/spy.gif"
#     return send_file(spy_meme, mimetype="image/gif")


@app.route('/image/<source>/<identifier>')
def my_spy_pixel(source, identifier):
    global pixel_filepath

    # Get some information about the user('s hard-/software)
    user_agent = request.headers.get('User-Agent')
    referrer = request.headers.get('Referer')
    accept_language = request.headers.get('Accept-Language')
    cookies = request.cookies
    secure_connection = request.is_secure
    hostname = request.host

    # Get the current time of request and format time into readable format.
    current_time = datetime.datetime.now()
    timestamp = datetime.datetime.strftime(current_time, "%Y-%m-%d %H:%M:%S")

    # Log the IP address of requester.
    requester_ip = request.headers.get('X-Real-IP', request.headers.get('X-Forwarded-For', request.remote_addr))

    # Lookup Geolocation of IP Address.
    with urllib.request.urlopen("https://geolocation-db.com/jsonp/" + requester_ip) as url:
        data = url.read().decode()
        data = data.split("(")[1].strip(")")

    if not LOG_TO_DB:
        # create log entry
        log_entry_json = create_json_log_entry("Accessed", source, identifier, timestamp, user_agent, referrer,
                                               accept_language, cookies, secure_connection, hostname, requester_ip, data)


        # writes the json_log_entry to two separate files (one for all and one for the source)
        write_json_logs(source, log_entry_json)
    else:
        add_db_log_entry("Accessed", source, identifier, timestamp, user_agent, referrer,
                         accept_language, cookies, secure_connection, hostname, requester_ip, data)

    # Serve a transparent pixel image
    return send_file(pixel_filepath, mimetype="image/png")


if __name__ == '__main__':
    initialize()
    app.run()
