from .util import *
from .wmb import wmb3_colTreeNode

class COL_Header(object):
	""" fucking header	"""
	def __init__(self, wmb_fp):
		super(COL_Header, self).__init__()
		self.magicNumber = wmb_fp.read(4)										# ID
		if self.magicNumber == b'COL2':
			self.version = "%08x" % (to_int(wmb_fp.read(4)))					# Version
			self.offsetNames = to_int(wmb_fp.read(4))							# Offset to names
			self.nameCount = to_int(wmb_fp.read(4))								# Number of names
			self.offsetMeshes = to_int(wmb_fp.read(4))							# Offset to meshes
			self.meshCount = to_int(wmb_fp.read(4))								# Number of meshes
			self.offsetBoneMap = to_int(wmb_fp.read(4))							# Offset to bone map
			self.boneMapCount = to_int(wmb_fp.read(4))							# Number of bones
			self.offsetBoneMap2 = to_int(wmb_fp.read(4))						# Offset to bone map 2
			self.boneMap2Count = to_int(wmb_fp.read(4))							# Number of bones 2
			self.offsetMeshMap = to_int(wmb_fp.read(4))							# Offset to mesh map
			self.meshMapCount = to_int(wmb_fp.read(4))							# Number of meshes
			self.offsetColTreeNodes = to_int(wmb_fp.read(4))					# Offset to collision tree nodes
			self.colTreeNodesCount = to_int(wmb_fp.read(4))						# Number of collision tree nodes

class COL_Mesh(object):
	def __init__(self, wmb_fp):
		super(COL_Mesh, self).__init__()
		self.flags = to_int(wmb_fp.read(4))										# Flags
		self.nameIndex = to_int(wmb_fp.read(4))									# Name index
		self.batchType = to_int(wmb_fp.read(4))									# Batch type
		self.offset = to_int(wmb_fp.read(4))									# Offset
		self.batchCount = to_int(wmb_fp.read(4))								# Batch count

		for i in range(self.batchCount):
			wmb_fp.seek(self.offset + i * 20)
			if (self.batchType == 2):
				self.batch = COL_BatchV2(wmb_fp)
			elif (self.batchType == 3):
				self.batch = COL_BatchV3(wmb_fp)
			else:
				raise Exception("Unknown batch type: %d" % self.batchType)

class COL_BatchV2(object):
	def __init__(self, wmb_fp):
		super(COL_BatchV2, self).__init__()
		self.boneIndex = to_int(wmb_fp.read(4))									# Bone index
		self.offsetVertices = to_int(wmb_fp.read(4))							# Offset to vertices
		self.vertexCount = to_int(wmb_fp.read(4))								# Number of vertices
		self.offsetIndices = to_int(wmb_fp.read(4))								# Offset to indices
		self.indexCount = to_int(wmb_fp.read(4))								# Number of indices

		self.vertices = []
		wmb_fp.seek(self.offsetVertices)
		for i in range(self.vertexCount):
			self.vertices.append({
				"position": {
					"x": to_float(wmb_fp.read(4)),
					"y": to_float(wmb_fp.read(4)),
					"z": to_float(wmb_fp.read(4)),
					"w": to_float(wmb_fp.read(4))
				}
			})

		self.indices = []
		wmb_fp.seek(self.offsetIndices)
		for i in range(self.indexCount):
			self.indices.append(to_int(wmb_fp.read(2)))

class COL_BatchV3(object):
	def __init__(self, wmb_fp):
		super(COL_BatchV2, self).__init__()
		self.offsetVertices = to_int(wmb_fp.read(4))							# Offset to vertices
		self.vertexCount = to_int(wmb_fp.read(4))								# Number of vertices
		self.offsetIndices = to_int(wmb_fp.read(4))							# Offset to indices
		self.indexCount = to_int(wmb_fp.read(4))								# Number of indices

		self.vertices = []
		wmb_fp.seek(self.offsetVertices)
		for i in range(self.vertexCount):
			self.vertices.append({
				"position": {
					"x": to_float(wmb_fp.read(4)),
					"y": to_float(wmb_fp.read(4)),
					"z": to_float(wmb_fp.read(4)),
					"w": to_float(wmb_fp.read(4))
				},
				"boneWeights": {
					"x": to_float(wmb_fp.read(4)),
					"y": to_float(wmb_fp.read(4)),
					"z": to_float(wmb_fp.read(4)),
					"w": to_float(wmb_fp.read(4))
				},
				"bones": [to_int(wmb_fp.read(4)), to_int(wmb_fp.read(4)), to_int(wmb_fp.read(4)), to_int(wmb_fp.read(4))]
			})
		
		self.indices = []
		wmb_fp.seek(self.offsetIndices)
		for i in range(self.indexCount):
			self.indices.append(to_int(wmb_fp.read(2)))

class COL(object):
	"""COL collision file"""
	def __init__(self, filepath):
		super(COL, self).__init__()

		self.col_fp = open(filepath, 'rb')
		self.col_header = COL_Header(self.col_fp)

		self.col_fp.seek(self.col_header.offsetNames + 16)
		self.nameTable = self.col_fp.read(self.col_header.offsetMeshes - self.col_header.offsetNames - 16).decode("utf-8").split('\0')

		self.meshes = []
		for i in range(self.col_header.meshCount):
			self.col_fp.seek(self.col_header.offsetMeshes + i * 20)
			self.meshes.append(COL_Mesh(self.col_fp))
		

		self.colTreeNodes = []
		if self.col_header.offsetColTreeNodes:
			self.col_fp.seek(self.col_header.offsetColTreeNodes)
			for i in range(self.col_header.colTreeNodesCount):
				self.colTreeNodes.append(wmb3_colTreeNode(self.col_fp))
