# Upstream-ready note: heap textures lose MTLTextureDescriptor.swizzle

Problem: a texture made by `-[MTLHeap newTextureWithDescriptor:]` on an automatic heap ignores the descriptor's
`swizzle`. `nvmtlPlacedTexture:charge:align:` in plugin/NVMTLObjects.m builds the texture without calling
`nvmtl_texture_desc_swizzle`, which the device, buffer, IOSurface and placement-heap paths all call.

Seen as: IconServices symbol layers (RG8, swizzle r,r,r,g) drawn as flat yellow shapes, e.g. System Settings sidebar
icons, on our Intel path. Same code in NullMoth v2.6.2.

Reproduction: RG8Unorm 2x1 texture, pixels (255,255) and (255,0), swizzle (red, red, red, green), from an
`MTLHeapTypeAutomatic` private heap, sampled in a fragment shader. Expected (255,255,255,255) and (255,255,255,0);
got (255,255,0,255) and (255,0,0,255). Test program: `i-120/swz3.m`.

Patch (one line before the final `return t;` of `nvmtlPlacedTexture:charge:align:`):

```objc
    // automatic heaps land here, not in -newTextureWithDescriptor:offset:; without this the descriptor's swizzle was lost
    nvmtl_texture_desc_swizzle(t, d);
```

Parked textures are safe: `-dealloc` destroys `_swzView` before it parks the image.
