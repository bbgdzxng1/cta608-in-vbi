# CTA-608 Line-21 in pseudo-VBI

Proof-of-concept for creating a digital representation of a CTA-608 (CEA/EIA-608) waveform.

![screenshot](https://github.com/user-attachments/assets/9d67a5a4-06c6-42a3-97c1-9a68a2d3c9aa)

> [!WARNING]
> This is NOT reference code.  This has only been tested with FFmpeg's readeia608, which is not a Line 21 reference decoder.

### Why bother?
I could not find an open-source Line-21 encoder out there.  I don't know why I really needed a Line-21 encoder, but there wasn't one.

There's probably good reason why an open-source Line-21 encoder does not exist... A VBI would not typically be visible to a digital user; nor would the HBI.  These concepts do not appear in digital.  But FFmpeg's readeia608 decoder does not have an analog companion. 

Ok, sometimes you will see the Line-21 waveform when digitizing a source into a full-frame 486 picture, but the VBI should not really appear in a 480 picture.  The team over at vhs-decode _do_ care about the VBI and preserving the full frame, including VBI and HBI, but the average user does not need analog Line-21 captions.  But if you have found this script, you probably know all that already.

It could be useful for creating a digital waveform to enhance or correct a vhs-decode.  It could be used for retro-video creation.

### This script doesn't do much, right?

This script just takes an simple hardcoded array of two-byte words and encodes those two-byte words into a series of sequential video frames, to _simulate_ Line-21 analog closed captions.  It is a badly, written proof of concept.
- You can't set the timings.
- You can't pipe stuff in.  It is a proof of concept.
- You can't send the script an SCC file.  It is _not_ an SCC convertor, processor or encoder.
- This script does not deal with DTVCCs, MPEG-2 Picture User Data, H.264 SEI side data.  There are other tools for digital 608-compatibility-bytes.  


### Line-21 Placement in NTSC

The Line 21s are probably in the wrong place.  But the script can be tweaked to tweak the height of the pseudo-vbi.  If you want a pseudo-VBI of six lines, tweak as you see fit.

field1 | field2 | data
--- | --- | ---
14  | 277 | VITC
16  | 279 | VITC Backup
21  | 284 | EIA-608 Line 21
22  | 285 | Wide-screen Signaling

This naive script willingly ignores inconveniences like interlaced frames, setup/pedestal, IRE, sine, colorrange, colorspace and plenty more.  It is "Ones and Zeros", baby.

It gets a little tricky between digital vertical lines and the field1/2 analog-scanline naming conventions.

### Timing

Analog horizontal scanlines do not operate in a currency of _pixels_, they operate in _time_.  Fortunately, in _Table 2, Line 21 Waveform Timing_ of the EIA-608 Spec (now free to access), it lists timings relative to the timing of the Data Bit 'D' within the Start Bits.

Section | Timing
--- | ---
Clock Run-In (B) | 6.5 * D (but lets use 7 * D)
Clock Run-In to Third Start Bit (C) | 2   * D
Data Bit (D) | 1   * D
Data Characters (E) | 16   * D

That gets us to 26 * D.  Since Clock Run-In needs to be a sinusoidal wave of freqency D to produce `01010101010101`, that needs 14 pixels.  Thus D need to be a minimum of 2 pixels.

Section | Pixels (D = 2 pixels)
--- | ---
Clock Run-In (B) | 7 * D = 14 pixels (could get away with 2 * 6.5 = 13)
Clock Run-In to Third Start Bit (C) | 2 * D = 4 pixels
Data Bit (D) | 1 * D = 2 pixels
Data Characters (E) | 16 * D = 32 pixels

You could probably get away with just a total of 51 pixels minimum if you use `1010101010101` as the Clock Run-In(B) of 6.5 * D = 6.5 * 2 pixels = 13 pixels.  13+4+2+32 = absolute bare minimum of 51 pixels.  But that's a nasty number.  So we'll use a full `01010101010101` as the run-in giving us a minimum of 52.

Once the 52 pixel waveform is encoded as an image, the script scales that to scanline of 640 square pixels wide.  It is a bit irritating that the payload ends up as 52 horizontal width and gets scaled to 640, which is mathematically imperfect (but given that analog line-21 608s rely on sine waves, it is within the realms of error).
- There must be a more elegant way of pre & post padding to a harmonic of 640 (64?), so that it scales pixel-perfect to 640.
- 51 is not much better than 52.  And decoders may not expect the scanline to start immediately on a 1.

It is expected that a user will encode the 640x1 scanline into non-square pixels, giving a horizontal width of 704 or 720.

### Why use Python PIL?

I understand that Python PIL/pillow is RGB only.  Of course, it would be preferable to operate in YUV (yuvio? imageio?).  But _"if all you got is a hammer, the whole world looks like a nail"_.

PIL it shall be, we'll let FFmpeg take the pain of color formats.

### Code Quality is only 1/10

I'm not a developer.  I don't speak Python.  This is my first Python script.  I don't know Python best practice nor any naming or coding conventions.  If there is an error, reader, you'll be better qualified than I to fix.  The code will probably run faster with pypy3 rather than python3.

Yeah, there is a bit of duplication in the code.  If anyone wants to produce a function to dedupe the commands for field 1/2, they are more than welcome.

There is no dependency checking, no error checking, no type checking, everything is a string (rather than Python3 integers in 'bytes').  The script is just a series of commands.

### References

- [Title-47, from The Man.](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-C/part-79)
- CTA [Line 21 Data Services (ANSI/CTA-608-E S-2019).](https://shop.cta.tech/products/line-21-data-services) Now freely-available from CTA.
- FFmpeg's [readeia608 documentation](https://ffmpeg.org/ffmpeg-filters.html#readeia608) and [source code](https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_readeia608.c).  Credit: Paul.
- [sccyou](https://github.com/amiaopensource/sccyou). A bash script for converting line-21s to SCC.  Credit: Dave Rice & Paul.
- McPoodle's [CC codes](http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/CC_CODES.HTML) and [CC characters](http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/CC_CHARS.HTML).  Credit to McPoodle for reverse-engineering SCCs before _"accessibility-standards became accessible to the public"_.
- The History of Closed Captions by Chris Lott.
  - [The analog era](https://hackaday.com/2021/04/14/history-of-closed-captions-the-analog-era/)
  - [entering the digital era](https://hackaday.com/2021/05/27/history-of-closed-captions-entering-the-digital-era/)
- [libzvbi](https://github.com/zapping-vbi/zvbi)
- Digital Video and HD, Algorithms & Interfaces. POYNTON, Charles.  (Morgan Kaufmann)
  - [First Edition (2003)](https://archive.org/details/DigitalVideoForDummies/Digital%20Video%20And%20Hdtv%20Algorithms%20And%20Interfaces)
  - [Second Edition (2012)](https://archive.org/details/digital-video-and-hd-algorithms-and-interfaces-2nd-ed.-poynton-2012-02-07/)
- The Closed Captioning Handbook, ROBSON, Gary D (Elsevier)
  - [2004 Edition](https://garydrobson.com/books/closed-captioning-books/the-closed-captioning-handbook/)
  - [Closed Captions, V-Chip & Other VBI data](https://garydrobson.com/2014/04/16/closed-captions-v-chip-and-other-vbi-data/)
- A blog on [Decoding Closed Captioning](https://nootropicdesign.com/projectlab/2011/03/20/decoding-closed-captioning/)


... And SCTE, SMPTE, ATSC, the good people at WGBH, the National Captioning Institute, Telecaption I, II, 3000? etc.  The crew at ld/vhs-decode.  And, of course, Team FFmpeg.

### VBI fun!
- [Unai.VITC](https://github.com/unai-d/Unai.VITC) which creates a VITC waveform, which kinda inspired the idea to create a scanline that could be embedded into a VBI.
- FFmpeg's [readvitc](https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_readvitc.c)
- [Wide Screen Signaling](https://en.wikipedia.org/wiki/Widescreen_signaling) could be simulated in the same way.
- vhs-decode's [Wide Screen Signaling wiki](https://github.com/oyvindln/vhs-decode/wiki/Wide-Screen-Signalling)


### DTVCCs
- ATSC [A/53](https://www.atsc.org/atsc-documents/a53-atsc-digital-television-standard/)
- CTA [Digital Television Closed Captioning (ANSI/CTA-708-E S-2023)](https://shop.cta.tech/products/digital-television-dtv-closed-captioning) aka DTVCCs
- [libcaption](https://github.com/szatmary/libcaption) for inserting DTVCCs.  Credit: Matt Szatmary, formerly at Twitch, now over at mux.com
