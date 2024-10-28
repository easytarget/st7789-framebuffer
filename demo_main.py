# Main demo code
# assumes 'display' and 'pallette' were created by the invoker.

from sys import path, implementation
from machine import Pin
import random

path.append('demofonts')
from ezFBfont import ezFBfont
import ezFBfont_23_spleen_12x24_ascii as promptfont
import ezFBfont_17_helvR12_ascii as consolefont

def do_demo(display, palette):
    display.fill(palette.BLACK)
    display.show()

    # GPIO-0 is found as the 'boot' button on most devboards 
    button = Pin(0, Pin.IN)

    while button.value() != 0:
        color = palette.color565(
            random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
        )

        display.line(
            random.randint(0, display.width),
            random.randint(0, display.height),
            random.randint(0, display.width),
            random.randint(0, display.height),
            color,
        )

        width = random.randint(0, display.width // 2)
        height = random.randint(0, display.height // 2)
        col = random.randint(0, display.width - width)
        row = random.randint(0, display.height - height)
        display.fill_rect(
            col,
            row,
            width,
            height,
            palette.color565(
                random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)
            ),
        )
        display.show()

    display.fill(palette.BLACK)
    prompt = ezFBfont(display, promptfont, fg = palette.swap_bytes(palette.WHITE))
    cons = ezFBfont(display, consolefont, fg = palette.swap_bytes(palette.SILVER))

    ver = '{}.{}.{}'.format(*implementation.version)
    prompt.write('LillyGo T-Display Touch', 5, 5)
    cons.write('ESP32-S3\nMicropython: {}\n>>> _'.format(ver), 5, 35)
    display.show()
