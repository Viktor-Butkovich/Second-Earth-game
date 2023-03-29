import save_load_tools
import utility

def save(input_list, global_manager):
    global_manager.set('current_display_mode', 'browse')
    global_manager.set('displayed_terrain', 'none')
    file_path = global_manager.get('active_file_path')
    save_load_tools.save_terrains(global_manager)
    while len(global_manager.get('terrain_list')) > 0:
        global_manager.get('terrain_list')[0].remove()
    save_load_tools.load_terrains(file_path, global_manager)

def print_terrains(input_list, global_manager):
    if len(input_list) > 1:
        printed_terrain = input_list[1]
        print(utility.get_terrain_by_name(printed_terrain, global_manager))
    else:
        for current_terrain in global_manager.get('terrain_list'):
            print(current_terrain)

def new(input_list, global_manager):
    global_manager.set('displayed_terrain', utility.create_default_terrain(global_manager))
    global_manager.set('current_display_mode', 'terrain_view')

def delete(input_list, global_manager):
    if len(input_list) > 1: #deletes terrain specified in argument
        if input_list[1].isdigit():
            input_list[1] = int(input_list[1])
            if input_list[1] - 1  >= 0 and input_list[1] - 1 < len(global_manager.get('terrain_list')):
                deleted_terrain = global_manager.get('terrain_list')[input_list[1] - 1]
            else:
                deleted_terrain = 'none'
        else:
            deleted_terrain = utility.get_terrain_by_name(input_list[1], global_manager)
        if deleted_terrain == 'none':
            print(str(input_list[1]) + ' is not a terrain')
            return()
        if deleted_terrain == global_manager.get('displayed_terrain'):
            global_manager.set('current_display_mode', 'browse')
            global_manager.set('displayed_terrain', 'none')
        deleted_terrain.remove()
    else:
        print('No terrain was specified')

def list(input_list, global_manager):
    counter = 1
    for current_terrain in global_manager.get('terrain_list'):
        print(str(counter) + '. ' + current_terrain.name)
        counter += 1

def browse(input_list, global_manager):
    global_manager.set('displayed_terrain', 'none')
    global_manager.set('current_display_mode', 'browse')

def select(input_list, global_manager):
    if len(input_list) > 1:
        if input_list[1].isdigit():
            input_list[1] = int(input_list[1])
            if input_list[1] - 1  >= 0 and input_list[1] - 1 < len(global_manager.get('terrain_list')):
                selected_terrain = global_manager.get('terrain_list')[input_list[1] - 1]
            else:
                selected_terrain = 'none'
        else:
            selected_terrain = utility.get_terrain_by_name(input_list[1], global_manager)
        if selected_terrain == 'none':
            print(str(input_list[1]) + ' is not a terrain')
            return()
        global_manager.set('displayed_terrain', selected_terrain)
        global_manager.set('current_display_mode', 'terrain_view')
    else:
        print('No terrain was specified')

def edit(input_list, global_manager):
    edited_parameter = 'none'
    for current_parameter in global_manager.get('parameter_types'):
        if current_parameter[0] == input_list[0]:
            edited_parameter = current_parameter
    displayed_terrain = global_manager.get('displayed_terrain')
    parameter_obj = displayed_terrain.parameter_dict[edited_parameter]
    if len(input_list) == 1:
        parameter_obj.min = 1
        parameter_obj.max = 6
    elif len(input_list) == 2:
        parameter_obj.min = int(input_list[1])
        parameter_obj.max = int(input_list[1])
    elif len(input_list) > 2:
        parameter_obj.min = int(input_list[1])
        parameter_obj.max = int(input_list[2])
    if parameter_obj.max < parameter_obj.min:
        temp = parameter_obj.max
        parameter_obj.min = parameter_obj.max
        parameter_obj.max = temp
    if parameter_obj.min < 1:
        parameter_obj.min = 1
    if parameter_obj.max > 6:
        parameter_obj.max = 6

def edit_point(input_list, global_manager):
    edited_parameter = 'none'
    for current_parameter in global_manager.get('parameter_types'):
        if current_parameter[0] == input_list[0]:
            edited_parameter = current_parameter
    displayed_point = global_manager.get('displayed_point')
    if len(input_list) > 1 and input_list[1].isdigit():
        displayed_point.parameter_dict[edited_parameter] = int(input_list[1])

    if displayed_point.parameter_dict[edited_parameter] < 1:
        displayed_point.parameter_dict[edited_parameter] = 1
    if displayed_point.parameter_dict[edited_parameter] > 6:
        displayed_point.parameter_dict[edited_parameter] = 6   

def rename(input_list, global_manager):
    if len(input_list) > 1:
        global_manager.get('displayed_terrain').name = input_list[1]
    else:
        print('No name was specified')

def select_point(input_list, global_manager):
    if len(global_manager.get('point_list')) > 0:
        global_manager.set('displayed_point', global_manager.get('point_list')[0])
    else:
        global_manager.set('displayed_point', utility.create_default_point(global_manager))
    global_manager.set('current_display_mode', 'point_view')
