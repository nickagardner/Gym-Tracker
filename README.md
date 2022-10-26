# Gym Tracker

Simple script to scrape data from RIT's gym website and store that data in a Firebase NoSQL database. This script is passed in to Google Cloud Run along with credentials files (not included here) for Firebase. Following a pub/sub trigger, this file scrapes the website and stores the result in the database. This database is used by my related repository, https://github.com/nickagardner/Gym-Tracker-Renderer, to render a world-visible plot showing current and historical gym occupancy.

Link to plot (on my website): https://www.nickgardner.us/gym_tracker.html

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

# TODO

- Incorporate simple machine learning element to predict future occupancy based on historical data and current trends. Waiting for a sufficiently large dataset for this.
