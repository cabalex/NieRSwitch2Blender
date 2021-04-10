import os
import sys
from .util import *
from .tegrax1swizzle import *
from struct import unpack, pack


class DDSHeader(object):
	# https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-header
	class DDSPixelFormat(object):
		def __init__(self, pixelFormat):
			self.size = 32
			self.flags = 4 # contains fourcc
			self.fourCC = b'DXT5' # Blender supports DXT1, DXT3, DXT5 [probably make this detected by something oops]
			# "DXT1 for normal texture, DX5 with alpha" [DXT5 reccommended]
			# I guess my textures are invalid?? If I load them compressed then Blender just crashes
			# but they work uncompressed (setting fourCC to something invalid) for some reason
			self.RGBBitCount = 0
			self.RBitMask = 0x00000000
			self.GBitMask = 0x00000000
			self.BBitMask = 0x00000000
			self.ABitMask = 0x00000000

	def __init__(self, texture):
		self.magic = b'DDS\x20'
		self.size = 124
		self.flags = 0x1 + 0x2 + 0x4 + 0x1000 + 0x20000 + 0x80000 # Defaults (caps, height, width, pixelformat) + mipmapcount and linearsize
		self.height = texture.height
		self.width = texture.width
		if texture._format == "R8G8B8A8_UNORM":
			self.pitchOrLinearSize = ((width + 1) >> 1) * 4
		else:
			self.pitchOrLinearSize = int(max(1, ((texture.width+3)/4) ) * returnFormatTable(texture._format)[0]) # https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide
		self.depth = texture.depth
		self.mipmapCount = 1#texture.mipCount # Setting this to the normal value breaks everything, don't do that
		self.reserved1 = [0x00000000] * 11
		self.ddspf = self.DDSPixelFormat(texture)
		self.caps = 4198408 # Defaults (DDSCAPS_TEXTURE) + mipmap and complex
		self.caps2 = 0 
		self.caps3 = 0
		self.caps4 = 0
		self.reserved2 = 0

	def save(self):
		return self.magic + pack("20I4s10I", self.size, self.flags, self.height, self.width, self.pitchOrLinearSize, self.depth,
			self.mipmapCount, self.reserved1[0], self.reserved1[1], self.reserved1[2], self.reserved1[3], self.reserved1[4],
			self.reserved1[5], self.reserved1[6], self.reserved1[7], self.reserved1[8], self.reserved1[9], self.reserved1[10],
			self.ddspf.size, self.ddspf.flags, self.ddspf.fourCC, self.ddspf.RGBBitCount, self.ddspf.RBitMask, self.ddspf.GBitMask,
			self.ddspf.BBitMask, self.ddspf.ABitMask, self.caps, self.caps2, self.caps3, self.caps4, self.reserved2)


class AstralChainTexture(object):
	def __init__(self, unpacked):
		formats = {
			0x25: "R8G8B8A8_UNORM",
			0x42: "BC1_UNORM",
			0x43: "BC2_UNORM",
			0x44: "BC3_UNORM",
			0x45: "BC4_UNORM",
			0x46: "BC1_UNORM_SRGB",
			0x47: "BC2_UNORM_SRGB",
			0x48: "BC3_UNORM_SRGB",
			0x49: "BC4_SNORM",
			0x50: "BC6H_UF16",
			0x79: "ASTC_4x4_UNORM",
			0x80: "ASTC_8x8_UNORM",
			0x87: "ASTC_4x4_SRGB",
			0x8E: "ASTC_8x8_SRGB"
		}
		self.magic = unpacked[0]
		self.unknown = unpacked[1]
		self.imageSize = [unpacked[2], unpacked[3]]
		self.headerSize = unpacked[4]
		self.mipCount = unpacked[5]
		self._typeval = unpacked[6]
		self._formatval = unpacked[7]
		self.width = unpacked[8]
		self.height = unpacked[9]
		self.depth = unpacked[10]
		self.unknown4 = unpacked[11]
		self.textureLayout = unpacked[12]
		self.textureLayout2 = unpacked[13]
		self.arrayCount = 1
		surfaceTypes = ["T_1D", "T_2D", "T_3D", "T_Cube", "T_1D_Array", "T_2D_Array", "T_2D_Multisample", "T_2D_Multisample_Array", "T_Cube_Array"]
		self._format = formats[self._formatval]
		self._type = surfaceTypes[self._typeval]
		if self._type in ["T_Cube", "T_Cube_Array"]:
			self.ArrayCount = 6

	def save(self):
		return [pack("<4s13I", self.magic, self.unknown, self.imageSize[0], self.imageSize[1], self.headerSize, self.mipCount, self._typeval,
			self._formatval, self.width, self.height, self.depth, self.unknown4, self.textureLayout, self.textureLayout2), self.identifier]

	def getImageData(self, textureData):
		blockHeightLog2 = self.textureLayout & 7
		texture = getImageData(self, textureData, 0, 0, 0, blockHeightLog2, 1)
		print(f"Loaded texture {self.identifier} ({self._format})")
		if self._format.startswith("ASTC"): # Texture is ASTC
			print(f"[!] This texture ({self.identifier}) is ASTC, and hence must be converted to be used in Blender.")
			formatInfo = returnFormatTable(self._format)
			outBuffer = b''.join([
						b'\x13\xAB\xA1\x5C', formatInfo[1].to_bytes(1, "little"),
						formatInfo[2].to_bytes(1, "little"), b'\1',
						self.width.to_bytes(3, "little"),
						self.height.to_bytes(3, "little"), b'\1\0\0',
						texture,
					])
			return outBuffer, True
		else: # Texture is DDS
			# must generate header data to add onto the beginning
			print(f"Adding header Data to {self.identifier}")
			headerDataObject = DDSHeader(self)
			headerData = headerDataObject.save()
			finalTexture = headerData + texture
			return finalTexture, False

class WTA(object):
	def __init__(self, wta_fp):
		super(WTA, self).__init__()
		self.magicNumber = wta_fp.read(4)
		self.game = "NIER"
		if self.magicNumber == b'WTB\x00':
			self.unknown04 = to_int(wta_fp.read(4))
			self.textureCount = to_int(wta_fp.read(4))
			self.textureOffsetArrayOffset = to_int(wta_fp.read(4))
			self.textureSizeArrayOffset = to_int(wta_fp.read(4))
			self.unknownArrayOffset1 = to_int(wta_fp.read(4))
			self.textureIdentifierArrayOffset = to_int(wta_fp.read(4))
			self.unknownArrayOffset2 = to_int(wta_fp.read(4)) # main table?
			self.wtaTextureOffset = [0] * self.textureCount
			self.wtaTextureSize = [0] * self.textureCount
			self.wtaTextureIdentifier = [0] * self.textureCount
			self.unknownArray1 = [0] * self.textureCount
			self.unknownArray2 = [] 
			for i in range(self.textureCount):
				wta_fp.seek(self.textureOffsetArrayOffset + i * 4)
				self.wtaTextureOffset[i] = to_int(wta_fp.read(4))
				wta_fp.seek(self.textureSizeArrayOffset + i * 4)
				self.wtaTextureSize[i] =  to_int(wta_fp.read(4)) 
				wta_fp.seek(self.textureIdentifierArrayOffset + i * 4)
				self.wtaTextureIdentifier[i] = "%08x"%to_int(wta_fp.read(4))
				wta_fp.seek(self.unknownArrayOffset1 + i * 4)
				self.unknownArray1[i] = "%08x"%to_int(wta_fp.read(4))
			wta_fp.seek(self.unknownArrayOffset2 )
			unknownval =  (wta_fp.read(4))
			if unknownval == b'XT1\x00':
				self.game = "ASTRALCHAIN" # AC uses XT1 textures; it is explicitly defined here
				# Thanks to https://github.com/KillzXGaming/Switch-Toolbox/blob/604f7b3d369bc97d9d05632da3211ed11b990ba7/File_Format_Library/FileFormats/Texture/WTB.cs
				print('! Loading an Astral Chain WTA file')
				wta_fp.seek(wta_fp.tell()-4)
				
				self.ACTextures = []
				for i in range(self.textureCount):
					tex = AstralChainTexture(unpack("<4s13I", wta_fp.read(56)))
					tex.identifier = self.wtaTextureIdentifier[i]
					self.ACTextures.append(tex)
				self.pointer2 = hex(wta_fp.tell())
				self.textureHeader_metadata = b'' # This may need to change in the future
				"""
				ac_texture_header.metadata -
				- texture identifier offset
				- number of textures
				> WTA texture header table
				> WTA texture identifier table
				"""
				textureOutputs = [t.save() for t in self.ACTextures]
				for i in range(self.textureCount):
					self.textureHeader_metadata += textureOutputs[i][0] # Might need to save file name?
				textureNameOffset = len(self.textureHeader_metadata) + 4
				for i in range(self.textureCount):
					self.textureHeader_metadata += pack("8s", bytes(textureOutputs[i][1], 'ascii'))
				self.textureHeader_metadata = pack("<2I", textureNameOffset, self.textureCount) + self.textureHeader_metadata
			else:
				while unknownval:
					self.unknownArray2.append(to_int(unknownval))
					unknownval =  (wta_fp.read(4))
				self.pointer2 = hex(wta_fp.tell())


	def getTextureByIndex(self, texture_index, texture_fp):
		texture_fp.seek(self.wtaTextureOffset[texture_index])
		texture = texture_fp.read(self.wtaTextureSize[texture_index])
		if self.game == "ASTRALCHAIN":
			# Get image data from class
			return self.ACTextures[texture_index].getImageData(texture)
		return texture, False

	def getTextureByIdentifier(self, textureIdentifier, texture_fp):
		for index in range(self.textureCount):
			if self.wtaTextureIdentifier[index] == textureIdentifier:
				return self.getTextureByIndex(index,texture_fp)
		return False