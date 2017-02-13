# 4 Key Board

As a test of using [SKiDL](https://xesscorp.github.io/skidl/docs/_site/index.html) for editing schematics and generating netlists, I wanted to create a small keyboard. I had come across the [Keyboard PCB Guite](https://github.com/ruiqimao/keyboard-pcb-guide) in my reasearch, and since it was very simple and used KiCAD for the work as well, I felt it would be a good match for the two to come together. 

## 4keyboard.py
This is the only really interesting file. It will generate a keyboard netlist file you can pull into KiCAD and with a litte tweaking build a PCB. I have been successfull with the layout, but am yet to make an actual board. The file has only 2 options: the X and Y sizes of the array used to drive/read the keys. The reading is intentionally limited to 8 lines so you can read a byte at a time on the MCU. The X can go up to 14 in this code, but of course a few tweaks could increase either of these. 112 keys is enough for what I need right now, but if I need to I can get 4 more lines(I would put them on the X side, driving me up to 144 keys. Optimally you would have X and Y either equal or within 1 of each other. Maxing out at 13 by 13, giving 169 on this processor).

Running the script, you may get an error about "WARNING:root:KISYSMOD environment variable is missing, so default KiCad libraries won't be searched." or similar. To avoid this you will need to either set the environment variable mentioned(google it) or just set it on every run as below(specific to Ubuntu with the package install of KiCAD):
```KISYSMOD=/usr/share/kicad/modules python 4keyboard.py```

## kicad-libraries
This folder contains some [git submodules](https://github.com/blog/2104-working-with-submodules), after checking out this repo, if the files are not there, just run:
```git submodule update --init --recursive```
Luckily most new versions of git should take care of this for you.

The 4keyboard.py script needs to generate absolute paths to these files, so your netlists will come out refering to this location.

## Importing
Once the .net file is generated, you need to get it into KiCAD and move the components around. The Keyboard tutorial has excellent instructions that work with this netlist starting in the [PCB](https://github.com/ruiqimao/keyboard-pcb-guide#pcb) section. Please follow that to get a working PCB.

## TODO
* Choice of footprints for the components. I'm more comfortable with through hole.
* Figure out [SubCircuit](https://xesscorp.github.io/skidl/docs/_site/index.html#going-deeper)s. I would like to make the keyboard and keys into functions.
* Get it manufactured. The ultimate test of the code is if it makes a working component.
