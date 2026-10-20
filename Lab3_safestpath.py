from utils.brick import reset_brick, wait_ready_sensors, Motor, EV3ColorSensor, NXTColorSensor
import math
import time

if __name__ == "__main__":
    wait_ready_sensors()
    
    prev_dl = 0
    prev_dr = 0
    theta = 0
    x = 0
    y = 0
    radius = 2.05 
    track_width = 13.4
    current_angle = 0
    black_hit = 0
    black_count = 0
    motor = Motor("A") #left
    motor2 = Motor("B") #right
    ev = EV3ColorSensor(4) #left
    nxt = NXTColorSensor(1) #right
    ev3arr = [254, 175, 71] #wood
    nxtarr = [681, 525, 435] # wood
    DRIVE_SPEED = -180 * 1/3 #DPS
    TURN_SPEED = 30 * 1 #DPS
    EV3_TOLERANCE = 0.75
    NXT_TOLERANCE = 0.75
    DEGREE_TOLERANCE = 1.5 #degrees
    SQUARE_SIZE = 30.48 # cm
    COORDINATES  = []
    CORRECTION_TURN_SPEED = -5 * 3
    BLACK_WAIT_DRIVE = 100 #checks val * 0.01 sec
    BLACK_WAIT_TURN = 50
    black_wait = BLACK_WAIT_DRIVE
    
    
    motor.reset_encoder()
    motor2.reset_encoder()
    wait_ready_sensors()
    time.sleep(0.5)
    
    def update_odometer():
        global prev_dl , prev_dr, theta, x, y, radius, track_width, h
        dl = -1*motor.get_encoder()
        dr = -1*motor2.get_encoder()
        #print("dl: ",dl)
        #print("dr: ", dr)
        dl_diff = ((dl - prev_dl) * 2 * math.pi * radius) /360
        dr_diff = ((dr - prev_dr) * 2 * math.pi * radius) /360
        prev_dl = dl
        prev_dr = dr
        d_diff = (dl_diff+dr_diff)/2
        theta_diff = math.asin((dl_diff - dr_diff)/track_width) *180/ math.pi
        theta = (theta + theta_diff)%360
        x = x + d_diff*math.cos(math.radians(theta)) #difference theta
        y = y + d_diff*math.sin(math.radians(theta)) #difference theta
        print("The value of X: ", x)
        print("The value of Y: ", y)
        print("the value of theta: ", theta )

    def move_forward(d):
        black_hit = 0
        motor.set_dps(DRIVE_SPEED)
        motor2.set_dps(DRIVE_SPEED)
        while(black_hit < d):
            update_odometer()
            correction()
            time.sleep(0.01)

    def turn(turnAngle):
        global current_angle
        global black_count
        global black_wait
        turned = 0
        last = theta
        if (turnAngle > 0): #if turning right
            motor.set_dps(-TURN_SPEED)
            motor2.set_dps(TURN_SPEED)
            while(turned < turnAngle + DEGREE_TOLERANCE):
                update_odometer()
                turned += (theta - last + 180) % 360 - 180
                last = theta
                time.sleep(0.01)
                current_angle = (current_angle + turnAngle) % 360
        elif (turnAngle < 0): #if turning left
            motor.set_dps(TURN_SPEED)
            motor2.set_dps(-TURN_SPEED)
            while(turned < -turnAngle + DEGREE_TOLERANCE):
                update_odometer()
                turned += (abs(theta - last) + 180) % 360 - 180
                last = theta
                time.sleep(0.01)
            current_angle = (current_angle + turnAngle) % 360
        black_count = 1
        black_wait = BLACK_WAIT_TURN

    def correction():
        global black_count
        global theta
        global black_wait
        global black_hit
        ev3_res, nxt_res = measureblack()
        if(ev3_res != nxt_res and ev3_res ==1):
            black_m = 0
            while black_m == 0 :
                motor.set_dps(0)
                motor2.set_dps(CORRECTION_TURN_SPEED)
                blank,black_m =measureblack()
                update_odometer()
                time.sleep(0.01)
            motor.set_dps(DRIVE_SPEED)
            motor2.set_dps(DRIVE_SPEED)
            black_count = 1
            theta = current_angle
            black_wait = BLACK_WAIT_DRIVE
        elif(ev3_res != nxt_res and nxt_res == 1):
            black_m = 0
            while black_m == 0 :
                motor.set_dps(CORRECTION_TURN_SPEED)
                motor2.set_dps(0)
                black_m,blank =measureblack()
                update_odometer()
                time.sleep(0.01)
            motor.set_dps(DRIVE_SPEED)
            motor2.set_dps(DRIVE_SPEED)
            black_count =1
            theta = current_angle
            black_wait = BLACK_WAIT_DRIVE
        elif(nxt_res == 1 and ev3_res ==1):
            black_count = 1
        if(nxt_res == 1 or ev3_res == 1):
            black_hit = black_hit +1

    def measureblack():
        global black_count
        black_wait
        if (0 < black_count < black_wait):
            black_count = black_count +1
            return (0,0)
        elif (black_count > black_wait):
            black_count =0
        val1 = ev.get_rgb()
        val2 = nxt.get_rgb()
        flag1 = 1
        flag2 = 1
        for i in range(3):
            val1[i] = val1[i]/ev3arr[i]
            val2[i] = val2[i]/nxtarr[i]
        for i in range(3):
            if val1[i] >= EV3_TOLERANCE:
                flag1 = 0
            if val2[i] >= NXT_TOLERANCE:
                flag2 = 0
        return (flag1, flag2)


    #NEED FUCNTION TO CONVERT X,Y POINTS INTO UP DOWN SO ITS JUST TURN AND DRIVE DISTANCE 