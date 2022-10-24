# Gym Tracker

Simple script to scrape data from RIT's gym website, store that data in a Firebase NoSQL database, then render it online with Plotly. This script is passed in to Google Cloud Run along with credentials files (not included here) for both Firebase and Plotly Chart Studio. Following a pub/sub trigger, this file scrapes the website, stores the result in the database, and renders a new world-visible plot with Plotly. 

Link to plot: https://plotly.com/~nickgardner7777/20/

If you are interested in implementing something similar, here is a brief explanation of the credentials files:
### Firebase
After creating a Firestore database, go to project, then navigate to your project and then click on *Project settings*. From here, navigate to *Service accounts* and then to *Generate a new private key*. Put this key in the root level of your project directory. It should look something like this (sensitive information replaced here):
```
{
  "type": "service_account",
  "project_id": "example_project_id",
  "private_key_id": "example_key_id",
  "private_key": "-----BEGIN PRIVATE KEY-----PRIVATE KEY STRING HERE-----END PRIVATE KEY-----\n",
  "client_email": "example_firebase_email",
  "client_id": "example_client_id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "client_auth_url"
}
```
### Plotly Chart Studio
After creating a Plotly account, navigate to https://chart-studio.plotly.com/settings/api#/ and click *Generate Key*. In order to pass my information to Google Cloud Run, I stored this information in a json file like the following (again with sensitive information replaced):
```
{
  "username": "fake_username_1337",
  "api_key": "FAKE_API_KEY_1234"
}
```

# TODO

- Massively clean up plotting to allow for different modes of visibility (daily, weekly, monthly, yearly)
- Incorporate simple machine learning element to predict future occupancy based on historical data and current trends
