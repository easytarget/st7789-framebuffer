# ST7789 FrameBuffer drivers for Micropython
# Compatible with I80 and SPI busses
* Because we dont (yet) have enough drivers for this chip.. :-)

These Drivers have methods for *both* **`SPI`** and **`I80`** (`I8080`) busses, using the inbuilt MicroPython driver for `spi` or the `I80` library from Brad Barnett's [mpdisplay](https://github.com/bdbarnett/mpdisplay).

## Code is Complete
It has been well tested on 3 devices now; a T-Display Touch (ESP32-S3, I80), a T-Watch 2020 (ESP32, SPI) and a loose IPS display module attached to a ESP32-C3 devboard via SPI.

There may be some minor tweaks as I work through documenting this, but I dont anticipate any further breaking changes

[![Demos](doc/tdisplay2.jpg)](doc/tdisplay2.jpg)
* Photos dont really do justice to how good the IPS panel on the T-Display looks in reality.https://github.com/russhughes/st7789_mpy

# There are better drivers available; but they require custom firmware
https://github.com/russhughes/st7789_mpy is a excellent driver; especially if you have a i80 bus. Because it uses the bus properly it is ver, very fast. far faster than the drivers here.

If you need speed or lots of free memory; and using (possibly compiling) a custom firmware is practical for you, use that driver and ignore this page.
- I'm being serious; The drvers  gve here were made for my own *very simple projects* and they do not scale very well for more complex use.

[LVGL](https://docs.lvgl.io/master/details/integration/bindings/micropython.html) and other projects also have good st7789 support via frmware drivers; if you are building a full GUI check them out.

# This repo actually has TWO drivers:

Both support SPI and I80 busses; one is smaller and more basic than the other.
- support for PWM backlight is also added to both

## A 'pure' framebuffer driver
Fully supports MicroPython's built in frameuffer, with no additional drawing, scrolling or font writng features.

## A modified version of of the driver from: https://github.com/echo-lalia/st7789fbuf
This is itself a modified version of Russ Hughes driver
There are a number of additional drawing and font handling features provided for this that can make use for GUI and large displays more convenient
Very heavy on memory; pretty much requires having PSRAM enabled

# Use
See the examples for a good example of using these.

Both of these divers use a lot of memory for the framebuffer; for 320x170 and 240x240 displays this is just *over* 100K of memory; with these large displays it may prove impossible to use these unless you have PSRAM (SPIRAM) enabled in the micropython firmware. SPI RAM enabled version for the firmwares are available on the main MicroPython dowwnload sites. The smaller (240x135) display I tested with only uses 60K and did not have any memory issues on a ESP32-C3.

The basic driver is essentially a drop-in replacement for any other framebuffer driver; and is aimed at people adapting code from simpler monochrome displays such as SSD1306's etc.

The more advanced driver has additional useful methods for use with large color displays; it is derived (via a third party) from the mani MPDisplay driver; these are documented here: [https://github.com/russhughes/st7789s3_mpy?tab=readme-ov-file#methods](https://github.com/russhughes/st7789s3_mpy/blob/main/README.md#methods); please note that the Init options are a little different as noted below, also see my examples etc.
@russhughes 
## INIT; chosing and using the SPI or I80 bus
Both drivers are subclassed into SPI and i80 variants; with a common init syntax
### Bus drivers
The SPI bus class is inbuilt in MicroPython; and imported with a simple `from microputhon import SPI` line.

The I80 bus driver needs to be added to your project; to do this simply copy the whole `i80` folder to the root of your device.
- This bus driver is rather nice; it was [written by @russhughes]9https://forum.lvgl.io/t/micropython-display-drivers-part-2/14131/21) and the home repo for it is [here](https://github.com/bdbarnett/mpdisplay/tree/main/drivers/bus). I use a older version bundled into a single library.

### Using the correct sub-class
Both drivers have SPI and I80 subclasses; so each has two init methods:

<TODO> !!!!!!!!!!!!!!!!!!!!!!!!

## Backlight PWM control

<TODO> !!!!!!!!!!!!!!!!!!!!!!!!
