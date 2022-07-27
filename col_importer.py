import bpy, bmesh, math
from mathutils import Vector, Matrix
from .col import COL
import os

def main(only_extract = False, col_file = os.path.split(os.path.realpath(__file__))[0] + '\\test\\pl0000.dtt\\pl0000.wmb'):
	#reset_blend()
	col = COL(col_file)
	colname = col_file.split('\\')[-1]

	collection_name = colname[:-4]

	collection = bpy.data.collections.new(collection_name)
	bpy.context.scene.collection.children.link(collection)
	bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]

	for i, mesh in enumerate(col.meshes):
		construct_mesh([col.nameTable[mesh.nameIndex], mesh.batch.vertices, mesh.batch.indices, False], collection_name)
	"""if wmb.hasBone:
		boneArray = [[bone.boneIndex, "bone%d"%bone.boneIndex, bone.parentIndex,"bone%d"%bone.parentIndex, bone.world_position, bone.world_rotation, bone.boneNumber, bone.local_position, bone.local_rotation, bone.world_rotation, bone.world_position_tpose] for bone in wmb.boneArray]
		armature_no_wmb = wmbname.replace('.wmb','')
		armature_name_split = armature_no_wmb.split('/')
		armature_name = armature_name_split[len(armature_name_split)-1] # THIS IS SPAGHETT I KNOW. I WAS TIRED
		construct_armature(armature_name, boneArray, wmb.firstLevel, wmb.secondLevel, wmb.thirdLevel, wmb.boneMap, wmb.boneSetArray)"""


	print('Importing finished. ;)')
	return {'FINISHED'}

def construct_mesh(mesh_data, collection_name):			# [meshName, vertices, faces, has_bone, boneWeightInfoArray, boneSetIndex, meshGroupIndex, vertex_colors, LOD_name, LOD_level, colTreeNodeIndex, unknownWorldDataIndex, boundingBox], collection_name
	name = mesh_data[0]
	for obj in bpy.data.objects:
		if obj.name == name:
			name = name + '-' + collection_name
	rawVertices = mesh_data[1]
	vertices = []
	for vertex in rawVertices:
		# change values to adapt to blender's coordinate system
		vertices.append((vertex['position']['x'], -vertex['position']['z'], vertex['position']['y']))

	facesRaw = [index - 1 for index in mesh_data[2]]
	usedVertexIndexArray = sorted(list(set(facesRaw)))
	mappingDict = {}
	for newIndex in range(len(usedVertexIndexArray)):
		mappingDict[usedVertexIndexArray[newIndex]] = newIndex
	for i in range(len(facesRaw)):
		facesRaw[i] = mappingDict[facesRaw[i]]
	faces = [0] * int(len(facesRaw) / 3)
	for i in range(0, len(facesRaw), 3):
		faces[int(i/3)] = (facesRaw[i]  , facesRaw[i + 1]  , facesRaw[i + 2] )

	has_bone = mesh_data[3]
	weight_infos = [[[],[]]]							# A real fan can recognize me even I am a 2 dimensional array
	print("[+] importing %s" % name)
	objmesh = bpy.data.meshes.new(name)
	if not name in bpy.data.objects.keys(): 
		obj = bpy.data.objects.new(name, objmesh)
	else:
		obj = bpy.data.objects[name]	
	obj.location = Vector((0,0,0))
	bpy.context.collection.objects.link(obj)
	objmesh.from_pydata(vertices, [], faces)
	objmesh.update(calc_edges=True)

if __name__ == '__main__':
	main()