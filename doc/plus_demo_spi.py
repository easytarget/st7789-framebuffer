"""
 HOI!
 YOU MUST UNCOMMENT ONE (and only one..) OF THE DRIVERS BELOW:

 ALSO:
 The fonts for this demo are in the 'doc/plusfonts' folder; copy them to
 the 'demo_extra' folder before using this demo.
"""

#import st7789_purefb as st7789
#import st7789_fb_plus as st7789

"""
    st7789 framebuffer driver demo for ST7789 SPI displays
    https://github.com/easytarget/st7789-framebuffer
"""

from machine import Pin, PWM, SPI
from time import sleep_ms, localtime
"""
    Before running copy the entire ./demo_extra folder to your device root

    This demo defaults to Pin and Display settings for a loose SPI display
    connected to a ESP32-C3 on the pins below.
"""

# All the pins below are defaults for T-Watch 2020 v3
# Adjust to suit your hardware

display_cs_pin        = Pin(10,  Pin.OUT, value = 1)
display_dc_pin        = Pin(3, Pin.OUT, value = 1)
display_reset_pin     = Pin(2, Pin.OUT, value = 1)

display_backlight_pin = Pin(1, Pin.OUT, value = 0)
display_backlight_pwm = PWM(display_backlight_pin,
                            duty_u16 = int(0x0))

display = st7789.ST7789_SPI(
    SPI(1,   # using hardware SPI#2 on esp32, adjust/remove as needed
        sck=Pin(6),
        mosi=Pin(7),
        miso=None,
        baudrate=30000000),
    width = 135,
    height = 240,
    cs = display_cs_pin,
    dc = display_dc_pin,
    backlight = display_backlight_pwm,
    rotation = 1,
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
from demo_extra import ezFBfont
# The above import will add ./demo_extra to the path
# we can now import fonts directly from there
import ezFBfont_spleen_32x64_ascii_60 as spleen_f
import ezFBfont_helvR24_ascii_34 as helv_f
import ezFBfont_7_Seg_41x21_0x0_0x39_37 as bigseven_f
import ezFBfont_7_Seg_33x19_0x0_0x39_29 as smallseven_f

# Four fonts, different ways of setting colors
spleen     = ezFBfont(display, spleen_f,
                      fg=palette.WHITE,
                      tkey=0,
                      cswap=True)
helv       = ezFBfont(display, helv_f,
                      fg=palette.color565(0x0,0x40,0x40),
                      bg=palette.TEAL,
                      cswap=True)
bigseven   = ezFBfont(display, bigseven_f,
                      halign='right',
                      valign='baseline',
                      fg=palette.NAVY,
                      bg=palette.ROSE,
                      cswap=True)
smallseven = ezFBfont(display, smallseven_f,
                      halign='left',
                      valign='baseline',
                      fg=palette.DARKGREY,
                      bg=palette.ROSE,
                      cswap=True)

# Crude way of making a rounded background
display.ellipse(20,20,20,20,palette.ROSE,True)
display.ellipse(220,115,20,20,palette.ROSE,True)
display.ellipse(20,115,20,20,palette.ROSE,True)
display.ellipse(220,20,20,20,palette.ROSE,True)
display.rect(20,0,200,135,palette.ROSE,True)
display.rect(0,20,240,95,palette.ROSE,True)

# Some info
spleen.write('Hello', 120, 0, halign='center')
helv.write('     my time is:   ', 120, 55, halign='center')
while True:
    _, _, _, h, m, s, *_ = localtime()
    bigseven.write('{:02d}:{:02d}'.format(h, m), 155, 130)
    smallseven.write(':{:02d}'.format(s), 155, 130)
    display.show()
