extends Node
class_name ObjectPool

var _pool: Dictionary = {} # Key: Scene Path, Value: Array of Nodes
var _parent_node: Node

func _init(parent: Node) -> void:
	_parent_node = parent

## Get an object from the pool, or instantiate a new one if empty
func get_object(scene_path: String) -> Node:
	if not _pool.has(scene_path):
		_pool[scene_path] = []
	
	var pool_array: Array = _pool[scene_path]
	if pool_array.is_empty():
		var scene = load(scene_path) as PackedScene
		var instance = scene.instantiate()
		_parent_node.add_child(instance)
		return instance
	else:
		var instance = pool_array.pop_back()
		if not is_instance_valid(instance):
			# If instance was freed externally, create new
			return get_object(scene_path)
		
		instance.visible = true
		instance.set_process(true)
		instance.set_physics_process(true)
		if instance.has_method("reset"):
			instance.reset()
		return instance

## Return an object to the pool
func return_object(instance: Node, scene_path: String) -> void:
	if not _pool.has(scene_path):
		_pool[scene_path] = []
	
	instance.visible = false
	instance.set_process(false)
	instance.set_physics_process(false)
	# Instead of queue_free, we keep it active but hidden/disabled
	
	# Optional: Move to a "Pool" position far away
	if instance is Node3D:
		instance.global_position = Vector3(0, -100, 0)
		
	_pool[scene_path].append(instance)
