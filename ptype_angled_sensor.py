from utils.brick import reset_brick, wait_ready_sensors, Motor, EV3UltrasonicSensor
import math
import time

SENSOR_ANGLE_DEG = 45
COS_A = math.cos(math.radians(SENSOR_ANGLE_DEG))

TARGET = 20
DEADBAND = 1
CORNER_DIST = 10
NO_WALL = 100
GAP_TIME = 1
OFFSET = 5
TARGET = TARGET + OFFSET

KP = 3.0
MAX_CORR = 20
BASE_SPEED = 35
MAX_POWER = 65

WRAP_RIGHT = (-25, -17.5)
PIVOT_LEFT = (20, -50)

left = Motor("A")
right = Motor("B")
us = EV3UltrasonicSensor(2)


def keep_bounds(x, lo, hi):
    return max(lo, min(hi, x))


def drive(l, r):
    left.set_power(keep_bounds(l, -MAX_POWER, MAX_POWER))
    right.set_power(keep_bounds(r, -MAX_POWER, MAX_POWER))


def read_raw():
    samples = []
    for _ in range(3):
        d = us.get_cm()
        if d is not None:
            samples.append(d)
        time.sleep(0.03)
    if not samples:
        return None
    return sorted(samples)[len(samples) // 2]


def steer(dist):
    error = dist - TARGET
    if abs(error) < DEADBAND:
        error = 0
    corr = keep_bounds(KP * error, -MAX_CORR, MAX_CORR)
    left_mag = BASE_SPEED + corr
    right_mag = BASE_SPEED - corr
    drive(-left_mag, -right_mag)


def main():
    wait_ready_sensors()
    left.reset_encoder()
    right.reset_encoder()
    time.sleep(1)

    lost_since = None
    try:
        while True:
            raw = read_raw()
            if raw is None:
                continue

            if raw * COS_A > NO_WALL:
                if lost_since is None:
                    lost_since = time.time()
                if time.time() - lost_since < GAP_TIME:
                    drive(-BASE_SPEED, -BASE_SPEED)
                else:
                    drive(*WRAP_RIGHT)
                continue

            lost_since = None
            dist = raw * COS_A

            if dist < CORNER_DIST:
                drive(*PIVOT_LEFT)
            else:
                steer(dist)
    finally:
        drive(0, 0)
        reset_brick()


if __name__ == "__main__":
    main()