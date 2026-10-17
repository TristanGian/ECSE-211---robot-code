from utils.brick import reset_brick, wait_ready_sensors, Motor, EV3ColorSensor, NXTColorSensor
import math
import time

if __name__ == "__main__":
    wait_ready_sensors()
    
    black_wait = 15
    prev_dl = 0
    prev_dr = 0
    theta = 0
    black_count = 0
    x = 0
    y = 0
    radius = 2.05 
    track_width = 13.4
    sensor_offset = 7.5
    sensor_diff = 5
    ev3arr = [46 + 15, 35 +15, 12 +15] #wood
    nxtarr = [512 +15, 354 +15, 313 +15] # wood
    motor = Motor("A") #left
    motor2 = Motor("B") #right
    ev = EV3ColorSensor(4) #left
    nxt = NXTColorSensor(1) #right
    
    motor.reset_encoder()
    motor2.reset_encoder()
    wait_ready_sensors()
    time.sleep(0.5)
    
    def update_odometer():
        global prev_dl , prev_dr, theta, x, y, radius, track_width
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
        motor.set_dps(-180 * 1/2)
        motor2.set_dps(-180 * 1/2)
        if 0 <= theta <= 89:
            initial = x
            while(x < initial + d):
                update_odometer()
                correction()
                time.sleep(0.01)
        if 89 < theta <= 179:
            initial = y
            while(y < initial + d):
                update_odometer()
                correction()
                time.sleep(0.01)
        if 180 < theta <= 269:
            initial = x
            while(x > initial - d):
                update_odometer()
                correction()
                time.sleep(0.01)
        if 270 < theta <= 359:
            initial = y
            while(y > initial - d):
                update_odometer()
                correction()
                time.sleep(0.01)
    
    def turn(turnAngle):
        initial = theta
        motor.set_dps(-30 * 1)
        motor2.set_dps(30 * 1)
        while(theta < initial + turnAngle):
            update_odometer()
            time.sleep(0.01)
    
    def float_motors():
        motor.float_motor()
        motor2.float_motor()
        
        while(True):
            update_odometer()
            time.sleep(0.01)

    def square_driver(): 
        for i in range(4):
            print("square_driver trigg")
            move_forward(90)
            turn(90)
    def correction():
        global black_count
        ev3_res, nxt_res = measureblack()
        if(ev3_res != nxt_res and ev3_res ==1):
            black_m = 0
            while black_m == 0 :
                motor.set_dps(0)
                motor2.set_dps(-5 * 2)
                blank,black_m =measureblack()
                time.sleep(0.01)
            motor.set_dps(-180 * 1/2 )
            motor2.set_dps(-180 * 1/2)
            black_count = 1
        elif(ev3_res != nxt_res and nxt_res == 1):
            black_m = 0
            while black_m == 0 :
                motor.set_dps(-5 * 2)
                motor2.set_dps(0)
                black_m,blank =measureblack()
                time.sleep(0.01)
            motor.set_dps(-180 * 1/2)
            motor2.set_dps(-180 * 1/2)
            black_count =1
            
    def measureblack():
        global black_count
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
            print(val2[i])
            if val1[i] >= 1.5:
                flag1 = 0
            if val2[i] >= 0.9102:
                flag2 = 0
        return (flag1, flag2)
    square_driver()
    reset_brick()