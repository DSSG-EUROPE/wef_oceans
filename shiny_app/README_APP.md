# An Illegal Fishing Vessel Risk Framework - Web app

This application shows the results of our *fishing/not-fishing* model and rank each vessel by possible risky behaviors on fishing (*i.e.,* EEZ presence, MPA presence, AIS signal blackout, etc.). The data shown in this app is only a anonymized subset of the total vessel data, no real MMSI or IMO is revealed. 

This web-app is created using RStudio's Shiny package. The `app.R` file contains both the user interaface and the server code, and the `www` folder contains the CSS layout and the images. Data connection to the PostgreSQL database is defined in `data/dummy_data.R`. This application is running in a Amazon EC2 instance using an Apache Server Framework. We used this server to create a secure connection to the app (under OpenSSL) and to create a controlled access with user and password. 

### Future work
* Create a `packrat` file to avoid conflicts between libraries
* Create a more secure SSL certificate (using [Let's Encript]). To do this we need to get a domain and not an AWS IP Address. 

[Let's Encript]:https://letsencrypt.org
