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
#   (madctl, width, height, xstart, ystart, needs_swap)[rotation % 4]

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

# fmt: on


def color565(red, green=0, blue=0):
    """
    Convert red, green and blue values (0-255) into a 16-bit 565 encoding.
    """
    if isinstance(red, (tuple, list)):
        red, green, blue = red[:3]
    return (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3

def swap_bytes(color):
    """
    this just flips the left and right byte in the 16 bit color.
    """
    return ((color & 255) << 8) + (color >> 8)


class ST7789(framebuf.FrameBuffer):
    """
    ST7789 driver class

    Args:
        i80 (bus): bus object **Required**
        width (int): display width **Required**
        height (int): display height **Required**
        reset (pin): reset pin
        cs (pin): cs pin
        backlight(pin): backlight pin (can be a pwm pin)   <-- PWM TO DO
        brightness (float 0->1): Initial brightness level  <-- Needs method() too
        rotation (int):
          - 0-Portrait
          - 1-Landscape
          - 2-Inverted Portrait
          - 3-Inverted Landscape
        color_order (int):
          - RGB: Red, Green Blue, default
          - BGR: Blue, Green, Red


    """

    def __init__(
        self,
        bus,
        width,
        height,
        reset=None,
        cs=None,
        backlight=None,
        brightness=1,
        rotation=0,
        color_order=BGR,
        swap_bytes=True,
    ):
        """
        Initialize display.
        """
        self.rotations = self._find_rotations(width, height)
        if not self.rotations:
            supported_displays = ", ".join(
                [f"{display[0]}x{display[1]}" for display in _SUPPORTED_DISPLAYS]
            )
            raise ValueError(
                f"Unsupported {width}x{height} display. Supported displays: {supported_displays}"
            )

        #init the framebuffer
        self.buffer = bytearray(height*width*2)
        if rotation == 1 or rotation == 3:
            super().__init__(self.buffer, height, width, framebuf.RGB565)
        else:
            super().__init__(self.buffer, width, height, framebuf.RGB565)
        self.width = width
        self.height = height
        self.xstart = 0
        self.ystart = 0
        self.bus = bus
        self.reset = reset
        self.cs = cs
        self.backlight = backlight
        self._rotation = rotation % 4
        self.color_order = color_order
        self.init_cmds = _ST7789_INIT_CMDS
        self.hard_reset()
        # yes, twice, once is not always enough
        self.init(self.init_cmds)
        self.init(self.init_cmds)
        # Rotoation
        self.rotation(self._rotation)
        # Write Window
        self._write(_ST7789_CASET,
            struct.pack(_ENCODE_POS, self.xstart, self.width + self.xstart - 1))
        self._write(_ST7789_RASET,
            struct.pack(_ENCODE_POS, self.ystart, self.height + self.ystart - 1))
        self._write(_ST7789_RAMWR)
        # Color LSB/MSB swapping
        self.swap_bytes = swap_bytes
        # Blank display and turn on backlight
        self.fill(0x0)
        self.show()
        if backlight is not None:
            backlight.value(brightness)

    def _find_rotations(self, width, height):
        """
        Find the correct rotation for our display or return None
        """
        for display in _SUPPORTED_DISPLAYS:
            if display[0] == width and display[1] == height:
                return display[2]
        return None

    def init(self, commands):
        """
        Initialize display.
        """
        for command, data, delay in commands:
            self._write(command, data)
            sleep_ms(delay)

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

    def rotation(self, rotation):
        """
        Set display rotation.

        Args:
            rotation (int):
                - 0-Portrait
                - 1-Landscape
                - 2-Inverted Portrait
                - 3-Inverted Landscape

            custom_rotations can have any number of rotations
        """
        rotation %= len(self.rotations)
        self._rotation = rotation
        (
            madctl,
            self.width,
            self.height,
            self.xstart,
            self.ystart,
        ) = self.rotations[rotation]

        if self.color_order == BGR:
            madctl |= _ST7789_MADCTL_BGR
        else:
            madctl |= _ST7789_MADCTL_RGB

        self._write(_ST7789_MADCTL, bytes([madctl]))
        # We should really clean and re-create framebuffer if orientation
        # changes and new width/height != old width/height, + set new self.width/height

    def _write(self, cmd=None, data=None):
        # The I80 bus driver expects an int() not byte()
        if cmd is not None:
            cmd = cmd[0]
        self.bus.send(cmd, data)
        
    def show(self):
        self._write(None, self.buffer)
        
    def _sc(self, c):   # aka 'swap colors'
        return swap_bytes(c) if self.swap_bytes else c

    # Now a super() for all the framebuffer methods that use colors
    # so we can swap colors as needed.
        
    def fill(self, c):
        super().fill(self._sc(c))
        
    def pixel(self, x, y, c=None):
        if c is not None:
            c = self._sc(c)
        super().pixel(text, x, y, c)
        # Swap the return????                     <<<------ TEST
        
    def hline(self, x, y, w, c):
        super().hline(x, y, w, self._sc(c))

    def vline(self, x, y, w, c):
        super().vline(x, y, w, self._sc(c))

    def line(self, x1, y1, x2, y2, c):
        super().line(x1, y1, x2, y2, self._sc(c))

    def rect(self, x, y, w, h, c, f=None):
        super().rect(x, y, w, h, self._sc(c), f)

    def fill_rect(self, x, y, w, h, c):
        super().rect(x, y, w, h, self._sc(c), True)
        
    def ellipse(self, x, y, xr, yr, c, f=None, m=None):
        super().ellipse(x, y, xr, yr, self._sc(c), f, m)

    def poly(self, x, y, coords, c, f=None):
        super().poly(x, y, coords, self._sc(c), f)

    def text(self, text, x, y, c=WHITE):
        super().text(text, x, y, self._sc(c))
#fin