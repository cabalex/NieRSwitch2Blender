![Nier2Blender](https://user-images.githubusercontent.com/54476280/64488614-519a7280-d24a-11e9-8627-784cdc5ac3de.png)
<br>
**CURRENTLY DOES NOT WORK WITH Blender2NieR** - I'm working on a separate Blender2NieR fork that will fix this (as the current .WTA/.WTP system, along with the .DAT/.DTT repacking, are not compatible with Astral Chain)

<br>

Fork of WoefulWolf's [Nier2Blender 2.8](https://github.com/WoefulWolf/NieR2Blender_2_8) repository that adds Astral Chain support (I guess you could call it AstralChain2Blender?)

<br>

## Why does the original add-on not work with Astral Chain's files?
While the model format and much of the .DAT/.DTT format are similar, if not identical, the texture formats are completely different. Since Astral Chain is made for the Switch, while NieR isn't, it relies on a different texture compression method known as ASTC for many of its textures. ASTC and NieR's texture format (.DDS) are not compatible, and hence the original addon doesn't load textures properly when importing a model from Astral Chain. Along with this, the Switch swizzles its textures, so the textures from AC must be unswizzled in order to be used. This add-on (in theory) should fix this.
<br>


## Notable things
* Some Astral Chain models have DDS textures on them, most notably being the Legion's police branding. While this add-on fixes the header data and allows for loading, it sets an invalid fourCC (DXT4) which Blender does not know how to read, so it falls back to uncompressed. However, setting it to DXT5 (which is what the textures are in) immediately crashes Blender on some models (e.x. the Sword Legion, em00a0). There may be something invalid with my texture loading, but uncompressed textures "work" for now.
* The add-on converts the ASTC textures to PNG. The only encoder/decoder I could find that converts from ASTC to DDS only converts to DX10, which Blender and the game do not support. There's probably a better method out there, but I just haven't found one. This may cause issues with mipmaps later down the line, however (although I'm fairly certain the EXE included can encode ASTC mipmaps dynamically).
* I include `astcenc-avx2.exe` from the [ASTC Encoder](https://github.com/ARM-software/astc-encoder) for decoding ASTC textures, which might not be compatible with many systems. If it doesn't work, you can try replacing the EXE with one that does. The EXE is called in `wmb_importer.py` around line ~598.
* Exporting to OBJ/FBX "works", but I have not modified the existing code there. It probably needs to be changed to include PNG support, but it doesn't throw any errors in my testing (?). 
* I rely on some libraries that probably don't need to be imported.
* This addon should still work with NieR models, but I'm not completely sure as I do not own NieR.
* My code probably isn't that great, and is definitely not optimized. Sorry :/

### Some credits/ported code
* [aboood40091's BNTX-Extractor](https://github.com/aboood40091/BNTX-Extractor)
* [KillzXGaming's Switch Toolbox](https://github.com/KillzXGaming/Switch-Toolbox)
* The [ASTC Encoder](https://github.com/ARM-software/astc-encoder) included

<br>![Sword Legion](https://user-images.githubusercontent.com/31020729/113498031-19a6f000-94be-11eb-9092-45f519d64c57.png)

* Some useful folders in pkz [(main documentation here)](https://cabalex.github.io/astral-chain-romfs/romfs/index.html)<br>
    /pl -> human models<br>
    /wp -> weapon models<br>
    /ba /bg /bh -> environment models<br>
    /em -> chimera/legion models<br>
