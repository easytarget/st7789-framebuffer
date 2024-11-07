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
from sys import path, argv
from time import sleep, ticks_ms

# Interrupt timer
from machine import Timer
from micropython import schedule

# fonts
path.append('demo_extra')
from ezFBmarquee import ezFBmarquee
from ezFBfont import ezFBfont
import ezFBfont_17_helvR12_ascii as font1
import ezFBfont_23_spleen_12x24_ascii as font2
import ezFBfont_7_Seg_41x21_0x0_0x39_37 as font3

'''
A demo of using ezFBmarquee to animate messages

It uses a simple 'as fast as possible' loop for a splashscreen
and then uses an interrupt timer to step marquees in the background

This is a good example to 'play' with, try changing fonts,
adding/removing options etc.
'''

# I80
from machine import Pin, PWM
from i80bus import I80Bus
"""
    This demo defaults to Pin and Display settings for the LilyGo T-Display Touch
    You will need to adjust the pins and dimensions as necesscary for your project.
"""

# Power and RD pins not used but need setting to correct values
display_power_pin     = Pin(15, Pin.OUT, value = 1)
display_rd_pin        = Pin(9,  Pin.OUT, value = 1)
# Pins used by the driver
display_reset_pin     = Pin(5,  Pin.OUT, value = 1)
display_backlight_pin = Pin(38, Pin.OUT, value = 0)
display_backlight_pwm = PWM(display_backlight_pin,
                           freq = 1000, duty_u16 = int(0x0))

display = st7789.ST7789_I80(
    I80Bus(  # I80 bus takes integer pin numbers, not objects
        dc=7,
        cs=6,
        wr=8,
        data=[39, 40, 41, 42, 45, 46, 47, 48]),
    width = 170,
    height = 320,
    reset = display_reset_pin,
    backlight = display_backlight_pwm,
    rotation = 3,
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



# two marquees
marquee1 = ezFBmarquee(display, font1, x=10, y=0, width=300, fg=palette.SILVER, cswap=True, verbose=True)
marquee2 = ezFBmarquee(display, font2, x=100, y=110, width=120, mode='scroller', hgap=0, fg=palette.CYAN, cswap=True, verbose=True)
bigseven   = ezFBfont(display, font3, halign='center', valign='baseline', fg=palette.AZURE, cswap=True)

# Timer interrupt to step both marquees
def mstep(t):
    def uptime():
        s = int(ticks_ms()/1000 % 60)
        m = int(ticks_ms()/60000 % 60)
        display.rect(100,40,120,60,0,True)
        bigseven.write('{:02d}:{:02d}'.format(m,s),160,88)

    # step marquee1 and add a pause whenever it rolls over
    if marquee1.step(4):
        marquee1.pause(20)
    # step marquee2 and stop when complete
    if marquee2.step(10):
        marquee2.stop()
    # add the uptime
    uptime()
    # Display results
    display.show()

# Start the timer
tim0 = Timer(0)
tim0.init(period=100, mode=Timer.PERIODIC, callback=mstep)

# Start the main marquee
message = 'Info: This is a a long & boring informational message! [with ~{:d} chars]'
marquee1.start(message.format(len(message)), pause=20)

# A box around the uptime count
display.rect(99,39,122,62,palette.NAVY)

# Loop forever, starting the lower marquee at set times
tens = {0:'zero', 10:'ten', 20:'twenty', 30:'thirty', 40:'fourty', 50:'fifty'}
while True:
    # start scrollbox on time based events
    secs = int(ticks_ms()/1000 % 60)
    if secs in tens.keys() and not marquee2.active():
        marquee2.start(tens[secs])
