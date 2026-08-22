#Posture Detector

A real-time computer vision posture detector: a webcam feed is analyzed with MediaPipe pose landmarks, evaluated by a custom posture state machine, and logged to a Django REST API backed by PostgreSQL. A Python desktop GUI (PySide6) ties everything together, with Google OAuth2/OIDC for login.
