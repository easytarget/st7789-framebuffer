"""
MIT License

Copyright (c) 2024 Owen Carter
Copyright (c) 2024 Ethan Lacasse
Copyright (c) 2020-2023 Russ Hughes
Copyright (c) 2019 Ivan Belokobylskiy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The driver is based on russhughes' st7789py_mpy module from
https://github.com/russhughes/st7789py_mpy, which is based on
https://github.com/devbis/st7789py_mpy.
"""


import framebuf, struct
from time import sleep_ms

# 7789 direct framebuffer driver

# ST7789 commands
_ST7789_SWRESET = b"\x01"
_ST7789_SLPIN = b"\x10"
_ST7789_SLPOUT = b"\x11"
_ST7789_NORON = b"\x13"
_ST7789_INVOFF = b"\x20"
_ST7789_INVON = b"\x21"
_ST7789_DISPOFF = b"\x28"
_ST7789_DISPON = b"\x29"
_ST7789_CASET = b"\x2a"
_ST7789_RASET = b"\x2b"
_ST7789_RAMWR = b"\x2c"
_ST7789_VSCRDEF = b"\x33"
_ST7789_COLMOD = b"\x3a"
_ST7789_MADCTL = b"\x36"
_ST7789_VSCSAD = b"\x37"
_ST7789_RAMCTL = b"\xb0"

# MADCTL bits
_ST7789_MADCTL_MY = const(0x80)
_ST7789_MADCTL_MX = const(0x40)
_ST7789_MADCTL_MV = const(0x20)
_ST7789_MADCTL_ML = const(0x10)
_ST7789_MADCTL_BGR = const(0x08)
_ST7789_MADCTL_MH = const(0x04)
_ST7789_MADCTL_RGB = const(0x00)

RGB = 0x00
BGR = 0x08

# 8 basic color definitions
BLACK = const(0x0000)
BLUE = const(0x001F)
RED = const(0xF800)
GREEN = const(0x07E0)
CYAN = const(0x07FF)
MAGENTA = const(0xF81F)
YELLOW = const(0xFFE0)
WHITE = const(0xFFFF)

_ENCODE_POS = const(">HH")

_BIT7 = const(0x80)
_BIT6 = const(0x40)
_BIT5 = const(0x20)
_BIT4 = const(0x10)
_BIT3 = const(0x08)
_BIT2 = const(0x04)
_BIT1 = const(0x02)
_BIT0 = const(0x01)

# Rotation tables
#   (madctl, width, height, xstart, ystart)[rotation % 4]

_DISPLAY_240x320 = (
    (0x00, 240, 320, 0, 0),
    (0x60, 320, 240, 0, 0),
    (0xc0, 240, 320, 0, 0),
    (0xa0, 320, 240, 0, 0))

_DISPLAY_170x320 = (
    (0x00, 170, 320, 35, 0),
    (0x60, 320, 170, 0, 35),
    (0xc0, 170, 320, 35, 0),
    (0xa0, 320, 170, 0, 35))

_DISPLAY_240x240 = (
    (0x00, 240, 240,  0,  0),
    (0x60, 240, 240,  0,  0),
    (0xc0, 240, 240,  0, 80),
    (0xa0, 240, 240, 80,  0))

_DISPLAY_135x240 = (
    (0x00, 135, 240, 52, 40),
    (0x60, 240, 135, 40, 53),
    (0xc0, 135, 240, 53, 40),
    (0xa0, 240, 135, 40, 52))

_DISPLAY_128x128 = (
    (0x00, 128, 128, 2, 1),
    (0x60, 128, 128, 1, 2),
    (0xc0, 128, 128, 2, 1),
    (0xa0, 128, 128, 1, 2))

# Supported displays (physical width, physical height, rotation table)
_SUPPORTED_DISPLAYS = (
    (240, 320, _DISPLAY_240x320),
    (170, 320, _DISPLAY_170x320),
    (240, 240, _DISPLAY_240x240),
    (135, 240, _DISPLAY_135x240),
    (128, 128, _DISPLAY_128x128))

# init tuple format (b'command', b'data', delay_ms)
_ST7789_INIT_CMDS = (
    ( b'\x11', b'\x00', 120),               # Exit sleep mode
    ( b'\x13', b'\x00', 0),                 # Turn on the display
    ( b'\xb6', b'\x0a\x82', 0),             # Set display function control
    ( b'\x3a', b'\x55', 10),                # Set pixel format to 16 bits per pixel (RGB565)
    ( b'\xb2', b'\x0c\x0c\x00\x33\x33', 0), # Set porch control
    ( b'\xb7', b'\x35', 0),                 # Set gate control
    ( b'\xbb', b'\x28', 0),                 # Set VCOMS setting
    ( b'\xc0', b'\x0c', 0),                 # Set power control 1
    ( b'\xc2', b'\x01\xff', 0),             # Set power control 2
    ( b'\xc3', b'\x10', 0),                 # Set power control 3
    ( b'\xc4', b'\x20', 0),                 # Set power control 4
    ( b'\xc6', b'\x0f', 0),                 # Set VCOM control 1
    ( b'\xd0', b'\xa4\xa1', 0),             # Set power control A
                                            # Set gamma curve positive polarity
    ( b'\xe0', b'\xd0\x00\x02\x07\x0a\x28\x32\x44\x42\x06\x0e\x12\x14\x17', 0),
                                            # Set gamma curve negative polarity
    ( b'\xe1', b'\xd0\x00\x02\x07\x0a\x28\x31\x54\x47\x0e\x1c\x17\x1b\x1e', 0),
    ( b'\x21', b'\x00', 0),                 # Enable display inversion
    ( b'\x29', b'\x00', 120)                # Turn on the display
)

def color565(red, green=0, blue=0):
    """
    Convert red, green and blue values (0-255) into a 16-bit 565 encoding.
    """
    if isinstance(red, (tuple, list)):
        red, green, blue = red[:3]
    return (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3

def swap_bytes(color):
    """
    Flips the left and right bytes in the 16 bit color word.
    """
    return ((color & 255) << 8) + (color >> 8)


class ST7789(framebuf.FrameBuffer):
    """
    ST7789 driver class base
    """
    def __init__(self, width, height, backlight, bright, rotation, color_order, reverse_bytes_in_word):
        """
        Initialize display and backlight.
        """
        # Initial dimensions and offsets; will be overridden when rotation applied
        self.width = width
        self.height = height
        self.xstart = 0
        self.ystart = 0
        # backlight pin
        self.backlight = backlight
        self._pwm_bl = True
        # Check display is known and get rotation table
        self.rotations = self._find_rotations(width, height)
        if not self.rotations:
            supported_displays = ", ".join(
                [f"{display[0]}x{display[1]}" for display in _SUPPORTED_DISPLAYS])
            raise ValueError(
                f"Unsupported {width}x{height} display. Supported displays: {supported_displays}")
        # Colors
        self.color_order = color_order
        self.needs_swap = reverse_bytes_in_word
        # init the st7789
        self.init_cmds = _ST7789_INIT_CMDS
        self.hard_reset()
        # Yes, send init twice, once is not always enough
        self.send_init(self.init_cmds)
        self.send_init(self.init_cmds)
        # Initial rotation
        self._rotation = rotation % 4
        # Create the framebuffer for the correct rotation
        self.buffer = bytearray(height*width*2)
        if self._rotation % 2 == 0:
            super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        else:
            super().__init__(self.buffer, self.height, self.width, framebuf.RGB565)
        # Apply rotation
        self.rotation(self._rotation)
        # Blank display and turn on backlight
        self.fill(BLACK)
        self.show()
        sleep_ms(150)
        self.brightness(bright)

    def send_init(self, commands):
        """
        Send initialisation commands to display.
        """
        for command, data, delay in commands:
            self._write(command, data)
            sleep_ms(delay)

    def soft_reset(self):
        """
        Soft reset display.
        """
        self._write(_ST7789_SWRESET)
        sleep_ms(150)

    def sleep_mode(self, value):
        """
        Enable or disable display sleep mode.

        Args:
            value (bool): if True enable sleep mode. if False disable sleep
            mode
        """
        if value:
            self._write(_ST7789_SLPIN)
        else:
            self._write(_ST7789_SLPOUT)

    def inversion_mode(self, value):
        """
        Enable or disable display inversion mode.

        Args:
            value (bool): if True enable inversion mode. if False disable
            inversion mode
        """
        if value:
            self._write(_ST7789_INVON)
        else:
            self._write(_ST7789_INVOFF)

    def _find_rotations(self, width, height):
        """ Find the correct rotation for our display or return None """
        for display in _SUPPORTED_DISPLAYS:
            if display[0] == width and display[1] == height:
                return display[2]
        return None

    def rotation(self, rotation):
        """
        Set display rotation.

        Args:
            rotation (int):
                - 0-Portrait
                - 1-Landscape
                - 2-Inverted Portrait
                - 3-Inverted Landscape
        """
        if ((rotation % 2) != (self._rotation % 2)) and (self.width != self.height):
            # non-square displays can currently only be rotated by 180 degrees
            # TODO: can framebuffer of super class be destroyed and re-created
            #       to match the new dimensions? or it's width/height changed?
            return

        # find rotation parameters and send command
        rotation %= len(self.rotations)
        (   madctl,
            self.width,
            self.height,
            self.xstart,
            self.ystart, ) = self.rotations[rotation]
        if self.color_order == BGR:
            madctl |= _ST7789_MADCTL_BGR
        else:
            madctl &= ~_ST7789_MADCTL_BGR
        self._write(_ST7789_MADCTL, bytes([madctl]))
        # Set window for writing into
        self._write(_ST7789_CASET,
            struct.pack(_ENCODE_POS, self.xstart, self.width + self.xstart - 1))
        self._write(_ST7789_RASET,
            struct.pack(_ENCODE_POS, self.ystart, self.height + self.ystart - 1))
        self._write(_ST7789_RAMWR)
        # TODO: Can we swap (modify) framebuffer width/height in the super() class?
        self._rotation = rotation

    def brightness(self, bright):
        """
        Set backlight value

        Args:
            bright(value): Brightness value
              - for PWM this is a (float) between 0 and 1
              - Otherwise a valid GPIO pin setting (bool)
        """
        if self.backlight is None:
            return
        elif self._pwm_bl:
            try:
                bright = max(0, min(1, bright))
                self.backlight.init(duty_u16=int(bright * 0xffff))
            except:
                # not a PWM backlight; set flag and try again
                self._pwm_bl = False
                self.brightness(bright)
        else:
            self.backlight.value(bright)

    def show(self):
        """ Put the current framebuffer onto the screen """
        self._write(None, self.buffer)

    def _cswap(self, color):
        """ Swap colors as needed """
        return swap_bytes(color) if self.needs_swap else color

    """
        Following functions all superclass the framebuffer
        so that color bytes can be swapped as needed
    """
    def fill(self, c):
        super().fill(self._cswap(c))

    def pixel(self, x, y, c=None):
        if c is not None:
            c = self._cswap(c)
            super().pixel(x, y, c)
        else:
            return self._cswap(super().pixel(x, y))

    def hline(self, x, y, w, c):
        super().hline(x, y, w, self._cswap(c))

    def vline(self, x, y, h, c):
        super().vline(x, y, h, self._cswap(c))

    def line(self, x1, y1, x2, y2, c):
        super().line(x1, y1, x2, y2, self._cswap(c))

    def rect(self, x, y, w, h, c, f=False):
        super().rect(x, y, w, h, self._cswap(c), f)

    def fill_rect(self, x, y, w, h, c):
        super().rect(x, y, w, h, self._cswap(c), True)

    def ellipse(self, x, y, xr, yr, c, f=False, m=0xf):
        super().ellipse(x, y, xr, yr, self._cswap(c), f, m)

    def poly(self, x, y, coords, c, f=False):
        super().poly(x, y, coords, self._cswap(c), f)

    def text(self, text, x, y, c=WHITE):
        super().text(text, x, y, self._cswap(c))


class ST7789_I80(ST7789):
    """
    ST7789 driver class for I80 (I8080) bus devices

    Args:
        i80 (bus): bus object        **Required**
        width (int): display width   **Required**
        height (int): display height **Required**
        reset (pin): reset pin
        cs (pin): cs pin is already defined for the I80 bus
          - only used here for hard resets
          - kept for completeness, no tested hardware required it
        backlight (pin) or (pwm): backlight pin
          - can be type Pin (digital), PWM or None
        bright (value): Initial brightness level; default 'on'
          - a (float) between 0 and 1 if backlight is pwm
          - otherwise (bool) or (int) for pin value()
        rotation (int): Orientation of display
          - 0-Portrait, default
          - 1-Landscape
          - 2-Inverted Portrait
          - 3-Inverted Landscape
        color_order (int):
          - RGB: Red, Green Blue, default
          - BGR: Blue, Green, Red
        reverse_bytes_in_word (bool):
          - Enable if the display uses LSB byte order for color words
    """
    def __init__(
        self,
        i80,
        width,
        height,
        reset=None,
        cs=None,
        backlight=None,
        bright=1,
        rotation=0,
        color_order=BGR,
        reverse_bytes_in_word=True,
    ):
        self.i80 = i80
        self.reset = reset
        self.cs = cs
        super().__init__(width, height, backlight, bright, rotation, color_order, reverse_bytes_in_word)

    def _write(self, cmd=None, data=None):
        """I80 bus write to device: command and data."""
        if cmd is not None:
            cmd = cmd[0]
        self.i80.send(cmd, data)

    def hard_reset(self):
        """
        Hard reset display.
        """
        if self.cs:
            self.cs.off()
        if self.reset:
            self.reset.on()
        sleep_ms(10)
        if self.reset:
            self.reset.off()
        sleep_ms(10)
        if self.reset:
            self.reset.on()
        sleep_ms(120)
        if self.cs:
            self.cs.on()


class ST7789_SPI(ST7789):
    """
    ST7789 driver class for SPI bus devices

    Args:
        spi (bus): bus object        **Required**
        width (int): display width   **Required**
        height (int): display height **Required**
        reset (pin): reset pin
        cs (pin): cs pin
        dc (pin): dc pin
        backlight (pin) or (pwm): backlight pin
          - can be type Pin (digital), PWM or None
        bright (value): Initial brightness level; default 'on'
          - a (float) between 0 and 1 if backlight is pwm
          - otherwise (bool) or (int) for pin value()
        rotation (int): Orientation of display
          - 0-Portrait, default
          - 1-Landscape
          - 2-Inverted Portrait
          - 3-Inverted Landscape
        color_order (int):
          - RGB: Red, Green Blue, default
          - BGR: Blue, Green, Red
        reverse_bytes_in_word (bool):
          - Enable if the display uses LSB byte order for color words
    """
    def __init__(
        self,
        spi,
        width,
        height,
        reset=None,
        cs=None,
        dc=None,
        backlight=None,
        bright=1,
        rotation=0,
        color_order=BGR,
        reverse_bytes_in_word=True,
    ):
        self.spi = spi
        self.reset = reset
        self.cs = cs
        self.dc = dc
        super().__init__(width, height, backlight, bright, rotation, color_order, reverse_bytes_in_word)

    def _write(self, command=None, data=None):
        """SPI write to the device: commands and data."""
        if self.cs:
            self.cs.off()
        if command is not None:
            self.dc.off()
            self.spi.write(command)
        if data is not None:
            self.dc.on()
            self.spi.write(data)
        if self.cs:
            self.cs.on()

    def hard_reset(self):
        """
        Hard reset display.
        """
        if self.cs:
            self.cs.off()
        if self.reset:
            self.reset.on()
        sleep_ms(10)
        if self.reset:
            self.reset.off()
        sleep_ms(10)
        if self.reset:
            self.reset.on()
        sleep_ms(120)
        if self.cs:
            self.cs.on()

#fin
