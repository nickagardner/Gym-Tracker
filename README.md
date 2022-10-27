# Gym Tracker

Simple script to scrape data from RIT's gym website and store that data in a Firebase NoSQL database. This script is passed in to Google Cloud Run along with credentials files (not included here) for Firebase. Following a pub/sub trigger, this file scrapes the website and stores the result in the database. This database is used by my related repository, https://github.com/nickagardner/Gym-Tracker-Renderer, to render a world-visible plot showing current and historical gym occupancy.

[![scraper_screenshot](https://user-images.githubusercontent.com/12617237/198174338-3f5d4ce9-1c23-40d5-a2bc-0656ff8de8b4.png)](https://www.nickgardner.us/gym_tracker.html)

# TODO

- Incorporate simple machine learning element to predict future occupancy based on historical data and current trends. Waiting for a sufficiently large dataset for this.
