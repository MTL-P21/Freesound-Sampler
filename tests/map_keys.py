import mido
import keyboard

outport = mido.open_output()
space_pressed = False

while True:
    if keyboard.is_pressed("space") and not space_pressed:
        msg = mido.Message("note_on", note=50, velocity=100, time=10)
        outport.send(msg)
        space_pressed = True
        print("True press")
    elif (keyboard.is_pressed("space") == False):
        msg = mido.Message("note_off", note=50, velocity=100, time=10)
        outport.send(msg)
        space_pressed = False
        print("False press")


