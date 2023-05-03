# GuitarTrainer
Digital guitar trainer that plays songs and displays tablature to play along.

The system can detect played notes and score the player accordingly.
There is also an option to change the songs and it's speed in the built-in menu.

Video presentation: https://youtu.be/kuRKiJ4D-AY

## Schematics
Schematic diagram of the whole project:

<img src="https://user-images.githubusercontent.com/71709842/235878086-c1f8072d-81ba-4144-a104-6d718cd4b7e0.png" width="50%" height="50%" />

Detailed diagram:

<img src="https://user-images.githubusercontent.com/71709842/235878659-da55c4bb-5219-4a06-a75f-928675f6f63e.png" width="50%" height="50%" />

## Repository contents
- GuitarTrainer.py - the main program that can be used on Raspberry Pi
- ReadAnalogVoltage.ino - a suplementary code to be used on Arduino (reading signal from a guitar)
- songs - directory with songs in mp3 format and tablature in gtin format
