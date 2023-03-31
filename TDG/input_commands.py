import save_load_tools
import utility
import math

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
        input_list.pop(0)
        for current_input in input_list:
            print(utility.get_terrain_by_name(current_input, global_manager))
    else:
        for current_terrain in global_manager.get('terrain_list'):
            print(current_terrain)

def new(input_list, global_manager):
    if len(global_manager.get('point_list')) > 0:
        last_point = global_manager.get('point_list')[0]
        new_terrain = utility.create_terrain(global_manager, last_point.parameter_dict)
    else:
        new_terrain = utility.create_terrain(global_manager)
    global_manager.set('displayed_terrain', new_terrain)
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
    if len(input_list) == 1 + len(global_manager.get('parameter_types')):
        parameter_dict = {}
        index = 0
        for current_parameter in global_manager.get('parameter_types'):
            index += 1
            if input_list[index].isdigit():
                parameter_dict[current_parameter] = int(input_list[index])
            else:
                parameter_dict[current_parameter] = 1
        selected_point = utility.create_point(global_manager, parameter_dict)

    elif len(global_manager.get('point_list')) > 0:
        selected_point = global_manager.get('point_list')[0]
    else:
        selected_point = utility.create_point(global_manager)
    global_manager.set('displayed_point', selected_point)
    global_manager.set('current_display_mode', 'point_view')

def select_next_point(input_list, global_manager):
    terrain_dict = {}
    starting_points = []
    parameter_types = global_manager.get('parameter_types')
    for current_parameter in parameter_types:
        if global_manager.get('displayed_point') == 'none':
            starting_points.append(0)
        else:
            starting_points.append(global_manager.get('displayed_point').parameter_dict[current_parameter])
        terrain_dict[current_parameter] = starting_points[-1]

    #starts from current point
    for a in range(starting_points[0], 6):
        terrain_dict[parameter_types[0]] = a + 1
        for b in range(starting_points[1], 6):
            terrain_dict[parameter_types[1]] = b + 1
            for c in range(starting_points[2], 6):
                terrain_dict[parameter_types[2]] = c + 1
                for d in range(starting_points[3], 6):
                    terrain_dict[parameter_types[3]] = d + 1
                    for e in range(starting_points[4], 6):
                        terrain_dict[parameter_types[4]] = e + 1
                        current_terrain = utility.get_terrain(terrain_dict, global_manager)
                        if current_terrain == 'none':
                            terrain_dict['init_type'] = 'point'
                            global_manager.set('displayed_point', global_manager.get('actor_creation_manager').create(terrain_dict, global_manager))
                            global_manager.set('current_display_mode', 'point_view')
                            return(global_manager.get('displayed_point'))
                
    #restarts from (1, 1, 1, 1, 1) if no empty points are found
    for a in range(starting_points[0]):
        terrain_dict[parameter_types[0]] = a + 1
        for b in range(starting_points[1]):
            terrain_dict[parameter_types[1]] = b + 1
            for c in range(starting_points[2]):
                terrain_dict[parameter_types[2]] = c + 1
                for d in range(starting_points[3]):
                    terrain_dict[parameter_types[3]] = d + 1
                    for e in range(starting_points[4]):
                        terrain_dict[parameter_types[4]] = e + 1
                        current_terrain = utility.get_terrain(terrain_dict, global_manager)
                        if current_terrain == 'none':
                            terrain_dict['init_type'] = 'point'
                            global_manager.set('displayed_point', global_manager.get('actor_creation_manager').create(terrain_dict, global_manager))
                            global_manager.set('current_display_mode', 'point_view')
                            return(global_manager.get('displayed_point'))
    return('none')
    
def select_first_overlap(input_list, global_manager):
    terrain_dict = {}
    parameter_types = global_manager.get('parameter_types')
    for a in range(6):
        terrain_dict[parameter_types[0]] = a + 1
        for b in range(6):
            terrain_dict[parameter_types[1]] = b + 1
            for c in range(6):
                terrain_dict[parameter_types[2]] = c + 1
                for d in range(6):
                    terrain_dict[parameter_types[3]] = d + 1
                    for e in range(6):
                        terrain_dict[parameter_types[4]] = e + 1
                        matching_terrains = utility.get_all_terrains(terrain_dict, global_manager)
                        matching_terrain_names = []
                        if len(matching_terrains) > 1:
                            for current_terrain in matching_terrains:
                                matching_terrain_names.append(current_terrain.name)
                            print('Overlapping terrains: ' + utility.comma_list(matching_terrain_names))
                            terrain_dict['init_type'] = 'point'
                            global_manager.set('displayed_point', global_manager.get('actor_creation_manager').create(terrain_dict, global_manager))
                            global_manager.set('current_display_mode', 'point_view')
                            return(global_manager.get('displayed_point'))
    global_manager.set('current_display_mode', 'browse')
    print('No overlap')
    return('none')
        
def check_point_overlap(input_list, global_manager):
    displayed_point = global_manager.get('displayed_point')
    matching_terrains = utility.get_all_terrains(displayed_point.parameter_dict, global_manager)
    matching_terrain_names = []
    if len(matching_terrains) > 1:
        for current_terrain in matching_terrains:
            matching_terrain_names.append(current_terrain.name)
        print('Overlapping terrains: ' + utility.comma_list(matching_terrain_names))
    else:
        print('No overlap')

def volume_summary(input_list, global_manager):
    total_volume = 0
    possible_volume = 6 ** len(global_manager.get('parameter_types'))
    for current_terrain in global_manager.get('terrain_list'):
        current_volume = current_terrain.volume()
        current_line = current_terrain.name.capitalize() + ': ' + str(current_volume) + '/' + str(possible_volume) + ' ('
        current_line += str(math.floor(current_volume/possible_volume * 100 * 100)/100) + '%)'
        print(current_line)
        total_volume += current_volume
    print()
    unused_volume = possible_volume - total_volume
    current_line = 'Undefined: ' + str(unused_volume) + '/' + str(possible_volume) + ' ('
    current_line += str(math.floor(unused_volume/possible_volume * 100 * 100)/100) + '%)'
    print(current_line)

def copy_terrain(input_list, global_manager):
    current_terrain = global_manager.get('displayed_terrain')
    input_dict = current_terrain.to_save_dict()
    input_dict['name'] += 'Copy'
    input_dict['init_type'] = 'terrain'
    new_terrain = global_manager.get('actor_creation_manager').create(input_dict, global_manager)
    global_manager.set('displayed_terrain', new_terrain)
    return(new_terrain)
