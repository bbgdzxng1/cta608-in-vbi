# CTA-608 Line-21 in pseudo-VBI

Proof-of-concept for creating a digital representation of a CTA-608 (CEA/EIA-608) waveform.

This is NOT reference code.  This has only been tested with FFmpeg's readeia608, which is not a Line 21 reference decoder.

I could not find an open-source line-21 encoder out there.

I don't know why I really needed a line-21 encoder, but there wasn't one.  A VBI would not usually be visible to a user.  Nor would the HBI.  These concepts do not appear in digital.  Ok, sometimes you will see the Line-21 waveform when digitizing a source into a full-frame 486 picture, but the VBI should not appear in a 480 picture.  The team over at vhs-decode do care about the VBI and preserving the full frame, including VBI and HBI, but the average user does not need line 21-captions.  But if you have found this script, you probably know all that already.

The Line 21s are probably in the wrong place.

This naive script willingly ignores inconveniences like interlaced frames, setup/pedestal, IRE, sine, colorrange, colorspace and plenty more.  It is "Ones and Zeros", baby.

The active horizontal picture is set at 640 wide (square pixels).  It is expected that a user will entode into a 704 or 720 with non-square pixels.

Yeah, there is a bit of duplication in the code.  If anyone wants to add a function to dedupe the command for field 1/2, they are more than welcome.

This is NOT an SCC convertor, processor or encoder.  It is unrelated to DTVCCs (either digital 608-compatibility-bytes or 708s).  It just takes an array of two-byte words and sequentially encodes those two-byte words to each frame, to simulate line-21 analog closed captions.

I believe that Python PIL/pillow is RGB only.  Of course, it would be preferable to operate in YUV (yuvio? imageio? but I'm not fighting numpy.).  "But if all you got is a hammer, the whole world looks like a nail". PIL it shall be, let FFmpeg take the pain of color formats...

It is a bit irritating that the payload ends up as 52 horizontal width and gets scaled to 640, which is mathematically imperfect (but given that alalog 608s relies on sine waves, it is within the realms of error).  There must be a more elegant way of pre-post padding to 64, so that it scales perfectly to 640.  But the "timing" all relies on the width of a single-bit of the startBits (D), as described in table "Table 2 Line 21 Waveform Timing" of EIA-608 (which is now free).

Credit to Paul for readeia608, and Dave Rice for sccyou.  And McPoodle for reverse-engineering before accessibility-standards became accessible to the public.  And SCTE, SMPTE, ATSC, the good people at WGBH, the National Captioning Institute with the Telecaption I, II, 3000? etc.  Matt Szatmary, formerly at Twitch, now over at Mux.com.  Chris Lott etc.  The crew at ld/vhs-decode.

I don't speak python.  This is my first python script.  I don't know the code or naming conventions.  If there is an error, reader, you'll be better qualified than I to fix.  This may be faster with pypy3 rather than python3.


### References

- [Title-47, from the man](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-C/part-79)
- [Line 21 Data Services (ANSI/CTA-608-E S-2019)](https://shop.cta.tech/products/line-21-data-services)
- https://ffmpeg.org/ffmpeg-filters.html#readeia608
- https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_readeia608.c
- https://github.com/amiaopensource/sccyou
- http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/CC_CODES.HTML
- http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/CC_CHARS.HTML
- https://hackaday.com/2021/04/14/history-of-closed-captions-the-analog-era/
- https://hackaday.com/2021/05/27/history-of-closed-captions-entering-the-digital-era/
- https://nootropicdesign.com/projectlab/2011/03/20/decoding-closed-captioning/
- https://garydrobson.com/2014/04/16/closed-captions-v-chip-and-other-vbi-data/
- https://github.com/zapping-vbi/zvbi

### Related
- [libcaption, for inserting DTVCCs](https://github.com/szatmary/libcaption)
- https://github.com/unai-d/Unai.VITC
- https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_readvitc.c
- https://en.wikipedia.org/wiki/Widescreen_signaling
- https://github.com/oyvindln/vhs-decode/wiki/Wide-Screen-Signalling



