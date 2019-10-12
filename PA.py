#use this script at your own risk
#this script is designed for klipper, but can probably be easily modified for other firmwares
#this script generates gcode for a square that has features and speed changes to help calibrate pressure advance values
#this script does not include any commands for a heated bed, but they can be added easily, just add the print(M140 S(bed_temp_goes_here)) and print(M190 S(bed_temp_goes_here)) commands to the start of the code on seperate lines

#to use this script on windows, download and install python, 
#use control panel to navigate to "Control Panel\System and Security\System", click "advanced system settings",
#in the new window, find and click on "enviromental variables", under "system variables" click on "path", click "edit",
#click "new", paste in your file path to your python installation (eg: "C:\Users\your_username\AppData\Local\Programs\Python\Python37-32")
#click "ok"
#after you have modified the parameters in this script to your liking and saved your changes,
#open command prompt, navigate to the directory where this script is saved on your drive using a cd command,
#type in "python PA.py > PAtestsquare.gcode", this will output a gcode file in the same directory, happy printing!

#it's a good idea to preview your gcode in a slicer before attempting to print
#this script assumes your (0,0) coordinate is the corner of a square bed

#after printing, use calipers to find the z height where your print looks best and most consistant all around
#use this z height to calculate your best pressure advance value (your measured z height should be a multiple of your layer height)
#your best pressure advance value=((measured_z_height/layer_height)-2)*((PA_max/PA_min)/(number_of_layers))
#add this calculated value to your firmware config or into your start gcode if you have that set up for different materials

#modify these following parameters to match your printer and desired settings. units are (mm or mm/s or degrees Celcius just standard stuff)
bed_x_length=235
bed_y_length=205
extrusion_width=0.4 
layer_height=0.3 
filament_diameter=1.75 
print_temp=190
travel_speed=150
slow_print_speed=15
fast_print_speed=120
cooling_fan_speed=51 # pwm value 0 to 255
rectangle_side_length=50 #make sure a square with this side length fits in the center of your print bed
layers=60 #number of layers (this does not include the initial layer or the two finishing layers) total z height will be: (layer_height*layers+(3*layer_height))
PA_min=0.00 #minimum pressure advance value
PA_max=0.1 #maximum pressure advance value
#end of parameter set

print("M104 S%.3f" % print_temp)
print("M109 S%.3f" % print_temp)

#start gcode goes here. this start code is pretty standard, it includes a very small prime strip. only modify if you know what you're doing
print('M220 S100\n\
M221 S100\n\
G28\n\
G92 E0\n\
G1 X1 Y1\n\
G1 Y40 E10 F500\n\
G92 E0\n\
G1 E-1 F500\n\
G1 Y80 F4000\n\
G1 Z2.0 F3000\n\
SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=1 ACCEL=500\n\
SET_PRESSURE_ADVANCE ADVANCE_LOOKAHEAD_TIME=0')
#end of start gcode

print('M82\n\
G92 E0') #enable absolute extrusion mode

from math import *

#the following two functions control extrusion
def extrusion_volume_to_length(volume):
    return volume / (filament_diameter * filament_diameter * 3.14159 * 0.25)

def extrusion_for_length(length):
    return extrusion_volume_to_length(length * extrusion_width * layer_height)

#these values are used to keep track of current xyz coordinates	and extruded length
current_x=((bed_x_length / 2)-(rectangle_side_length / 2))
current_y=((bed_y_length / 2)-(rectangle_side_length / 2))
current_z=layer_height
current_e=0

#move the printhead to the starting position and prime nozzle
print("G1 X%.3f Y%.3f Z%.3f E1.0 F%.0f" % (current_x, current_y, current_z, travel_speed * 60))

#when called, this function moves the z axis up
def move_up():
    global current_z
    current_z += layer_height
    print("G1 Z%.3f" % current_z)

#when called this function generates the gcode for a line segment using an x length, a y length, and a speed variable	
def line(x,y,speed):
	length = sqrt(x**2 + y**2)
	global current_x, current_y, current_e
	current_x += x
	current_y += y
	current_e += extrusion_for_length(length)
	print("G1 X%.3f Y%.3f E%.4f F%.0f" % (current_x, current_y, current_e, speed * 60))

#print first layer without cooling fan and without pressure advance at 20mm/s for better adhesion
pressure_advance=0
print("SET_PRESSURE_ADVANCE ADVANCE=%.4f" % pressure_advance)
line(rectangle_side_length,0,20)
line(0,rectangle_side_length / 2,20)
line(0,rectangle_side_length / 2,20)
line(-rectangle_side_length,0,20)
line(0,-rectangle_side_length,20)
move_up()

#start cooling fan		
print("M106 S%.3f" % cooling_fan_speed)

#below code generates the gcode for the rectangle 
for i in range(layers):
	pressure_advance = (i / layers) * (PA_max-PA_min) + PA_min;
	print("SET_PRESSURE_ADVANCE ADVANCE=%.4f" % pressure_advance)
	line(rectangle_side_length,0,fast_print_speed)
	line(0,rectangle_side_length / 2,fast_print_speed)
	line(0,rectangle_side_length / 2,slow_print_speed)
	line(-rectangle_side_length,0,fast_print_speed)
	line(0,-rectangle_side_length,slow_print_speed)
	move_up()

#print two finishing layers	at PA_MAX
pressure_advance = PA_max
print("SET_PRESSURE_ADVANCE ADVANCE=%.4f" % pressure_advance)
line(rectangle_side_length,0,fast_print_speed)
line(0,rectangle_side_length / 2,fast_print_speed)
line(0,rectangle_side_length / 2,slow_print_speed)
line(-rectangle_side_length,0,fast_print_speed)
line(0,-rectangle_side_length,slow_print_speed)
move_up()
line(rectangle_side_length,0,fast_print_speed)
line(0,rectangle_side_length / 2,fast_print_speed)
line(0,rectangle_side_length / 2,slow_print_speed)
line(-rectangle_side_length,0,fast_print_speed)
line(0,-rectangle_side_length,slow_print_speed)

#ending gcode goes here (just moves the nozzzle up a bit and turns everything off)
print('G91\n\
G1 Z10 F450\n\
G90\n\
M106 S0\n\
M104 S0\n\
M140 S0\n\
M84')
