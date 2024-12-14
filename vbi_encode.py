#!/usr/bin/env python3

"""
A digital representation of Line 21 analog 608 captions in a pseudo-VBI.
"""

import subprocess
from PIL import Image

# TODO: PyLint

# Array of two-byte words for Field 1.  It should produce a pop-on capttion on row-15. I shall leave it to the reader to guess what it says.  The convention of duplicating control codes seems wasteful in terms of in a digital world.
field1_words_hex = [
    "94ae",
    "9420",
    "9470",
    "c8e5",
    "ecec",
    "ef2c",
    "20f7",
    "eff2",
    "ec64",
    "942c",
    "942c",
    "942f",
]
# Using null characters for Field 2, since From CTA-608... "When no field 2 services are being used, the line 21, field 2 waveform shall carry the appropriate clock run-in and null characters with parity bits"
field2_words_hex = ["8080"] * len(field1_words_hex)


def encode_scanline_as_image(payload):
    """
    Create a 1-pixel height image from a binary string.
    """
    width = len(payload)
    image = Image.new("RGB", (width, 1), "darkgray")
    pixels = image.load()
    for pixel in range(width):
        if payload[pixel] == "1":
            pixels[pixel, 0] = (255, 255, 255)  # White
        else:
            pixels[pixel, 0] = (0, 0, 0)  # Black
    return image


def process_word_hex(field1_word_hex, field2_word_hex, frame_number):
    # CC1/2
    byte1_hex = field1_word_hex[:2]
    byte1_bin = format(int(byte1_hex, 16), "08b")
    byte1_bin = byte1_bin[::-1]  # reverse the order
    byte2_hex = field1_word_hex[2:]
    byte2_bin = format(int(byte2_hex, 16), "08b")
    byte2_bin = byte2_bin[::-1]  # reverse the order
    field1_payload = byte1_bin + byte2_bin
    print("INFO: field1 payload is " + field1_payload + " (" + field1_word_hex + ")")
    # Each bit in the character data payload needs to be twice the width
    field1_payload_doublewidth = "".join([char * 2 for char in field1_payload])
    clockRunIn_payload = "01010101010101"
    startBits_payload = "000011"
    field1_scanline_payload = (
        clockRunIn_payload + startBits_payload + field1_payload_doublewidth
    )
    print("INFO: scanline payload length is: {}".format(len(field1_scanline_payload)))
    field1_scanline_encoded = encode_scanline_as_image(field1_scanline_payload)
    field1_scanline_encoded = field1_scanline_encoded.resize(
        (640, field1_scanline_encoded.height), Image.NEAREST
    )

    # CC3/4 - this is all just duplicated/pasted code.  I appreciate that it should be a function.  If it offends you, improvements are welcome.
    byte1_hex = field2_word_hex[:2]
    byte1_bin = format(int(byte1_hex, 16), "08b")
    byte1_bin = byte1_bin[::-1]  # reverse the order
    byte2_hex = field2_word_hex[2:]
    byte2_bin = format(int(byte2_hex, 16), "08b")
    byte2_bin = byte2_bin[::-1]  # reverse the order
    field2_payload = byte1_bin + byte2_bin
    print("INFO: field2 payload is " + field2_payload + " (" + field2_word_hex + ")")
    # Each bit in the character data payload needs to be twice the width
    field2_payload_doublewidth = "".join([char * 2 for char in field2_payload])
    clockRunIn_payload = "01010101010101"
    startBits_payload = "000011"
    field2_scanline_payload = (
        clockRunIn_payload + startBits_payload + field2_payload_doublewidth
    )
    print("INFO: scanline payload length is: {}".format(len(field2_scanline_payload)))
    field2_scanline_encoded = encode_scanline_as_image(field2_scanline_payload)
    field2_scanline_encoded = field2_scanline_encoded.resize(
        (640, field2_scanline_encoded.height), Image.NEAREST
    )

    vbi = Image.new("RGB", (640, 23), "black")
    vbi.paste(field1_scanline_encoded, (0, 21))
    vbi.paste(field2_scanline_encoded, (0, 22))

    filename = f"./vbi_frame_{frame_number:05d}.png"
    vbi.save(filename)  # Save the frame


# Process each word and save frames
for frame_number, (field1_word_hex, field2_word_hex) in enumerate(
    zip(field1_words_hex, field2_words_hex)
):
    process_word_hex(field1_word_hex, field2_word_hex, frame_number)

# Validate what was encoded into field1 with FFprobe.
command = [
    "ffprobe",
    "-hide_banner",
    "-loglevel",
    "warning",
    "-f",
    "lavfi",
    "movie=filename=./vbi_frame_%05d.png:format_name='image2':format_opts=framerate='ntsc',readeia608",
    "-show_entries",
    "frame=best_effort_timestamp_time : frame_tags=lavfi.readeia608.0.cc",
    "-print_format",
    "compact=nokey=true:print_section=false",
]
result = subprocess.run(command, capture_output=True, text=True)
# print(result.stdout)
print(result.stderr)

readeia608_0_cc = result.stdout
print(
    "INFO: Result... Caption two-byte words for field 1 as read by FFprobe: \n{}".format(
        readeia608_0_cc
    )
)

# Encode some smptebars with vbi on top
# ignoring range, colorspace, interlacing, ntsc-stuff, range limiters etc.

command = [
    "ffmpeg",
    "-hide_banner",
    "-loglevel",
    "warning",
    "-f",
    "lavfi",
    "-i",
    "smptebars=size='sntsc':rate='ntsc',setdar=ratio='(4/3)'",
    "-f",
    "image2",
    "-framerate",
    "ntsc",
    "-i",
    "./vbi_frame_%05d.png",
    "-filter_complex",
    "[1:v:0][0:v:0]vstack=inputs=2,format=pix_fmts='yuv422p',scale=width=720:height='ih'[out]",
    "-map",
    "[out]",
    "-codec:v",
    "ffv1",
    "-level:v",
    "3",
    "-g:v",
    "1",
    "-t",
    "00:00:01.000",
    "./vbi.nut",
    "-y",
]
result = subprocess.run(command, capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

### More Validation...
# sccyou to extract line21 to scc
# sccyou -y "./vbi.nut"
# mpv "./vbi.nut" --sub-file="./vbi.scc"
