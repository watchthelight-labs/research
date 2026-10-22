**What was wrong**

Dock badges were red circles with no number in them. CoreAnimation draws the digit into a 108x108 texture that has a full mip chain, uploads only level 0, then shrinks it into the badge with a trilinear sampler. Nothing ever fills the other levels, so on this driver the sample read empty levels and the digit disappeared.

**What this changes**

When an app uploads level 0 of a mipmapped 8-bit texture and never touched the levels above it, the plugin fills them from that upload (box filter for replaceRegion, generateMipmaps after a buffer copy). Any explicit write to a higher level, or a generateMipmaps call, turns that off for the texture.

**How I tested it** (card, macOS version, what you ran or did)

RTX 5070 Laptop, macOS 26.7.1. Badges show their numbers again, nothing else changed that I could see.

(screenshot of the Dock goes here)
