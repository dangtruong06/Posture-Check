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

    def update(self, flags):

        # if good posture, reset
        if not flags:
            self.state = GOOD
            self.bad_since = None
            return False
        
        # if there is bad posture flag
        if flags:

            # from good -> bad, set self state to bad and record the time
            if self.state == GOOD:
                self.state = BAD
                self.bad_since = time.time()
                return False
            
            # posture already bad, calculate elapsed time since bad posture started
            if self.state == BAD:
                elapsed_time = time.time() - self.bad_since

            # if it has been 60 seconds since
                if elapsed_time > self.bad_duration_threshold:
                    self.state = ALERTED
                    return True
            
                return False
            
            # after alerting but posture is still bad, don't spam alerts
            if self.state == ALERTED:
                return False
