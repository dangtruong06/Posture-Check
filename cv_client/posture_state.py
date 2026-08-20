import time

# OBJECT STATES
GOOD = 'good'
BAD = 'bad'
ALERTED = 'alerted'

class PostureState:

    # class object will accept flag 
    def __init__(self, bad_duration_threshold=60):
        self.state = GOOD
        self.bad_since = None
        self.bad_duration_threshold = bad_duration_threshold
        self.window_start_time = time.time()  #
        self.window_duration = 300  # 5 minutes between every db log, adjust as needed
        self.good_seconds = 0
        self.bad_seconds = 0
        self.alert_count = 0
        self.last_update_time = time.time()

    def update(self, flags):
        # find elapsed time between each update
        now = time.time()
        elapsed = now - self.last_update_time
        self.last_update_time = now

        should_alert = False

          # if good posture, reset
        if not flags:
            self.state = GOOD
            self.good_seconds += elapsed
            self.bad_since = None
        
        # if there is bad posture flag
        else:
            self.bad_seconds += elapsed

            # from good -> bad, set self state to bad and record the time
            if self.state == GOOD:
                self.state = BAD
                self.bad_since = time.time()
            
            # posture already bad, calculate elapsed time since bad posture started
            elif self.state == BAD:
                elapsed_time = time.time() - self.bad_since

            # if it has been 60 seconds since
                if elapsed_time > self.bad_duration_threshold:
                    self.state = ALERTED
                    self.alert_count += 1
                    should_alert = True
        
        summary = None
        if (time.time() - self.window_start_time) >= self.window_duration:
            summary = {
                'window_start': self.window_start_time,
                'window_end': time.time(),
                'time_in_good_posture': self.good_seconds,
                'time_in_bad_posture': self.bad_seconds,
                'times_notified': self.alert_count
            }

            # after logging the summary, reset to 0 to track the next posture window
            self.good_seconds = 0
            self.bad_seconds = 0
            self.alert_count = 0
            self.window_start_time = time.time()
        
        return should_alert, summary

      