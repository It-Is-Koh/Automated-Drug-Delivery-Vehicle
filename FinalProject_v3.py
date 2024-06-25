from machine import Pin, PWM, freq, SoftI2C
from time import sleep
from hcsr04 import HCSR04
import ssd1306
import _thread

class Motor:
    def __init__(self, Pin_A1A, Pin_A1B, Pin_B1A, Pin_B1B):
        self.A1A = Pin(Pin_A1A, Pin.OUT) # Left +
        self.A1B = Pin(Pin_A1B, Pin.OUT) # Left -
        self.B1A = Pin(Pin_B1A, Pin.OUT) # Right +
        self.B1B = Pin(Pin_B1B, Pin.OUT) # Right -
    
    def motor_forward(self):
        self.A1A.value(1)
        self.A1B.value(0)
        self.B1A.value(1)
        self.B1B.value(0)
    
    def motor_backward(self):
        self.A1A.value(0)
        self.A1B.value(1)
        self.B1A.value(0)
        self.B1B.value(1)
    
    def motor_left(self): # Turning Left = Rolling Right Wheels
        self.A1A.value(0)
        self.A1B.value(1)
        self.B1A.value(1)
        self.B1B.value(0)
    
    def motor_right(self): # Turning Right = Rolling Left Wheels
        self.A1A.value(1)
        self.A1B.value(0)
        self.B1A.value(0)
        self.B1B.value(1)
    
    def motor_stop(self):
        self.A1A.value(0)
        self.A1B.value(0)
        self.B1A.value(0)
        self.B1B.value(0)

class PathSensor():
    def __init__(self, Pin_LeftSensor, Pin_RightSensor, Pin_HCSRTrigger, Pin_HCSREcho):
        self.leftSensor = Pin(Pin_LeftSensor, Pin.IN)
        self.rightSensor = Pin(Pin_RightSensor, Pin.IN)
        self.obstacleSensor = HCSR04(trigger_pin=Pin_HCSRTrigger, echo_pin=Pin_HCSREcho, echo_timeout_us=10000)

class DrugContainer():
    def __init__(self, Pin_Servo, Pin_Button, Pin_Buzzer, Pin_OLEDSCL, Pin_OLEDSDA):
        self.servo = PWM(Pin(Pin_Servo), freq=50)
        self.servo.duty(0)
        self.start_stop_pin = Pin(Pin_Button, Pin.IN, Pin.PULL_DOWN)
        self.buzzer = PWM(Pin(Pin_Buzzer))
        self.buzzer.deinit()
        self.i2c = SoftI2C(scl=Pin(Pin_OLEDSCL), sda=Pin(Pin_OLEDSDA), freq=400000)
        self.display = ssd1306.SSD1306_I2C(width=128, height=64, i2c=self.i2c)
    
    def container_spin(self):
        self.servo.duty(80)
#         sleep(0.675)
        sleep(0.75)
        self.servo.duty(0)
    
    def buzzing(self, freq, beat):
        self.buzzer.freq(freq)
        sleep(beat)
    
    def container_waiting(self):
        self.buzzer.init()
        self.buzzer.duty(512)
        
        buzzing_freq = [330, 262, 196, 262, 294, 392, 294, 330, 294, 196, 262]
#         buzzing_freq = [659, 523, 392, 523, 587, 784, 587, 659, 587, 392, 523]
        buzzing_beat = [0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5, 0.5, 0.5, 0.5, 1.5]
        
        global receiveButton
        buzzing_stop = False
        while True:
            for i in range(len(buzzing_freq)):
                self.buzzing(buzzing_freq[i], buzzing_beat[i]/5)
                if receiveButton:
                    buzzing_stop = True
                    break
            if buzzing_stop:
                break
        
        self.buzzer.deinit()
    
    def display_patient_1(self):
        self.display.text("Wu Li-How", 0, 22)
        self.display.text("-Sildenafil", 0, 39)
        self.display.text("-Methylphenidate", 0, 50)
    
    def display_patient_2(self):
        self.display.text("WuWu", 0, 22)
        self.display.text("-Smarter Pill", 0, 39)
        self.display.text("-Memory Toast", 0, 50)
    
    def display_patient_3(self):
        self.display.text("LiLi", 0, 22)
        self.display.text("-Melatonin", 0, 39)
        self.display.text("-Dopamine", 0, 50)
    
    def display_patient_4(self):
        self.display.text("HowHow", 0, 22)
        self.display.text("-Aspirin", 0, 39)
        self.display.text("-Flying Candy", 0, 50)
    
    def OLED_showing(self, patientNo):
        text = "Press the button after taking the medication."
        i = 0
        place = 128
        global receiveButton
        showing_stop = False
        while True:
            for i in range(len(text)+16):
                if i < 16:
                    show_text = text[0:i]
                    place = place - 8
                    self.display.text(show_text, place, 0)
                else:
                    show_text = text[(i-16):]
                    self.display.text(show_text, 0, 0)
                if patientNo == 1:
                    self.display_patient_1()
                elif patientNo == 2:
                    self.display_patient_2()
                elif patientNo == 3:
                    self.display_patient_3()
                elif patientNo == 4:
                    self.display_patient_4()
                self.display.show()
                sleep(0.1)
                self.display.fill(0)
                if receiveButton:
                    showing_stop = True
                    break
            if showing_stop:
                break
            i = 0
            place = 128

def start_stop_handler(pin):
    global receiveButton
    receiveButton = True

if __name__ == "__main__":
    motor1 = Motor(Pin_A1A=19, Pin_A1B=18, Pin_B1A=17, Pin_B1B=16)
    motor2 = Motor(Pin_A1A=23, Pin_A1B=26, Pin_B1A=27 , Pin_B1B=5)
    pathSensor = PathSensor(Pin_LeftSensor=33, Pin_RightSensor=32, Pin_HCSRTrigger=14, Pin_HCSREcho=12)
    drugContainer = DrugContainer(Pin_Servo=2, Pin_Button=34, Pin_Buzzer=25, Pin_OLEDSCL=22, Pin_OLEDSDA=21)
    drugContainer.start_stop_pin.irq(trigger=Pin.IRQ_FALLING, handler=start_stop_handler)
    patientNo = 1
    sleep(5)
    while True:
        if pathSensor.obstacleSensor.distance_cm() <= 20: # sensing obstacle at front - stop
            print("Obstacle Sensed")
            motor1.motor_stop()
            motor2.motor_stop()
            drugContainer.display.text("Obstacle Sensed", 0, 0)
            drugContainer.display.show()
        elif pathSensor.leftSensor.value() == 1 and pathSensor.rightSensor.value() == 1: # sensing black line mark - stop
            receiveButton = False
            print("Drug Delivering")
            motor1.motor_stop()
            motor2.motor_stop()
            drugContainer.display.text("Drug Delivering", 0, 0)
            drugContainer.display.show()
            sleep(1)
            print("\tSpin Start")
            drugContainer.container_spin()
            sleep(1)
            print("\tWaiting for Button")
            
            # Create threads for container_waiting and OLED_showing
            receiveButton = False
            _thread.start_new_thread(lambda: drugContainer.container_waiting(), ())
            _thread.start_new_thread(lambda: drugContainer.OLED_showing(patientNo), ())
            while not receiveButton:
                sleep(0.1)
                pass
            drugContainer.display.fill(0)
            drugContainer.display.show()
            patientNo += 1
            if patientNo == 5:
                patientNo = 1
            sleep(1)
            
            print("\tContinue Going")
            motor1.motor_forward()
            motor2.motor_forward()
            sleep(0.25)
        elif pathSensor.leftSensor.value() == 1: # sensing black road on left side - receive no reflection: 1
            print("Turning Left")
            motor1.motor_left()
            motor2.motor_left()
            drugContainer.display.text("Turning Left", 0, 0)
            drugContainer.display.show()
        elif pathSensor.rightSensor.value() == 1: # sensing black road on right side - receive no reflection: 1
            print("Turning Right")
            motor1.motor_right()
            motor2.motor_right()
            drugContainer.display.text("Turning Right", 0, 0)
            drugContainer.display.show()
        else:
            print("Moving Forward")
            motor1.motor_forward()
            motor2.motor_forward()
            drugContainer.display.text("Moving Forward", 0, 0)
            drugContainer.display.show()
        sleep(0.005) # make a decision for every 0.005 seconds
