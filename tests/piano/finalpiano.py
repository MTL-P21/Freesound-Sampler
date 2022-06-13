
import os
import sys

# Hide welcome message from pygame when importing (seriously, who does that?)
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    import pygame.midi


# Colors for keys and background
color_grey = (127, 127, 127)
color_white = (255, 255, 255)
color_black = (0, 0, 0)
color_red = (255, 0, 0)
color_blue = (0, 0, 255)


key_to_note = {
        # pygame_key_id: (pitch, black, on)
        # pygame_key_id: pygame's internal constant to represent a key
        # pitch: the pitch of this note (on the octave 0) --> not used
        # black: a boolean to know if the key is black or white
        # on: a boolean to keep track of if this note is on

        #1st octave
        pygame.K_q: (12, False, False),  # C0
        pygame.K_2: (13, True, False),  # C#/Db0
        pygame.K_w: (14, False, False),  # D0
        pygame.K_3: (15, True, False),  # D#/Eb0
        pygame.K_e: (16, False, False),  # E0
        pygame.K_r: (17, False, False),  # F0
        pygame.K_5: (18, True, False),  # F#/Gb0
        pygame.K_t: (19, False, False),  # G0
        pygame.K_6: (20, True, False),  # G#/Ab0
        pygame.K_y: (21, False, False),  # A0
        pygame.K_7: (22, True, False),  # A#/Bb0
        pygame.K_u: (23, False, False),  # B0

        #2nd octave
        pygame.K_z: (24, False, False),  # C1
        pygame.K_s: (25, True, False),  # C#/Db1
        pygame.K_x: (26, False, False),  # D1
        pygame.K_d: (27, True, False),  # D#/Eb1
        pygame.K_c: (28, False, False),  # E1
        pygame.K_v: (29, False, False),  # F1
        pygame.K_g: (30, True, False),  # F#/Gb1
        pygame.K_b: (31, False, False),  # G1
        pygame.K_h: (32, True, False),  # G#/Ab1
        pygame.K_n: (33, False, False),  # A1
        pygame.K_j: (34, True, False),  # A#/Bb1
        pygame.K_m: (35, False, False),  # B1
}

def draw_keyboard(window) -> None:
    '''Draw the octave keyboard on screen'''

    window_width = 600 #window.get_width()
    window_height = 350 #window.get_height()

    margin = window_width // 140

    white_width = (window_width - 8 * margin) // 7
    black_width = white_width // 2 + 2 * margin

    left = margin
    top = margin
    bottom = window_height - top

    # Draw white keys
    for key in key_to_note:
        note, black, on = key_to_note[key]
        if black:
            continue
        pygame.draw.rect(window, color_red if on else color_white, (left, top, white_width, bottom - top))
        left += margin + white_width

    # Reset left for black keys
    left = margin + white_width + margin // 2 - black_width // 2

    bottom = bottom - (bottom - top) // 3

    # Draw black keys
    for key in key_to_note:
        note, black, on = key_to_note[key]
        if not black:
            continue
        if note == 18 or note == 25 or note == 30:  # Skip the inexistant black keys
            left += margin + white_width
        pygame.draw.rect(window, color_blue if on else color_black, (left, top, black_width, bottom - top))
        left += margin + white_width

def main() -> None:
    '''The main entrypoint for our program'''
    pygame.display.init()
    window = pygame.display.set_mode((1280, 720))
    window.fill(color_grey)
    draw_keyboard(window)
    pygame.display.update()

    # We only want to get events for our keyboard -> other events disabled
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.KEYUP])

    # Our main loop which gets pressed keys, plays or stops notes and updates the display
    go_on = True
    while go_on:
        for event in pygame.event.get():

            # Turn note on if known key
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key in key_to_note:
                    note, black, on = key_to_note[key]
                    if not on:
                        key_to_note[key] = note, black, True

                # Exit is user pressed <escape>
                elif key == pygame.K_ESCAPE:
                    go_on = False

            # Turn note off if known key
            elif event.type == pygame.KEYUP:
                key = event.key
                if key in key_to_note:
                    note, black, on = key_to_note[key]
                    if on:
                        key_to_note[key] = note, black, False

        draw_keyboard(window)
        pygame.display.update()

if __name__ == '__main__':
    main()