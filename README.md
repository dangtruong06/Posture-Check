# Posture Detector

A real-time computer vision posture detector: a webcam feed is analyzed with MediaPipe pose landmarks, evaluated by a custom posture state machine, and posture trends are logged to a Django REST API backed by PostgreSQL. A Python desktop GUI (PySide6) enables user authentication with Google OAuth2/OIDC, camera controls to start and stop the tracking process, and live analysitcs dashboard with matplotlib.

## Features

- Real-time pose tracking via webcam + MediaPipe, to calibrate and begin tracking, sit up straight and press 'c' while the camera window is on screen/focused.
- Custom posture state machine that tracks good/bad posture over time and triggers a desktop notification after sustained bad posture
- Posture summaries logged to a REST API every 5 minutes (good seconds, bad seconds, alert count)
- Google OAuth2/OIDC login (PKCE flow) — no separate account system, sign in with an existing Google account
- Desktop dashboard (PySide6) with:
  - Start/Stop controls for the camera process
  - A pie chart (good vs. bad posture) and stat cards for percentage, minutes, and alert count
  - Stats computed as a rolling average/sum over the last 3 logged windows (~15 minutes) rather than a single noisy reading
  - Auto-refreshing data on a background thread, polling roughly every 5 minutes 15 seconds — never blocks the UI

## Application Architecture

### `cv_client/` — Computer Vision & State Analysis

- **Camera process (`main.py`)** — captures live webcam footage and feeds video frames into MediaPipe for pose landmark detection; runs as its own OS process, launched by the GUI via `subprocess.Popen`, with its own native `cv2.imshow()` window independent of the GUI's event loop
- **Posture state machine (`posture_state.py`)** — a dedicated `PostureState` class that tracks elapsed good/bad time, detects sustained bad posture (default: 60+ seconds triggers an alert), and builds a summary dict every 5-minute window (`window_duration = 300`)
- **Backend ingestion (`api_client.py`)** — posts posture summaries to the backend once per window; if the access token has expired, transparently refreshes it and retries before giving up

### `posture_backend/` — API Service & Database

- **Authentication** — Google ID token verification, JWT (SimpleJWT) issuance and refresh
- **Database** — PostgreSQL, storing per-user posture summary logs (window start/end, time in good/bad posture, alert count)
- **REST API** — endpoints for summary ingestion (cv_client) and summary retrieval (GUI), plus token refresh

### `gui/` — Desktop User Interface

- **Framework** — PySide6 (Qt)
- **Login screen** — Google sign-in button, styled with a light theme, launches the OAuth flow on a background thread so the UI never freezes while waiting on the browser
- **Dashboard** — Start/Stop camera controls, a matplotlib pie chart embedded via `FigureCanvasQTAgg`, and stat cards; fetches data on a background thread on a timer so the UI stays responsive

## Authentication & Token Flow

Since `cv_client` (posting data) and the GUI (fetching data) are fully separate OS processes with no shared memory or IPC, each side independently holds and manages its own copy of the user's tokens.

**Getting the token to `cv_client`:** on login, the GUI holds the access and refresh tokens in memory. When the camera process is launched, both tokens are passed in as environment variables (`POSTURE_ACCESS_TOKEN`, `POSTURE_REFRESH_TOKEN`) via `subprocess.Popen(..., env=env)`. `cv_client` reads them at startup and threads them through to every request it sends.

**Handling token expiry:** JWT access tokens are short-lived (5 minutes, SimpleJWT's default). Rather than requiring the user to log in again every 5 minutes, both sides independently detect a `401 Unauthorized`, call the backend's `/api/token/refresh/` endpoint with the refresh token to mint a new access token, retry the original request once, and keep using the new access token going forward:

- **`cv_client`** — `send_summary()` catches the 401, refreshes, retries the POST, and returns whichever token is now valid so `main.py`'s loop can keep using it for the next summary
- **GUI** — `SummaryFetchWorker` does the same for its GET request, emitting back the current valid token so `DashboardScreen` can use it on the next scheduled poll

The refresh token itself is long-lived and doesn't change during this process — only the access token gets swapped out as needed.

## Design Notes

- **cv_client and the GUI have no direct communication.** They're deliberately separate processes, so the GUI can't be notified the moment a new summary is posted. Instead, it polls on a `QTimer` roughly every 5 minutes 15 seconds (a small buffer past the 5-minute logging window, so it isn't racing the database write), doing the actual HTTP fetch on a background `QThread` so the UI never freezes.
- **Dashboard stats are a rolling window, not a single reading.** The most recent 3 summaries are summed (not averaged individually) to get true totals for time and alerts, then percentages are derived from those totals — this avoids one noisy 5-minute window skewing the display, and avoids a subtle bug where averaging percentages first collapses the displayed minutes back down to a single window's worth instead of the true multi-window total.
