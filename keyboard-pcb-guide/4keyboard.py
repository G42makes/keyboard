#Ensure that KISYSMOD is set, on ubuntu standard install use KISYSMOD=/usr/share/kicad/modules
#Let's start with getting the SKiDL library
from skidl import *

#From the skidl docs we will create some templates, edited to not do the footprints yet, but those will be added
res = Part('device', 'R', dest=TEMPLATE)
cap = Part('device', 'C', dest=TEMPLATE)

#create the global nets up gront
gnd = Net('GND')
gnd.drive = POWER
vcc = Net('+5V')
vcc.drive = POWER

#We need to import the kicad libraries we have as git submodules
skidl.lib_search_paths_kicad.append(u'./kicad-libraries/kicad_lib_tmk/')
#keyboardParts_lib = r'./kicad-libraries/kicad_lib_tmk/keyboard_parts.lib'

#The first component from the howto is the ATMEGA32U4, let's add that
atmega = Part('atmel', 'ATmega32U4')	#TODO footprint

#add in the timing circuit
crystal = Part('device', 'Crystal')
crystal_decouple = cap(2, value='22pf')
#connect these all up
crystal[1,2] += atmega['XTAL1', 'XTAL2']
crystal.ref = 'X1'
crystal_decouple[0][1,2] += crystal[1], gnd
crystal_decouple[1][1,2] += crystal[2], gnd

#Add in the decoupling caps for VCC
vcc_decouple = cap(5, value='0.1uf')
vcc_decouple[4].value = '4.7uf'	#just to keep it in the array, we tweak just the one
#link all them up to the power and ground
for i in range(0,4):
	vcc_decouple[i][1,2] += vcc, gnd

#Now we wire up the reset switch
reset_res = res(2, value='10K')
reset_sw = Part('device', 'SW_PUSH')
reset_res[0][1,2] += vcc, atmega['RESET']
reset_sw[1,2] += gnd, atmega['RESET']
#this one is used to go into the bootloader on Reset
reset_res[1][1,2] += gnd, atmega[33]	#I use the number here because the name sucks for this

#Add a USB port
usb_conn = Part('conn', 'USB_OTG')
usb_res = res(2, value='22')
usb_cap = cap(value='1uf')
#connect it all up
usb_conn['VCC'] += vcc, atmega['UVCC']
usb_res[0][1,2] += usb_conn['D-'], atmega['D-']
usb_res[1][1,2] += usb_conn['D\+'], atmega['D\+']
usb_conn['ID'] += NC	#not connected
usb_conn['GND', 'shield'] += gnd
atmega['UGND'] += gnd
usb_cap[1,2] += gnd, atmega['UCAP']

#Wire up all the VCC or Gnd and related on the processor
atmega['VBUS', 'VCC', 'AVCC'] += vcc
atmega['GND'] += gnd	#this will select all 'GND' pins










#print it out
generate_netlist(sys.stdout)

