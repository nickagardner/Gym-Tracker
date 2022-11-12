"""
File: constants.py
Author: Nicholas Gardner <nag6650@rit.edu>

Simple file to hold shared values relevant to both scraping and displaying.
"""

# URL of RIT gym website
RIT_GYM_URL = "https://recreation.rit.edu/facilityoccupancy"

# Timezone to localize results into (Eastern for RIT)
TIMEZONE = "US/Eastern"

# Name of dataframe columns representing counts for each facility
FACILITY_COUNT_NAMES = ["ll_count", "ul_count", "aq_count"]

# Formal name of each facility for plot legend purposes
FORMAT_VALUE_NAMES = ["Lower Level", "Upper Level", "Aquatic Center"]

# Colors for each facility trace for plotting
VALUE_COLORS = ['rgba(239, 85, 59, 1)', 'rgba(0, 204, 150, 1)', 'rgba(99, 110, 250, 1)']

# Formal names for prediction traces for plotting purposes
FORMAT_PRED_NAMES = ["Lower Level<br>Prediction", "Upper Level<br>Prediction", "Aquatic Center<br>Prediction"]

# Colors for each prediction facility trace for plotting
PRED_COLORS = ['rgba(239, 85, 59, 0.25)', 'rgba(0, 204, 150, 0.25)', 'rgba(99, 110, 250, 0.25)']
