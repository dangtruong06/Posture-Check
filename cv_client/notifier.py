from plyer import notification

def send_alert(title, message, timeout=10):
    try:
        notification.notify(
            title=title, 
            message=message, 
            app_name="Posture Checker", 
            timeout=timeout
        )
    except Exception as e:
        print(f"[Notification failed: {e}] {title} - {message}")

