import requests
from datetime import datetime


API_BASE_URL = "http://localhost:8000/api"

def epoch_to_datetime(s):
    return datetime.fromtimestamp(s).isoformat()

def refresh_access_token(refresh_token):
    try:
        response = requests.post(
            f"{API_BASE_URL}/token/refresh/",
            json={'refresh': refresh_token}
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to get new token: {e}")
        return None

    data = response.json()
    return data['access']

def send_summary(summary, access_token, refresh_token):
    start = epoch_to_datetime(summary["window_start"])
    end = epoch_to_datetime(summary["window_end"])
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "window_start": start,
        "window_end": end,
        "time_in_good_posture": round(summary["time_in_good_posture"]),
        "time_in_bad_posture": round(summary["time_in_bad_posture"]),
        "times_notified": summary["times_notified"],
    }

    try:
        response = requests.post(f"{API_BASE_URL}/posture_summaries/", json=payload, headers=headers)
        response.raise_for_status()
        return access_token

    except requests.exceptions.RequestException as e:
        if e.response is None or e.response.status_code != 401:
            print(f"Failed to send summary: {e}")
            return access_token

        new_token = refresh_access_token(refresh_token)
        if new_token is None:
            print("Fail to refresh token")
            return access_token

        headers = {
            "Authorization": f"Bearer {new_token}"
        }
        try:
            retry_response = requests.post(f"{API_BASE_URL}/posture_summaries/", json=payload, headers=headers)
            retry_response.raise_for_status()
            return new_token
        except requests.exceptions.RequestException as retry_error:
            print(f"Failed to send summary after refresh: {retry_error}")
            return new_token