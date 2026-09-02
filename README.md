# Posture Detector

A real-time computer vision posture detector: a webcam feed is analyzed with MediaPipe pose landmarks, evaluated by a custom posture state machine, and posture trends are logged to a Django REST API backed by PostgreSQL. A Python desktop GUI (PySide6) ties everything together, with Google OAuth2/OIDC for login, and camera controls to start and stop the camera process.

# Application Architecture
## Module Overview
cv_client/ - Computer Vision & State Analysis
- Camera Process (main.py): Captures live webcam footage and feeds video frames into MediaPipe for pose landmark detection.
- Posture State Machine (posture_state.py): Dedicated state machine class to track, update, and build posture summaries (Example: Good: 10s, Bad: 2s).
- Backend ingestion: Posts posture event updates asynchronously to backend.

posture_backend/ - API Service & Database
- Authentication: Handles user registration, login JWT token generation, and secure session management.
- Database Management: Stores posture summary logs, session analytics like time/frequency, and user metadata.
- REST API: Exposes endpoints for data ingestion from CV Client, and data fetching on GUI Client.

gui/ - Desktop User Interface
- Framework: Built using PySide6 (QT)
- Renders Login and Registration interface
- Analytics Dashboard: Retrieves data from the backend through GET requests to fetch and render posture stats in real time.

Debugging / Design notes
- After authenticating with google and querying the correct user's data, a problem that needed to be solved was how to correctly log posture data to the correct user on the cv client side. 
- The solution was on log in, the GUI will hold the access token as a python attribute. Then when the GUI starts the camera process, the access token is set as an environment variable for the camera process through Popen(..., env=env).
- Since the camera process now has access to the token, the only job left is to pass the token as an argument to api_client, build the request with the correct headers, and log data correctly with the provided bearer token
