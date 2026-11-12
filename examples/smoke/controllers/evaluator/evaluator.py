"""Frozen evaluator (do not edit during the improvement loop).

Measures how many laps the robot completes along the ellipse centerline within
TRIAL_SIM_SECONDS, writes a JSON result to $TRIAL_RESULT and quits Webots.
"""
import json, math, os
from controller import Supervisor

A, B = 0.7, 0.5            # must match tools/make_track.py
OFF_LIMIT_M = 0.05         # farther than this from the centerline = off the line
OFF_ABORT_S = 2.0          # continuous off-line time that aborts the trial
SIM_SECONDS = float(os.environ.get("TRIAL_SIM_SECONDS", "60"))

CENTER = [(A * math.cos(2 * math.pi * i / 1440), B * math.sin(2 * math.pi * i / 1440)) for i in range(1440)]

def dist_to_line(x, y):
    return min(math.hypot(x - cx, y - cy) for cx, cy in CENTER)

sup = Supervisor()
dt = int(sup.getBasicTimeStep())
robot = sup.getFromDef("EPUCK")

x, y, _ = robot.getPosition()
prev = math.atan2(y / B, x / A)
angle = 0.0
err_sum, steps, off_time, off_total, reason = 0.0, 0, 0.0, 0.0, "time_up"

while sup.step(dt) != -1:
    x, y, _ = robot.getPosition()
    cur = math.atan2(y / B, x / A)
    d = cur - prev
    d = (d + math.pi) % (2 * math.pi) - math.pi
    angle += d
    prev = cur
    e = dist_to_line(x, y)
    err_sum += e
    steps += 1
    if e > OFF_LIMIT_M:
        off_time += dt / 1000
        off_total += dt / 1000
        if off_time >= OFF_ABORT_S:
            reason = "off_line"
            break
    else:
        off_time = 0.0
    if sup.getTime() >= SIM_SECONDS:
        break

result = {
    "score": round(abs(angle) / (2 * math.pi), 4),   # laps (higher is better)
    "laps": round(angle / (2 * math.pi), 4),
    "mean_abs_error_m": round(err_sum / max(steps, 1), 5),
    "off_line_s": round(off_total, 3),
    "sim_time_s": round(sup.getTime(), 3),
    "end": reason,
}
path = os.environ.get("TRIAL_RESULT")
if path:
    with open(path, "w") as f:
        json.dump(result, f)
print("EVAL_RESULT " + json.dumps(result), flush=True)
sup.simulationQuit(0)
