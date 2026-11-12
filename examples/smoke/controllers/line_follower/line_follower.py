"""Baseline line follower for the e-puck (this is the file the agent improves)."""
from controller import Robot

robot = Robot()
dt = int(robot.getBasicTimeStep())
gs = [robot.getDevice(f"gs{i}") for i in range(3)]
for s in gs:
    s.enable(dt)
left, right = robot.getDevice("left wheel motor"), robot.getDevice("right wheel motor")
for m in (left, right):
    m.setPosition(float("inf"))
    m.setVelocity(0)

BASE, GAIN = 4.0, 0.004
while robot.step(dt) != -1:
    l, _, r = (s.getValue() for s in gs)
    turn = GAIN * (l - r)          # line under the left sensor -> l is darker -> turn left
    left.setVelocity(max(-6.28, min(6.28, BASE + turn)))
    right.setVelocity(max(-6.28, min(6.28, BASE - turn)))
