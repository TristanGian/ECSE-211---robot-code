from utils.brick import reset_brick, wait_ready_sensors, Motor, EV3ColorSensor, NXTColorSensor
import time

motor = Motor("A") #left
motor2 = Motor("B") #right

color_sensor1 = EV3ColorSensor(4) #left_sensor
color_sensor2 = NXTColorSensor(3) #right_sensor
wait_ready_sensors()

motor.reset_encoder()


    
while True:
    color1 = color_sensor1.get_rgb()
    print(color1)
    
    color2 = color_sensor2.get_rgb()

    print(color2)
    time.sleep(0.5)

print(motor.get_encoder())
motor.set_dps(360)
motor2.set_dps(-360)
time.sleep(1)

print(motor.get_encoder())


reset_brick()




