LiFi Laser Communication Simulation

A real-time 2D simulation (built with Python + Pygame) demonstrating Beam-steering mechanism of Laser LiFi device. 
The program simulates:
A Transmitter (TX) projecting laser onto a Beam Splitter.
A Beam Splitter scanning until it locks onto the Receiver (RX).
A Secondary Receiver (RX2) receiving a direct beam.
Beam alignment, link acquisition, and 8-bit data display.
Interactive receiver motion & dynamic beam tracing.

Requirements:
Python 3.8.x
Pygame
Install Pygame with:
	pip install pygame

Run:
Open LifiSim.py
Click Run
Enter your 8-bit Binary Digits (11001001)
Use Arrow Keys to move the receiver and display pair around the screen.  
Press ESC to quit Simulation. 

Controls:
Keys			Action
0/1			Add 8-binary digits for input
Backspace		Delete last bit
Arrow keys 		Move the Receiver Rx around the screen
ESC			Close Simulation

 
Simulation Logic:
Transmitter (TX): Transmits signal onto the Beam Splitter
Status switches to Splitter: FOUND

Beam Splitter
Once TX→Splitter link is established:
It begins scanning for the Receiver (RX)
When RX is found:  Beam turns green
Status switches to Beam-Receiver: FOUND

Receivers
RX (Main Receiver): Can be moved using arrow keys across the screen. 
Displays the 8-bit input when aligned & link is locked
RX2 (Direct Receiver): Receives direct beam from TX
Displays 8-bit input if TX hits it directly

On Screen you can also see the devices Position and Status.

References: pygame documentaries

No receiver displayed: Program has been set to 8-bits. So, 8 exact digits need to be entered. 

Future Extension: Will develop for multiples of 8, i.e, 8,16,32, etc in one go.


Contributors: Roemen Edwards, Scott Selke, Chris Eugene 