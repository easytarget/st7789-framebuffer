# HOI!
# YOU MUST UNCOMMENT ONE (and only one..) OF THE DRIVERS BELOW:

#import st7789_purefb as st7789
#import st7789_fb_plus as st7789

"""
    st7789 framebuffer driver demo for ST7789 SPI displays
    https://github.com/easytarget/st7789-framebuffer
"""

from machine import Pin, PWM, SPI

"""
    Before running copy the entire /demo_extra folder to your device root

    This demo defaults to Pin and Display settings for the LilyGo T-Watch 2020 (v3)
    You will need to adjust the pins and dimensions as necesscary for your project.
"""

# All the pins below are defaults for T-Watch 2020 v3
# Adjust to suit your hardware

display_cs_pin        = Pin(5,  Pin.OUT, value = 1)
display_dc_pin        = Pin(27, Pin.OUT, value = 1)
display_reset_pin     = None

display_backlight_pin = Pin(15, Pin.OUT, value = 0)
display_backlight_pwm = PWM(display_backlight_pin,
                            duty_u16 = int(0x0))

"""
    T-Watch 2020 specific:
    - On this hardware you must enable and set an external Power Manager Unit to
      provide screen power.
    - T-Watch users need to uncomment this section.
      Everybody else can ignore or delete it as needed
"""
#from sys import path
#path.append('demo_extra')
#import axp202c
#axp = axp202c.PMU()
#axp.enablePower(axp202c.AXP202_LDO2)
#axp.setLDO2Voltage(2950)   # low=2600, mid=2950, high=3300

display = st7789.ST7789_SPI(
    SPI(2,   # using hardware SPI#2 on esp32, adjust/remove as needed
        baudrate=30000000,
        sck=Pin(18),
        mosi=Pin(19),
        miso=None),
    width = 240,
    height = 240,
    reset = display_reset_pin,
    cs = display_cs_pin,
    dc = display_dc_pin,
    backlight = display_backlight_pwm,
    rotation = 2,
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
    # color helper
    color565 = st7789.color565
    swap_bytes = st7789.swap_bytes

print('init done, running demo')
from demo_extra import run_demo
run_demo(display, palette)
