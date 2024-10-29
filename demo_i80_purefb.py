import st7789_purefb as st7789
from machine import Pin, PWM
from i80bus import I80Bus

"""
    This demo defaults to Pin and Display settings for the LilyGo T-Display Touch
    You will need to adjust the pins and dimensions as necesscary for your project.
"""

display_reset_pin     = Pin(5,  Pin.OUT, value = 1)

display_backlight_pin = Pin(38, Pin.OUT, value = 0)
display_backlight_pwm = PWM(display_backlight_pin,
                           freq = 5000, duty_u16 = int(0x0))

display = st7789.ST7789_I80(
    I80Bus(  # I80 bus takes pin numbers, not objects
        dc=7,
        cs=6,
        wr=8,
        data=[39, 40, 41, 42, 45, 46, 47, 48]),
    width = 170,
    height = 320,
    reset = display_reset_pin,
    backlight = display_backlight_pwm,
    rotation = 3,
    swap_bytes = True
)

# An example 'palette' class with 20 colors and helper
class palette():
    # color definitions
    BLACK    = 0x0000
    DARKGREY = 0x4208
    NAVY     = 0x0010
    BLUE     = 0x001f
    GREEN    = 0x0400
    TEAL     = 0x0410
    AZURE    = 0x041f
    LIME     = 0x07e0
    CYAN     = 0x07ff
    MAROON   = 0x8000
    PURPLE   = 0x8010
    OLIVE    = 0x8400
    GREY     = 0x8410
    SILVER   = 0xc618
    RED      = 0xf800
    ROSE     = 0xf810
    MAGENTA  = 0xf81f
    ORANGE   = 0xfc00
    YELLOW   = 0xffe0
    WHITE    = 0xffff
    # color helpers
    color565 = st7789.color565
    swap_bytes = st7789.swap_bytes

print('init done, running demo')
from demo_main import do_demo
do_demo(display, palette)
