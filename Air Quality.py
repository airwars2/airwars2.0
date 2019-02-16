from mcp3208 import MCP3208
import time
import RPi.GPIO as GPIO
import urllib3
import sys
import dht11
myApi='BX6XQXZTWEE9D8WE'
baseURL="https://api.thingspeak.com/update?api_key=%s" %myApi
LED1=16
LED2=23
LED3=24

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(LED1,GPIO.OUT)
GPIO.setup(LED2,GPIO.OUT)
GPIO.setup(LED3,GPIO.OUT)

LCD_RS = 21
LCD_E  = 20
LCD_D4 = 26
LCD_D5 = 19
LCD_D6 = 13
LCD_D7 = 6

LCD_WIDTH = 16  
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 
LCD_LINE_2 = 0xC0

E_PULSE = 0.0005
E_DELAY = 0.0005
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED=16
GPIO.setup(LED,GPIO.OUT)
adc= MCP3208()

def Map(x,in_min,in_max,out_min,out_max):
    return (x - in_min)*(out_max - out_min)/(in_max - in_min)+out_min




def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT)  # E
    GPIO.setup(LCD_RS, GPIO.OUT) # RS
    GPIO.setup(LCD_D4, GPIO.OUT) # DB4
    GPIO.setup(LCD_D5, GPIO.OUT) # DB5
    GPIO.setup(LCD_D6, GPIO.OUT) # DB6
    GPIO.setup(LCD_D7, GPIO.OUT) # DB7
    lcd_init()
    while True:
        MQ2=adc.read(0)
        MQ9=adc.read(1)
        MQ135=adc.read(2)
        instance=dht11.DHT11(pin=18)
        result=instance.read()
        smoke=int(Map(MQ2,0,4095,0,100))
        carbon=int(Map(MQ9,0,4095,0,14))
        #Benzene=int(Map(MQ135,0,4095,10,1000))
        Air=int(Map(MQ135,0,4095,10,300))
        time.sleep(2)
        x="CO = "
        temp=str(carbon)
        y="AQ = "
        temp1=str(Air)

        lcd_string(x+temp+","+y+temp1,LCD_LINE_1)
        time.sleep(1)
        print("Smoke level = ",smoke)
        print("Carbon level = ",carbon)
	#print("NH3 = ",NH3)
        print("Air Quality =",Air)
        temp=result.temperature
        a="Temprature = "
        if(temp==0):
            pass
        else:
            print("Temperature: %d C" % result.temperature)
            lcd_string(a+str(temp),LCD_LINE_2)
		#print("Alchohol=",Alchohol)
        lcd_string("AirWars2.0",LCD_LINE_1)
        
        time.sleep(1)
        if(smoke>14 or Air>50 or carbon>7):
            lcd_string("Air Quality:",LCD_LINE_1)
            lcd_string("Inhabitable",LCD_LINE_2)
            time.sleep(1)

        else:
            lcd_string("Air Quality:",LCD_LINE_1)
            lcd_string("Good",LCD_LINE_2)
            time.sleep(1)
        #print("Benzene =",Benzene)
        http = urllib3.PoolManager()
        conn=http.request('GET',baseURL + '&field1=%s&field2=%s&field3=%s&field4=%s' %(Air,carbon,smoke,temp))
        conn.read()
        conn.close()
def lcd_init():
  # Initialise display
    lcd_byte(0x33,LCD_CMD) # 110011 Initialise
    lcd_byte(0x32,LCD_CMD) # 110010 Initialise
    lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
    lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
    lcd_byte(0x01,LCD_CMD) # 000001 Clear display
    time.sleep(E_DELAY)
 
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
    GPIO.output(LCD_RS, mode) # RS
 
  # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x10==0x10:
        GPIO.output(LCD_D4, True)
    if bits&0x20==0x20:
        GPIO.output(LCD_D5, True)
    if bits&0x40==0x40:
        GPIO.output(LCD_D6, True)
    if bits&0x80==0x80:
        GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
    lcd_toggle_enable()
 
  # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x01==0x01:
        GPIO.output(LCD_D4, True)
    if bits&0x02==0x02:
        GPIO.output(LCD_D5, True)
    if bits&0x04==0x04:
        GPIO.output(LCD_D6, True)
    if bits&0x08==0x08:
        GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
    lcd_toggle_enable()
 
def lcd_toggle_enable():
  # Toggle enable
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)
 
def lcd_string(message,line):
  # Send string to display
    message = message.ljust(LCD_WIDTH," ")
 
    lcd_byte(line, LCD_CMD)
 
    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]),LCD_CHR)
if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            GPIO.output(LED,GPIO.LOW)
            print("Reading Stopped")
GPIO.cleanup()
