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
    h= 0
    radius = 2.05 
    track_width = 13.4
    motor = Motor("A") #left
    motor2 = Motor("B") #right
    DRIVE_SPEED = -180 * 1/3 #DPS
    TURN_SPEED = 30 * 1 #DPS
    DEGREE_TOLERANCE = 1.5 #degrees
    SQUARE_SIZE = 30.48 # cm
    COORDINATES  = []
    current_angle = 0
    
    
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
        h= h + d_diff
        x = x + d_diff*math.cos(math.radians(theta)) #difference theta
        y = y + d_diff*math.sin(math.radians(theta)) #difference theta
        print("The value of X: ", x)
        print("The value of Y: ", y)
        print("the value of theta: ", theta )

    def move_forward(d):
            initial = h
            motor.set_dps(DRIVE_SPEED)
            motor2.set_dps(DRIVE_SPEED)
            while(h < initial + d): 
                update_odometer()
                time.sleep(0.01)

    def turn(turnAngle):
            global current_angle
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

    def calculateMoveArr(coordinates): #coordinates should be [x,y]
        arr = []  #[distance in cm, angle in degrees]
        prev = [0, 0]
        prev_angle = 0
        for i in range(coordinates):
            angle = math.atan2(coordinates[i][1] - prev[1], coordinates[i][0] - prev[0])*(180/math.pi)
            angle = angle - prev_angle
            if angle > 180:
                 angle = -(360 - angle)
            distance = math.sqrt(math.pow(coordinates[i][0] - prev[0], 2) + math.pow(coordinates[i][1] - prev[1], 2))
            distance = distance * SQUARE_SIZE
            arr[i] = [distance, angle]     
            prev = coordinates[i]  
        return arr

    instructions = calculateMoveArr(COORDINATES)
    for i in range(instructions):
        turn(instructions[i][1])
        move_forward(instructions[i][0]) 