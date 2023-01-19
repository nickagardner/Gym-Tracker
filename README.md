# Gym Tracker

System to scrape data from RIT's gym website and store that data in a Firebase NoSQL database. This script is passed to Google Cloud Run by a Google Cloud Repository mirroring this repository (with entry point main.py). Following a pub/sub trigger, this file scrapes the website and stores the result in the database. It also performs future prediction using Facebook AI's Prophet (using the historical data collected by this app). Once the historical data and future prediction is stored in the database, my Plotly Dash Flask app (app.py), hosted on Heroku, renders a world-visible plot showing current and historical gym occupancy, as well as future prediction up to two weeks in the future.

[![weekly_scraper_screenshot](https://user-images.githubusercontent.com/12617237/200126249-5e125ac1-028f-4360-ba31-cff9d348d956.png)](https://www.nickgardner.us/gym_tracker.html)

# TODO

- Add capability to expand historical data tracking past the size of one document (which is approximately 850 days worth)
- Create monthly/yearly views
- Set ymin to zero and ymax to maximum recorded value. Will allow for more meaningful visual comparison between weeks and days if all plots are on the same y scale

