# GymTracker

Simple script to scrape data from RIT's gym website, store that data in a Firebase NoSQL database, then render it online with Plotly. This script is passed in to Google Cloud Run along with credentials files (not included here) for both Firebase and Plotly Chart Studio. Following a pub/sub trigger, this file scrapes the website, stores the result in the database, and renders a new world-visible plot with Plotly. 

# TODO

- Massively clean up plotting to allow for different modes of visibility (daily, weekly, monthly, yearly)
- Add explanation on README on how to generate relevant credentials files
- Incorporate simple machine learning element to predict future occupancy based on historical data and current trends
