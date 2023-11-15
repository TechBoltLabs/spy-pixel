[![Build Status](https://drone.huzi.rocks/api/badges/TechBoltLabs/spy-pixel/status.svg)](https://drone.huzi.rocks/TechBoltLabs/spy-pixel)

# 🔍 Email Spy Pixel
*A basic tracking pixel to track email and website opens.* -- *Dockerized version of [collinsmc23's spy-pixel](https://github.com/collinsmc23/spy-pixel)*

## Overview
Spy pixels, also commonly referred to as web beacons, are small artifacts implemented in applications to gather user information, which could include the User-Agent string, IP address, and if an email is opened etc. A basic method to collect this information is through the use of a 1x1 pixel with an embedded URL through a transparent PNG, GIF, JPG.

This project uses Python Flask to serve a static web page with a `pixel.png` included in the `app/images/` directory. When a user opens an email or website with the embedded spy pixel, some information is *(example below)* logged to the `spy_pixel_logs_all.log` *(all logs)* and `sources/{source}/spy_pixel_log.log` *(logs per source)* files.

There are two variables, which are set through the url path of the pixel:
 - source (like website, mail, ...)
 - identifier (like website_a, mail_body_version_b, ...)

```json
{
  "event": "Accessed",
  "source": "website",
  "identifier": "<some_identifier>",
  "timestamp": "<some_timestamp>",
  "user_agent": "<user_agent_string>",
  "referrer": "<referrer>",
  "accept_language": "de-DE,de;q=0.7",
  "cookies": {},
  "secure_connection": false,
  "hostname": "<your_hostname>",
  "ip_raw": "<ip_of_requestor>",
  "ip_info": "<information_about_ip_address>"
}
```

## Deploy

To deploy this application, use either the Dockerfile to build a docker image on your own or use the [image from docker hub](https://hub.docker.com/r/techbolt/spy-pixel).
You can then bring the container up using the compose.yml file

If you want to use it in production mode, you should have a server, which is remotely available (such as a VPS).
To use it a with domain, you can use the example compose file with traefik configuration.


**Spy Away (For Learning Purposes only)**

![Spy Dwight](https://github.com/collinsmc23/spy-pixel/blob/main/images/spy.gif )


