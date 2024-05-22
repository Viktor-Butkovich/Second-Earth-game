from . import terrains
import json

def load_terrains(file_path, global_manager):
    global_manager.set('active_file_path', file_path)

    active_file = open(global_manager.get('active_file_path'))
    global_manager.set('active_file', active_file)

    terrains_dict = json.load(active_file) #dictionary of terrain name keys and terrain dict values for each terrain
    for current_terrain_dict in terrains_dict: #create terrain with stored terrain dict
        terrains.terrain(terrains_dict[current_terrain_dict], global_manager)

def save_terrains(global_manager):
    terrains_dict = {}
    global_manager.get('active_file').close()
    for current_terrain in global_manager.get('terrain_list'):
        terrains_dict[current_terrain.name] = current_terrain.to_save_dict()
    with open(global_manager.get('active_file_path'), 'w') as f:
        json.dump(terrains_dict, f, indent=4)
