
Fork of Cabalex's [AstralChain2Blender](https://github.com/cabalex/AstralChain2Blender) which was a fork of WoefulWolf's [NieR2Blender 2.8](https://github.com/WoefulWolf/NieR2Blender_2_8) repository that adds NieR Switch support.

## IMPORTANT

**This is pretty much a temporary fork.** I don't really expect to update it that much and this functionality might be merged with the other NieR Blender plugins at some point.

<br>

## Why does the original add-on not work with NieR Switch's files?
Astral Chain and NieR internally use different specifications for their textures in the "Texture Info" table. While Astral Chain's textures are notated by `XT1\x00`, NieR Switch notates its textures with `.tex` and has a completely different format for how texture info is laid out. It also trims a lot of information, like surface type, texture layout, etc... while simultaneously taking up more space (each texture info item takes up 100 bytes, despite most of it being empty?)
<br>
NieR also seems to use ASTC_6x6, while Astral Chain doesn't, for some reason.

## Why does the *original* original add-on not work with Astral Chain's files?
While the model format and much of the .DAT/.DTT format are similar, if not identical, the texture formats are completely different. Since Astral Chain is made for the Switch, while NieR isn't, it relies on a different texture compression method known as ASTC for many of its textures. ASTC and NieR's texture format (.DDS) are not compatible, and hence the original addon doesn't load textures properly when importing a model from Astral Chain. Along with this, the Switch swizzles its textures, so the textures from AC must be unswizzled in order to be used. This add-on (in theory) should fix this.
<br>
There are some other differences (the last file table in the .WTA, the way .DAT/.DTTs are packed, how header data is dealt with, etc), but those are the main points.
<br>


## Notable things
* The add-on converts ASTC to PNG; thus, it can be quite slow to load a model. I'd probably recommend other methods if you're just browsing through the models.
* I haven't tested it on that many models, so there will probably be errors.
* This plugin should probably still work on Astral Chain models and NieR models, but that hasn't really been tested.

### Some credits/ported code
* [WoefulWolf](https://github.com/WoefulWolf) and other contributors to [Nier2Blender](https://github.com/WoefulWolf/NieR2Blender_2_8) and [NieR2Blender2NieR](https://github.com/WoefulWolf/NieR2Blender2NieR)
* [aboood40091's BNTX-Extractor](https://github.com/aboood40091/BNTX-Extractor)
* [KillzXGaming's Switch Toolbox](https://github.com/KillzXGaming/Switch-Toolbox)
* The [ASTC Encoder](https://github.com/ARM-software/astc-encoder) included