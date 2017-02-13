#Ensure that KISYSMOD is set, on ubuntu standard install use KISYSMOD=/usr/share/kicad/modules

#First we set some vars to effect output.
# a full 104 key board can be done with x = 13, y = 8, so this should be enough
# of course you will have to place them all by hand in the PCB editor, have fun if you go that high
keys_x = 2	#Number of columns of keys on the device, max 14
keys_y = 2	#Number of rows of keys on the device, max 8

#Let's start with getting the SKiDL library
from skidl import *
from os.path import dirname, realpath, sep

#We need to import the kicad libraries we have as git submodules
keyboardParts_lib = dirname(realpath(__file__)) + sep + 'kicad-libraries/kicad_lib_tmk/keyboard_parts.lib'

#Set the vars for the foorprints
#allows for each change later(ie I will probably want throughhole if I build one)
fp_r = 'Resistors_SMD:R_0805_HandSoldering'
fp_c = 'Capacitors_SMD:C_0805_HandSoldering'
fp_d = 'Diodes_SMD:D_SOD-323_HandSoldering'
fp_mcu = 'Housings_QFP:TQFP-44_10x10mm_Pitch0.8mm'
fp_x = 'Crystals:Crystal_SMD_0603-2pin_6.0x3.5mm_HandSoldering'			
fp_sw = 'Buttons_Switches_SMD:SW_SPST_PTS645'
fp_usb = 'keyboard_parts:USB_miniB_hirose_5S8'

#From the skidl docs we will create some templates, edited to not do the footprints yet, but those will be added
res = Part('device', 'R', dest=TEMPLATE, footprint=fp_r)
cap = Part('device', 'C', dest=TEMPLATE, footprint=fp_c)
dio = Part('device', 'D', dest=TEMPLATE, footprint=fp_d)
key = Part(keyboardParts_lib, '\~KEYSW', dest=TEMPLATE, footprint='httpstr:Mx_Alps_100') #only one footprint on this, so no options

#create the global nets up gront
gnd = Net('GND')
gnd.drive = POWER
vcc = Net('+5V')
vcc.drive = POWER

#The first component from the howto is the ATMEGA32U4, let's add that
atmega = Part('atmel', 'ATmega32U4', footprint=fp_mcu)
atmega[:] += NC	#we connect all the pins to the NC net, which is overwritten if we use the pin

#add in the timing circuit
crystal = Part(keyboardParts_lib, 'XTAL_GND', footprint=fp_x)
crystal_decouple = cap(2, value='22pf')
#connect these all up
crystal[1,2,3] += atmega['XTAL1', 'XTAL2'], gnd
crystal.ref = 'X1'
crystal_decouple[0][1,2] += crystal[1], gnd
crystal_decouple[1][1,2] += crystal[2], gnd

#Add in the decoupling caps for VCC
vcc_decouple = cap(5, value='0.1uf')
vcc_decouple[4].value = '4.7uf'	#just to keep it in the array, we tweak just the one
#link all them up to the power and ground
for i in range(0,5):
	vcc_decouple[i][1,2] += vcc, gnd

#Now we wire up the reset switch
reset_res = res(2, value='10K')
reset_sw = Part('device', 'SW_PUSH', footprint=fp_sw)
reset_res[0][1,2] += vcc, atmega['RESET']
reset_sw[1,2] += gnd, atmega['RESET']
#this one is used to go into the bootloader on Reset
reset_res[1][1,2] += gnd, atmega[33]	#I use the number here because the name sucks for this

#Add a USB port
usb_conn = Part(keyboardParts_lib, '\~USB_mini_micro_B', footprint=fp_usb)
usb_res = res(2, value='22')
usb_cap = cap(value='1uf')
#connect it all up
usb_conn['VUSB'] += vcc, atmega['UVCC']
usb_res[0][1,2] += usb_conn['D-'], atmega['D-']
usb_res[1][1,2] += usb_conn['D\+'], atmega['D\+']
usb_conn['ID'] += NC	#not connected
usb_conn['GND', 'shield'] += gnd
atmega['UGND'] += gnd
usb_cap[1,2] += gnd, atmega['UCAP']

#Wire up all the VCC or Gnd and related on the processor
atmega['VBUS', 'VCC', 'AVCC'] += vcc
atmega['GND'] += gnd	#this will select all 'GND' pins


#Keyboard keys
keys = [None] * keys_x
keys_dio = [None] * keys_x
for i in range(0, keys_x):
	#We create a pair of two dimensional arrays of key switches and diodes for the keybaord
	keys[i] = key(keys_y)
	keys_dio[i] = dio(keys_y)
drive = Bus('KEY_Drive', keys_x)	#Create the nets in a bus for the drive side
drain = Bus('KEY_Drain', keys_y)	#Create the nets in a bus for the drain side
for ix in range(0, keys_x):
	for iy in range(0, keys_y):
		keys[ix][iy][2] += keys_dio[ix][iy][2]	#Hook the diodes up to the keys
		keys[ix][iy][1] += drive[ix]		#Hook up the drive bus to the keys input
		keys_dio[ix][iy][1] += drain[iy]	#Hook up the drain to the other end of the diode

		#the library is sub optimal on the key names, fix that here
		keys[ix][iy].ref = 'K' + str((ix * keys_y) + iy + 1)

#In a slight change from the tutorial source, I will be connecting the drive(col) to PB? and drain(row) to PD?
#It allows us to grow the keyboard up to 8 x 8 = 64 keys in this code
for ix in range(0, keys_x):
	if ix < 8:
		#First 8 go to port B (PB#)
		drive[ix] += atmega['.*PB' + str(ix) + '.*']
	elif ix < 10:
		#Next 2 go to port F 0,1
		drive[ix] += atmega['.*PF' + str(ix - 8) + '.*']
	else:
		#Since there is no port F 2,3 we have to skip to port F 4
		drive[ix] += atmega['.*PF' + str(ix - 6) + '.*']
for iy in range(0, keys_y):
	#we only go to 8 because this way we can read all 8 bits of port D at once and process from there
	drain[iy] += atmega['.*PD' + str(iy) + '.*']

#test it
ERC()			#outputs to 'progname.erc' file

#print it out
generate_netlist()	#outputs to 'progname.net' file

