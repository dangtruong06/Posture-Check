# Posture Detector

A real-time computer vision posture detector: a webcam feed is analyzed with MediaPipe pose landmarks, evaluated by a custom posture state machine, and logged to a Django REST API backed by PostgreSQL. A Python desktop GUI (PySide6) ties everything together, with Google OAuth2/OIDC for login.

Debugging / Design notes
- After authenticating with google and querying the correct user's data, a problem that needed to be solved was how to correctly log posture data to the correct user on the cv client side. 
- The solution was on log in, the GUI will hold the access token as a python attribute. Then when the GUI starts the camera process, the access token is set as an environment variable for the camera process through Popen(..., env=env).
- Since the camera process now has access to the token, the only job left is to pass the token as an argument to api_client, build the request with the correct headers, and log data correctly with the provided bearer token