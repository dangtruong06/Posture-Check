from config import NOSE_HEIGHT_DIF, NOSE_TO_SHOULDER_DIF, SHOULDER_TILT_DIF, MIN_TILT_THRESHOLD

def compute_metrics(left_shoulder, right_shoulder, nose):

    # SLOUCHING CHECK, nose and shoulders Y direction
    shoulder_mid_y = (right_shoulder.y + left_shoulder.y) / 2
    distance_to_nose = shoulder_mid_y - nose.y

    # SHOULDER TILT CHECK
    shoulder_tilt = abs(right_shoulder.y - left_shoulder.y)
    
    return{
            "dist": distance_to_nose,
            "shoulder_tilt": shoulder_tilt,
            "nose_y": nose.y
    }

def average_samples(samples):
    #samples = [
    #{"dist": 0.18, "shoulder_tilt": 0.004, "nose_y": 0.32},    frame 1
    #{"dist": 0.19, "shoulder_tilt": 0.005, "nose_y": 0.31}

    keys = samples[0].keys()

    return{
        # for each key in samples, get average of values of keys, and return dictionary with key: average
        key: sum(s[key] for s in samples) / len(samples) for key in keys
    }

def check_posture(metrics, baseline):
    flags = []
    if metrics["dist"] < (baseline["dist"] * NOSE_TO_SHOULDER_DIF):
        flags.append("slouching_distance")

    if metrics["nose_y"] > (baseline["nose_y"] * NOSE_HEIGHT_DIF):
        flags.append("slouching_nose_height")

    tilt_threshold = max(baseline["shoulder_tilt"] * SHOULDER_TILT_DIF, MIN_TILT_THRESHOLD)
    if metrics["shoulder_tilt"] > tilt_threshold:
        flags.append("tilting")

    return flags
