import requests
from datetime import datetime


API_BASE_URL = "http://localhost:8000/api"

def epoch_to_datetime(s):
    return datetime.fromtimestamp(s).isoformat()


def send_summary(summary, access_token):
    start = epoch_to_datetime(summary["window_start"])
    end = epoch_to_datetime(summary["window_end"])
    headers = {
        "Authorization" : f"Bearer {access_token}"
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
    except requests.exceptions.RequestException as e:
        print(f"Failed to send summary: {e}")