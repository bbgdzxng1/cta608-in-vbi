# CTA-608 Line-21 in pseudo-VBI

A proof-of-concept for creating a digital representation of a CTA-608 (CEA/EIA-608) waveform, aka "analog line-21 captions" encoded in the video signal.

![screenshot](https://github.com/user-attachments/assets/9d67a5a4-06c6-42a3-97c1-9a68a2d3c9aa)

> [!WARNING]
> This is NOT reference code.  This has only been tested with FFmpeg's readeia608, which is not a Line 21 reference decoder.

### Why bother?
I could not find an open-source analog line-21 encoder out there.  I don't know why I really needed an analog line-21 encoder, but there wasn't one.

There's probably good reason why an open-source analog line-21 encoder does not exist... A VBI would not typically be visible to a digital user; nor would the HBI.  These concepts do not appear in digital.  But I felt that FFmpeg's readeia608 decoder was missing an analog line-21 encoder companion. 

Ok, sometimes you will see the analog line-21 waveform when digitizing a source into a full-frame 486 picture, but the VBI should not really appear in a digital 480 picture.  The team over at [vhs-decode](https://github.com/oyvindln/vhs-decode) _do_ care about the VBI and preserving the full frame, including VBI and HBI, but the average user does not need analog line-21 captions.  But if you have found this script, you probably know all that already.

This repo could be used as a basis for:
- Enhancing or correcting a vhs-decode.
- Retro-style video creation.
- Creating analog line-21 captions on the top-row of a SVCD.

### This script doesn't do much, right?

This script just takes an simple hardcoded array of CTA-608 two-byte words (the same as used in SCC) and encodes those two-byte words into a series of sequential video frames, to _simulate_ Line-21 analog closed captions.  It is a badly written proof of concept.
- You can't set the timings.
- You can't pipe stuff in.  It is a proof of concept.
- You can't send the script an SCC file.  It is _not_ an SCC convertor, processor or encoder.
- This script does not deal with DTVCCs, MPEG-2 Picture User Data, H.264 SEI side data.  It is for analog line-21s.  Analog line-21s predate digital storage and transmission such as DTVCCs, which were subsequent mechanisms & technologies to transmit those same bytes through MPEG headers.  If you have found this repository looking for the inclusion of CTA-608 in MPEG Headers (aka 608-compatibility-bytes), see projects such as CC_MUX (DVD) and libcaption (DTVCC), referenced later in this file.  

### Line-21 Placement in NTSC

The vertical height of the pseudo-VBI and the location of the Line-21 scanlines in this script are probably in the wrong place, when compared to real-world implementations.  But the script can be tweaked to change the height of the pseudo-VBI.  If you want a pseudo-VBI of six lines, adjust as you see fit.

It gets a little tricky between digital vertical lines and the analog-scanline naming conventions.  I make no apologies. The common locations of various similar payloads in VBI were...

field1 | field2 | data
--- | --- | ---
14  | 277 | VITC
16  | 279 | VITC Backup
21  | 284 | EIA-608 Line 21
22  | 285 | Wide-screen Signaling

This naive script willingly ignores inconveniences like interlaced frames, setup/pedestal, IRE, sine-waves, colorrange, colorspace and plenty more.  It is _"ones and zeros, baby"_.  The pixels are either 0 or 255, but the script can be modified to produce 1-254 (SDI legal), or 16-240 (limited), or any value of intensity to simulate setup/pedestal when within an HBI.

### Timing

Analog horizontal scanlines do not operate in a currency of _pixels_, they operate in a currency of _time_.  Fortunately, in _Table 2, Line 21 Waveform Timing_ of the EIA-608 Spec (now free to access), it lists timings relative to the timing of the Data Bit 'D' within the Start Bits.

Section | Timing
--- | ---
Clock Run-In (B) | 7 * D (could get away with 6.5 * D)
Clock Run-In to Third Start Bit (C) | 2   * D
Data Bit (D) | 1   * D
Data Characters (E) | 16   * D

That gets us to 26 * D.  Clock Run-In needs 7 (or 6.5) cycles of an oscillating wave of freqency D.  If we assume that a digital square-wave is a sufficient approximation of a sine wave, _D needs to be an absolute minimum of 2 pixels to approximate a sinusoidal Clock Run-In cycle with square-waves._

Section | Pixels (D = 2 pixels)
--- | ---
Clock Run-In (B) | 7 * D = 14 pixels (could get away with 2 * 6.5 = 13)
Clock Run-In to Third Start Bit (C) | 2 * D = 4 pixels
Data Bit (D) | 1 * D = 2 pixels
Data Characters (E) | 16 * D = 32 pixels

- Is the Clock Run-In 6.5 or 7 cycles?
  - The EIA608 spec states a minimum of 6.5 * D, ie `1010101010101`.  Since D requires a minimum of 2 pixels to represent an oscillating square wave, the Clock Run-In needs an absolute minimum of 13 pixels, thus the total minimum playload is 13+4+2+32 = 51 pixels.
  - In "The Closed Captioning Handbook", Gary Robson writes _"The Clock Run-In signal is 7 full cycles of a 0.5034965 MHz sine wave, centered around the 25 IRE level, lasting 12.91 ps."_  Robson was a member of the 608 and 708 working group, so we'll use 7*D as the Clock Run-In.  With 7 full cycles, the clock run-in is `01010101010101`, thus the total minimum playload is 14+4+2+32 = 52 pixels.  52 is a nicer number than 51.  Therefore we'll use 7 * D.

Once the 52 pixel payload/waveform is encoded as an image, the script scales that image to a full scanline of 640 square-pixels width.  It is a bit irritating that 52 pixels is not a perfect harmonic of a 640 square-pixel scanline, but given that analog line-21 608s rely on oscillation waves and timing rather than digital pixels, it is within the realms of reasonable error.
- There may be a more elegant way of pre & post-padding the payload to a harmonic of 640 (64?), so that it scales pixel-perfect to 640.
- A more competant coder could skip the scaling step and generate the payload at full resolution, or may even choose to vary the intensity to avoid the square-wave/sine-wave approximation.

The 640x1 scanline can then be used in a VBI, or overlaid on the top row of a 480 video frame depending on the output format.

It is expected that a user will eventually encode the 640 square pixels into NTSC non-square pixels.

### Why use Python PIL?

Python PIL/pillow is RGB only.  Of course, it would be preferable to operate in YUV (yuvio? imageio?).  But _"if all you got is a hammer, the whole world looks like a nail"_.

PIL it shall be, for the purposes of a proof-of-concept, we'll let FFmpeg take the pain of color formats.

### Code Quality is only 1/10

I'm not a developer.  I don't speak Python.  This is my first Python script.  I don't know Python best-practice, nor any naming or coding conventions.  If there is an error, reader, you'll be better qualified than I to fix.  It is most likely that the script will run faster with pypy3 rather than python3.

Yeah, there is a bit of duplication in the code.  If anyone wants to produce a function to dedupe the commands for field 1/2, they are more than welcome.

The script contains no dependency checking, no error checking, no type checking, everything is a string (rather than Python3's new 'bytes').  The script is just a series of naive commands.

## References

### Line-21 Captions

The four magic documents that explain how to construct 608 pairs are...
- [Title-47, from The Man.](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-C/part-79)
- CTA [Line 21 Data Services (ANSI/CTA-608-E S-2019).](https://shop.cta.tech/products/line-21-data-services) Now freely-available from CTA.  Contains useful implementation details, including extended chararacter sets which are not covered in Title-47.
- The Closed Captioning Handbook, ROBSON, Gary D (Elsevier).  Note: this hard-to-find book is an excellent reference.  Robson was involved in the development of both 608 and 708.  This book is a great companion to Title-47 and CTA-608-E.
  - [2004 Edition](https://garydrobson.com/books/closed-captioning-books/the-closed-captioning-handbook/)
  - [Closed Captions, V-Chip & Other VBI data](https://garydrobson.com/2014/04/16/closed-captions-v-chip-and-other-vbi-data/)
- McPoodle's [CC codes](http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/CC_CODES.HTML) and [CC characters](http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/CC_CHARS.HTML).  Credit to McPoodle for reverse-engineering SCCs before _"accessibility-standards became accessible to the public"_.  It should be cross-referenced to Title-47 and CTA-608-E, and should not be considered reference material (since it is reverse engineered), but is a useful quick guide.  It may contain implementation errors.

Other useful material...
- FFmpeg's [readeia608 documentation](https://ffmpeg.org/ffmpeg-filters.html#readeia608) and [source code](https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_readeia608.c).  Credit: Paul.
- [sccyou](https://github.com/amiaopensource/sccyou). A bash script for converting line-21s to SCC, based on the readeia608 filter.  Credit: Dave Rice & Paul.
- The History of Closed Captions by Chris Lott.
  - [The analog era](https://hackaday.com/2021/04/14/history-of-closed-captions-the-analog-era/)
  - [entering the digital era](https://hackaday.com/2021/05/27/history-of-closed-captions-entering-the-digital-era/)
- Digital Video and HD, Algorithms & Interfaces. POYNTON, Charles.  (Morgan Kaufmann)
  - [First Edition (2003)](https://archive.org/details/DigitalVideoForDummies/Digital%20Video%20And%20Hdtv%20Algorithms%20And%20Interfaces)
  - [Second Edition (2012)](https://archive.org/details/digital-video-and-hd-algorithms-and-interfaces-2nd-ed.-poynton-2012-02-07/)
- [libzvbi](https://github.com/zapping-vbi/zvbi)
- A blog on [Decoding Closed Captioning](https://nootropicdesign.com/projectlab/2011/03/20/decoding-closed-captioning/)
- [Closed Captioning: More Ingenious than You Know](https://www.youtube.com/watch?v=6SL6zs2bDks)

... and SCTE, SMPTE, ATSC, the good people at WGBH, the National Captioning Institute [TeleCaption I](https://www.youtube.com/watch?v=nLi2uJAwYQ4), II, [3000](https://www.chicagotribune.com/1989/05/05/captioning-gives-deaf-whole-story/), [4000](https://www.lddb.com/hardware/1689/caption/National-Caption-Institute/TeleCaption-4000) & [VR-100](https://www.lddb.com/hardware/1973/caption/National-Caption-Institute/TeleCaption-VR-100) devices.  The crew at ld/vhs-decode.  And, of course, Team FFmpeg.

### DTVCCs (digital 608s & 708s) in MPEG-2 Picture User Data and H.264 SEI side data

Although this proof-of-concept does not aim to deal with the digital representation of CTA-608 within MPEG2 Picture User Data nor H.264 SEI side-data, the following are useful resources on DTVCCs.
- ATSC 1.0 [A/53](https://www.atsc.org/atsc-documents/a53-atsc-digital-television-standard/)
- CTA [Digital Television Closed Captioning (ANSI/CTA-708-E S-2023)](https://shop.cta.tech/products/digital-television-dtv-closed-captioning), aka DTVCCs
- [libcaption](https://github.com/szatmary/libcaption) for inserting DTVCCs and examples for muxing 608-compatibility-bytes in H.264 SEI side-data.  Credit: Matt Szatmary, formerly at Twitch, now over at mux.com.  At the time of writing, there are no known, actively maintained, open-source projects that easily allow for DTVCCs in MPEG-2 Picture User Data, although it may be possible to modify the H.264 examples included in libcaption. 

### Line-21 captions in SVCD & DVD

The [SVCD Specification](https://archive.org/details/super-video-compact-disc-svcd-system-specification-version-1.0-may-1999/page/28/mode/2up) states that analog line-21 captions can be included on the top pixel row of an NTSC SVCD.  An SVCD player would be expected to modulate this on line-21 of an analog output.

_"V.3.3 Special Information in the MPEG video signal.  If bit|3] of the Status Flags entry of the file INFO.SD is set to one, then the top pixel row of the MPEG picture can contain special information. In this case the top pixel row is intended to be displayed at line 21 of the video output signal for NTSC. This Special Information is used for Closed Caption in USA."_

Until the [DVD-Video Format Book is publicly released in early 2025](https://www.dvdfllc.co.jp/notice.html#january), it is unclear whether the DVD-Video specification supports analog line-21 captions on a video scanline, similar to SVCD.  It is considered factual that NTSC DVD-Video does not allow NTSC video signalling outside of an 720x480 NTSC frame, it seems that support for analog line-21s would be unlikely unless a "top-row workaround" via a similar mechanism to SVCD is utilized.
- Where Closed Captioning _is_ supported in DVD-Video, the data is stored as picture user data header and the line-21 output is regenerated/modulated on an analog output.  See McPoodle's [CC_MUX](http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/CC_MUX.HTML) for a reverse-engineered interpretation of real-world implementations.  In The Closed Captioning Handbook, Robson suggests that Closed Captioning support in DVD-Video was somewhat an afterthought.  _"At the last minute, support was thrown into the DVD specifications for embedded line 21 captioning...  Unfortunately, not all commercial players support the line 21 captioning capability..."_
- It is noted that although the mechanism for DVD-Video and ATSC 1.0 are _similar_, they differ in implementation.  The DVD-Video specification pre-dates ATSC 1.0 by several years.

### libzvbi's zvbi-ntsc-cc line 21 decoder

From https://github.com/zapping-vbi/zvbi.  Output from this repository has not been tested against `zvbi-ntsc-cc`

```shell
$ zvbi-ntsc-cc -h

CCDecoder 0.13 -- Closed Caption and XDS decoder
Copyright (C) 2003-2007 Mike Baker, Mark K. Kim, Michael H. Schimek
<mschimek@users.sf.net>; Based on code by timecop@japan.co.jp.
This program is licensed under GPL 2 or later. NO WARRANTIES.

Usage: zvbi-ntsc-cc [options]
Options:
-? | -h | --help | --usage  Print this message and exit
-1 ... -4 | --cc1-file ... --cc4-file filename
                            Append caption channel CC1 ... CC4 to this file
-b | --no-webtv             Do not print WebTV links
-c | --cc                   Print Closed Caption (includes WebTV)
-d | --device filename      VBI device [/dev/vbi]
-f | --filter type[,type]*  Select XDS info: all, call, desc, length,
                            network, rating, time, timecode, timezone,
                            title. Multiple -f options accumulate. [all]
-k | --keyword string       Break caption line at this word (broken?).
                            Multiple -k options accumulate.
-l | --channel number       Select caption channel 1 ... 4 [no filter]
-p | --plain-ascii          Print plain ASCII, else insert VT.100 color,
                            italic and underline control codes
-r | --raw line-number      Dump raw VBI data
-s | --sentences            Decode caption by sentences
-v | --verbose              Increase verbosity
-w | --window               Open debugging window (with -r option)
-x | --xds                  Print XDS info
-C | --cc-file filename     Append all caption to this file [stdout]
-R | --semi-raw             Dump semi-raw VBI data (with -r option)
-X | --xds-file filename    Append XDS info to this file [stdout]
```

Installation of `zvbi-ntsc-cc` via homebrew, for macOS (and possibly linuxbrew?)...

```shell
$ brew info lescanauxdiscrets/tap/zvbi

==> lescanauxdiscrets/tap/zvbi: stable 0.2.35
http://zapping.sourceforge.net/
Installed
/opt/homebrew/Cellar/zvbi/0.2.35 (25 files, 1.4MB) *
  Built from source on 2024-12-18 at 09:46:31
From: https://github.com/lescanauxdiscrets/homebrew-tap/blob/HEAD/Formula/zvbi.rb
```

### Max Smith's cc_decode.py
A Python-based line-21 decoder, written for extraction of line 21s from Laserdiscs.  `cc_decoder.py` appears to be able to extract line21s to SCC (and SRT).  Output from this repository has not been tested against `cc_decoder.py`.
https://github.com/CordySmith/cc_decoder

### Wide-screen Signaling/Signalling in VBI
- [Rec. ITU-R BT.1119-2](https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1119-2-199802-W!!PDF-E.pdf) Recommendation ITU-R BT.1119-2 Wide-screen Signalling for Broadcasting (Signalling for wide-screen and other enhanced television parameters).
- [Wide Screen Signaling](https://en.wikipedia.org/wiki/Widescreen_signaling) could be simulated in the same way, however encoding WSS in an NTSC 525 digital stream would need careful consideration, since in bit 7, NTSC WSS signals whether the frame is a reference frame.  This would rely on either prior-knowledge (such as FFmpeg's `force_key_frames`) or a predictable reference frame cadence (such as a fixed-GOP/sub-GOP) prior to generation of the waveform.
- vhs-decode's [Wide Screen Signaling wiki](https://github.com/oyvindln/vhs-decode/wiki/Wide-Screen-Signalling)

### VITC in VBI
- [Unai.VITC](https://github.com/unai-d/Unai.VITC) which creates a VITC 90-bit scanline, which kinda inspired the idea to create a Line-21 scanline that could be embedded into a pseudo-VBI.
- FFmpeg's [readvitc](https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_readvitc.c)
