from flask import Flask, send_file, request
import os
import datetime
import urllib.request
import json

app = Flask(__name__)

# Serve a default page. This function is not required. Serving up a spy.gif for the homepage.
#@app.route('/')
#def my_function():
#    spy_meme = "/app/images/spy.gif"
#    return send_file(spy_meme, mimetype="image/gif")

@app.route('/image/<source>/<identifier>')
def my_spy_pixel(source, identifier):
    # File path and name for 1 x 1 pixel. Must be an absolute path to pixel.
    filename = "/app/images/pixel.png"

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
    get_ip = request.headers.get('X-Real-IP', request.headers.get('X-Forwarded-For', request.remote_addr))

    # Lookup Geolocation of IP Address.
    with urllib.request.urlopen("https://geolocation-db.com/jsonp/"+ get_ip) as url:
        data = url.read().decode()
        data = data.split("(")[1].strip(")")

    # create log entry
    log_entry = {
            "event": "Accessed",
            "source": source,
            "identifier": identifier,
            "timestamp": timestamp,
            "user_agent": user_agent,
            "referrer": referrer,
            "accept_language": accept_language,
            "cookies": cookies,
            "secure_connection": secure_connection,
            "hostname": hostname,
            "ip_raw": get_ip,
            "ip_info": data
            }

    # define the names for the log file
    log_source_directory_name = f'/app/logs/sources/_{source}_'
    log_file_name_source = f'spy_pixel_logs.log'
    log_file_name_all = '/app/logs/spy_pixel_logs_all.log'

    # create log files and its directories if they do not exist
    os.makedirs(log_source_directory_name, exist_ok=True)
    if not os.path.exists(log_file_name_all):
        open(log_file_name_all, 'a').close()
    if not os.path.exists(log_file_name_source):
        open(log_file_name_source, 'a').close()
    

    # Write log to the log files
    # source specific log file
    with open(f'{log_source_directory_name}/{log_file_name_source}', 'a') as f:
        f.write(json.dumps(log_entry)+ '\n')
    # file for all logs
    with open(log_file_name_all, 'a') as f:
        f.write(json.dumps(log_entry)+ '\n')

    # Serve a transparent pixel image
    return send_file(filename, mimetype="image/png")


if __name__ == '__main__':
    app.run()
