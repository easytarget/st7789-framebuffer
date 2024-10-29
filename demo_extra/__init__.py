# Main demo code
# assumes 'display' and 'pallette' were created by the invoker.
# (C) Owen Carter 2024; released 'as-is', no liabaility conceeded

from sys import path, implementation, platform
from machine import Pin
from time import ticks_ms
import random

path.append('demo_extra')
from ezFBfont import ezFBfont
import ezFBfont_23_spleen_12x24_ascii as promptfont
import ezFBfont_17_helvR12_ascii as consolefont

def run_demo(display, palette, runtime=10000):
    display.fill(palette.BLACK)
    display.show()

    # GPIO-0 is found as the 'boot' button on most devboards
    button = Pin(0, Pin.IN)
    button_initial = button.value()

    # default 10 seconds timeout
    end = ticks_ms() + runtime

    print('boxlines')
    while (button.value() == button_initial) and (ticks_ms() <= end):
        color = palette.color565(
            random.getrandbits(8), random.getrandbits(8), random.getrandbits(8))
        display.line(
            random.randint(0, display.width),
            random.randint(0, display.height),
            random.randint(0, display.width),
            random.randint(0, display.height),
            color)
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

    print('prompt')
    display.fill(palette.BLACK)
    prompt = ezFBfont(display, promptfont, fg = palette.swap_bytes(palette.WHITE))
    cons = ezFBfont(display, consolefont, fg = palette.swap_bytes(palette.SILVER))

    plat = platform.upper()
    ver = '{}.{}.{} {}'.format(*implementation.version)

    prompt.write('st7789 framebuffer', 5, 5)
    cons.write('{}\nMicropython: {}\n>>> _'.format(plat, ver), 5, 35)
    display.show()
