from utils.brick import reset_brick, wait_ready_sensors, Motor, EV3UltrasonicSensor
import math
import time

SENSOR_ANGLE_DEG = 45
COS_A = math.cos(math.radians(SENSOR_ANGLE_DEG))

BAND_CENTER = 20
BAND_WIDTH = 3
CORNER_DIST = 15
NO_WALL = 50
GAP_TIME = 0.6
OFFSET = 5
BAND_CENTER = OFFSET + BAND_CENTER

FWD, SLOW, FAST = -35  , -30  , -50
PIVOT_LEFT = (20, -50)
PIVOT_RIGHT = (-45,-30)

left = Motor("A")
right = Motor("B")
us = EV3UltrasonicSensor(2)


def drive(l, r):
    left.set_power(l)
    right.set_power(r)


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
                    drive(FWD, FWD)
                else:
                    drive(*PIVOT_RIGHT)
                continue

            lost_since = None
            dist = raw * COS_A

            if dist < CORNER_DIST:
                drive(*PIVOT_LEFT)
            elif dist < BAND_CENTER - BAND_WIDTH:
                drive(SLOW, FAST)
            elif dist > BAND_CENTER + BAND_WIDTH:
                drive(FAST, SLOW)
            else:
                drive(FWD, FWD)
    finally:
        drive(0, 0)
        reset_brick()


if __name__ == "__main__":
    main()