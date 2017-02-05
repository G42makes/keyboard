#Ensure that KISYSMOD is set, on ubuntu standard install use KISYSMOD=/usr/share/kicad/modules
#Let's start with getting the SKiDL library
from skidl import *
from os.path import dirname, realpath, sep

#We need to import the kicad libraries we have as git submodules
#skidl.lib_search_paths_kicad.append(u'./kicad-libraries/kicad_lib_tmk/')
keyboardParts_lib = dirname(realpath(__file__)) + sep + 'kicad-libraries/kicad_lib_tmk/keyboard_parts.lib'

#From the skidl docs we will create some templates, edited to not do the footprints yet, but those will be added
res = Part('device', 'R', dest=TEMPLATE, footprint='Resistors_SMD:R_0805')
cap = Part('device', 'C', dest=TEMPLATE, footprint='Capacitors_SMD:C_0805')
dio = Part('device', 'D', dest=TEMPLATE, footprint='keyboard_parts:D_SOD123_axial')
key = Part(keyboardParts_lib, '\~KEYSW', dest=TEMPLATE, footprint='httpstr:Mx_Alps_100')

#We create a function to return a button with diode
#@SubCircuit
#def keyboard_key():
	

#create the global nets up gront
gnd = Net('GND')
gnd.drive = POWER
vcc = Net('+5V')
vcc.drive = POWER

#The first component from the howto is the ATMEGA32U4, let's add that
atmega = Part('atmel', 'ATmega32U4', footprint='Housings_QFP:TQFP-44_10x10mm_Pitch0.8mm')
atmega[:] += NC	#we connect all the pins to the NC net, which is overwritten if we use the pin

#add in the timing circuit
crystal = Part(keyboardParts_lib, 'XTAL_GND', footprint='Crystals:crystal_FA238-TSX3225')
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
reset_sw = Part('device', 'SW_PUSH', footprint='Buttons_Switches_SMD:SW_SPST_PTS645')
reset_res[0][1,2] += vcc, atmega['RESET']
reset_sw[1,2] += gnd, atmega['RESET']
#this one is used to go into the bootloader on Reset
reset_res[1][1,2] += gnd, atmega[33]	#I use the number here because the name sucks for this

#Add a USB port
usb_conn = Part(keyboardParts_lib, '\~USB_mini_micro_B', footprint='keyboard_parts:USB_miniB_hirose_5S8')
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


#We start into the 4 keys for this version
#TODO: generalize this to any size
x = 2
y = 2
keys = [None] * x
keys_dio = [None] * x
for i in range(0, x):
	#We create a pair of two dimensional arrays of key switches and diodes for the keybaord
	keys[i] = key(y)
	keys_dio[i] = dio(y)
drive = Bus('KEY_Drive', x)	#Create the nets in a bus for the drive side
drain = Bus('KEY_Drain', y)	#Create the nets in a bus for the drain side
for ix in range(0, x):
	for iy in range(0, y):
		keys[ix][iy][2] += keys_dio[ix][iy][2]	#Hook the diodes up to the keys
		keys[ix][iy][1] += drive[ix]		#Hook up the drive bus to the keys input
		keys_dio[ix][iy][1] += drain[iy]	#Hook up the drain to the other end of the diode

		#the library is sub optimal on the key names, fix that here
		keys[ix][iy].ref = 'K' + str((ix * y) + iy + 1)

#In a slight change from the tutorial source, I will be connecting the drive(col) to PB? and drain(row) to PD?
#It allows us to grow the keyboard up to 8 x 8 = 64 keys in this code
for ix in range(0, x):
	drive[ix] += atmega['.*PB' + str(ix) + '.*']
for iy in range(0, y):
	drain[iy] += atmega['.*PD' + str(iy) + '.*']






#test it
ERC()

#print it out
generate_netlist()

