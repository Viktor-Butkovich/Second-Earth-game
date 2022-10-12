#Contains functions used in the game's main loop and event management

import pygame
import time
from . import scaling
from . import text_tools
from . import actor_utility
from . import minister_utility
from . import utility

def update_display(global_manager):
    '''
    Description:
        Draws all images and shapes and calls the functions to draw tooltips and the text box
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    actor_utility.order_actor_info_display(global_manager, global_manager.get('mob_ordered_label_list'), global_manager.get('mob_ordered_list_start_y')) #global manager, list to order, top y of list
    actor_utility.order_actor_info_display(global_manager, global_manager.get('tile_ordered_label_list'), global_manager.get('tile_ordered_list_start_y'))
    actor_utility.order_actor_info_display(global_manager, global_manager.get('minister_ordered_label_list'), global_manager.get('minister_ordered_list_start_y'))
    if global_manager.get('loading'):
        global_manager.set('loading_start_time', global_manager.get('loading_start_time') - 1) #makes it faster if the program starts repeating this part
        draw_loading_screen(global_manager)
    else:
        global_manager.get('game_display').fill((125, 125, 125))
        possible_tooltip_drawers = []

        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                current_grid.draw()

        for current_image in global_manager.get('image_list'):
            current_image.has_drawn = False

        for current_background_image in global_manager.get('background_image_list'):
            current_background_image.draw()
            current_background_image.has_drawn = True
            
        for current_tile in global_manager.get('tile_list'):
            if global_manager.get('current_game_mode') in current_tile.image.modes and not current_tile in global_manager.get('overlay_tile_list'):
                current_tile.image.draw()
                current_tile.image.has_drawn = True

        for current_infrastructure_connection in global_manager.get('infrastructure_connection_list'): #draw roads above terrain and below building icons, which are drawn below mobs
            current_infrastructure_connection.draw()
            current_infrastructure_connection.has_drawn = True

        for current_slums in global_manager.get('slums_list'): #slums appear under other buildings
            for current_image in current_slums.images:
                current_image.draw()
                current_image.has_drawn = True

        mob_image_list = []
        for current_image in global_manager.get('image_list'):
            if not current_image.has_drawn:
                if global_manager.get('current_game_mode') in current_image.modes:
                    if not current_image.image_type == 'mob':
                        current_image.draw()
                        current_image.has_drawn = True
                    else:
                        mob_image_list.append(current_image)

        for current_image in mob_image_list:
            current_image.draw()
            current_image.has_drawn = True
                
        for current_overlay_tile in global_manager.get('overlay_tile_list'):
            if global_manager.get('current_game_mode') in current_overlay_tile.image.modes:
                current_overlay_tile.image.draw()
                current_overlay_tile.image.has_drawn = True
                
        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                current_grid.draw_grid_lines()

        displayed_tile = global_manager.get('displayed_tile')
        if not displayed_tile == 'none':
            displayed_tile.draw_actor_match_outline(False)

        for current_mob in global_manager.get('mob_list'):
            for current_image in current_mob.images:
                if current_mob.selected and global_manager.get('current_game_mode') in current_image.modes:
                    current_mob.draw_outline()
            #if current_mob.veteran:
            for current_status_icon in current_mob.status_icons:
                current_status_icon.image.has_drawn = False #may have been drawn already but draw on top of other images
                current_status_icon.image.draw()
                current_status_icon.image.has_drawn = True
            if current_mob.can_show_tooltip():
                for same_tile_mob in current_mob.images[0].current_cell.contained_mobs:
                    if same_tile_mob.can_show_tooltip() and not same_tile_mob in possible_tooltip_drawers: #if multiple mobs are in the same tile, draw their tooltips in order
                        possible_tooltip_drawers.append(same_tile_mob)

        for current_building in global_manager.get('building_list'):
            if current_building.can_show_tooltip():
                possible_tooltip_drawers.append(current_building)
            
        for current_actor in global_manager.get('actor_list'):
            if current_actor.can_show_tooltip() and not current_actor in possible_tooltip_drawers:
                possible_tooltip_drawers.append(current_actor) #only one of these will be drawn to prevent overlapping tooltips

        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                for current_cell in current_grid.cell_list:
                    current_cell.show_num_mobs()

        for current_button in global_manager.get('button_list'):
            if not (current_button in global_manager.get('button_list') and current_button.in_notification): #notifications are drawn later
                current_button.draw()
                if current_button.can_show_tooltip(): #while multiple actor tooltips can be shown at once, if a button tooltip is showing no other tooltips should be showing
                    possible_tooltip_drawers = [current_button]
                
        for current_label in global_manager.get('label_list'):
            if not (current_label in global_manager.get('button_list') and current_label.in_notification):
                current_label.draw()

        for current_free_image in global_manager.get('free_image_list'):
            if current_free_image.to_front: #draw on top if free image should be in front
                current_free_image.has_drawn = False
                current_free_image.draw()
                current_free_image.has_drawn = True
            if current_free_image.can_show_tooltip():
                possible_tooltip_drawers = [current_free_image]

        for current_button in global_manager.get('button_list'): #draws notifications and buttons attached to notifications
            if current_button.in_notification and not current_button == global_manager.get('current_instructions_page'):
                current_button.draw()
                if current_button.can_show_tooltip(): #while multiple actor tooltips can be shown at once, if a button tooltip is showing no other tooltips should be showing
                    possible_tooltip_drawers = [current_button]#notifications have priority over buttons and will be shown first
                
        if global_manager.get('show_text_box'):
            draw_text_box(global_manager)

        global_manager.get('mouse_follower').draw()
            
        if not global_manager.get('current_instructions_page') == 'none':
            instructions_page = global_manager.get('current_instructions_page')
            instructions_page.draw()
            if instructions_page.can_show_tooltip(): #while multiple actor tooltips can be shown at once, if a button tooltip is showing no other tooltips should be showing
                possible_tooltip_drawers = [instructions_page]#instructions have priority over everything
        if not (global_manager.get('old_mouse_x'), global_manager.get('old_mouse_y')) == pygame.mouse.get_pos():
            global_manager.set('mouse_moved_time', time.time())
            old_mouse_x, old_mouse_y = pygame.mouse.get_pos()
            global_manager.set('old_mouse_x', old_mouse_x)
            global_manager.set('old_mouse_y', old_mouse_y)
        if time.time() > global_manager.get('mouse_moved_time') + 0.15:#show tooltip when mouse is still
            manage_tooltip_drawing(possible_tooltip_drawers, global_manager)
        pygame.display.update()

def check_if_minister_appointed(minister_type, global_manager):
    '''
    Description:
        Checks if there is a minister appointed in the inputted office and prints a warning if there is not one, used to explain why the player can't do an action
    Input:
        string minister_type: minister office to check the occupancy of, like "Minister of Trade"
    Output:
        boolean: Returns whether there is a minister appointed in the inputted office
    '''
    if not global_manager.get('current_ministers')[minister_type] == 'none':
        return(True)
    else:
        keyword = global_manager.get('minister_type_dict')[minister_type]
        text_tools.print_to_screen("", global_manager)
        text_tools.print_to_screen("You can not do " + keyword + " actions because a " + minister_type + " has not been appointed", global_manager)
        text_tools.print_to_screen("Press q or the button in the upper left corner of the screen to manage your ministers", global_manager)
        return(False)

def action_possible(global_manager):
    '''
    Description:
        Because of this function, ongoing events such as trading, exploring, and clicking on a movement destination prevent actions such as pressing buttons from being done except when required by the event
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        boolean: Returns False if the player is in an ongoing event that prevents other actions from being taken, otherwise returns True
    '''
    if global_manager.get('ongoing_exploration'):
        return(False)
    elif global_manager.get('ongoing_trade'):
        return(False)
    elif global_manager.get('ongoing_religious_campaign'):
        return(False)
    elif global_manager.get('ongoing_public_relations_campaign'):
        return(False)
    elif global_manager.get('ongoing_advertising_campaign'):
        return(False)
    elif global_manager.get('ongoing_loan_search'):
        return(False)
    elif global_manager.get('ongoing_conversion'):
        return(False)
    elif global_manager.get('ongoing_construction'):
        return(False)
    elif global_manager.get('ongoing_combat'):
        return(False)
    elif global_manager.get('ongoing_trial'):
        return(False)
    elif global_manager.get('ongoing_slave_capture'):
        return(False)
    elif global_manager.get('game_over'):
        return(False)
    elif global_manager.get('making_choice'):
        return(False)
    elif not global_manager.get('player_turn'):
        return(False)
    elif global_manager.get('choosing_destination'):
        return(False)
    elif global_manager.get('choosing_advertised_commodity'):
        return(False)
    elif global_manager.get('making_choice'):
        return(False)
    elif global_manager.get('drawing_automatic_route'):
        return(False)
    return(True)

def draw_loading_screen(global_manager):
    '''
    Description:
        Draws the loading screen, occupying the entire screen and blocking objects when the game is loading
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('game_display').fill((125, 125, 125))
    global_manager.get('loading_image').draw()
    pygame.display.update()    
    if global_manager.get('loading_start_time') + 1.01 < time.time():#max of 1 second, subtracts 1 in update_display to lower loading screen showing time
        global_manager.set('loading', False)

def manage_tooltip_drawing(possible_tooltip_drawers, global_manager):
    '''
    Description:
        Decides whether each of the inputted objects should have their tooltips drawn based on if they are covered by other objects. The tooltip of each chosen object is drawn in order with correct placement and spacing
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        object list possible_tooltip_drawers: All objects that possess tooltips and are currently touching the mouse and being drawn
    Output:
        None
    '''
    possible_tooltip_drawers_length = len(possible_tooltip_drawers)
    font_size = scaling.scale_width(global_manager.get('font_size'), global_manager)
    y_displacement = scaling.scale_width(30, global_manager) #estimated mouse size
    x_displacement = 0
    if possible_tooltip_drawers_length == 0:
        return()
    elif possible_tooltip_drawers_length == 1:
        height = y_displacement
        height += font_size
        for current_text_line in possible_tooltip_drawers[0].tooltip_text:
            height += font_size
        possible_tooltip_drawers[0].update_tooltip()
        width = possible_tooltip_drawers[0].tooltip_box.width
        mouse_x, mouse_y = pygame.mouse.get_pos()
        below_screen = False
        beyond_screen = False
        if (global_manager.get('display_height') + 10 - mouse_y) - height < 0:
            below_screen = True
        if mouse_x + width > global_manager.get('display_width'):
            beyond_screen = True
        possible_tooltip_drawers[0].draw_tooltip(below_screen, beyond_screen, height, width, y_displacement)
    else:
        stopping = False
        height = y_displacement
        width = 0
        for possible_tooltip_drawer in possible_tooltip_drawers:
            if possible_tooltip_drawer == global_manager.get('current_instructions_page'):
                height += font_size
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    height += font_size
                width = possible_tooltip_drawer.tooltip_box.width
                stopping = True
            if (possible_tooltip_drawer in global_manager.get('button_list') and possible_tooltip_drawer.in_notification) and not stopping:
                height += font_size
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    height += font_size
                width = possible_tooltip_drawer.tooltip_box.width
                stopping = True
        if not stopping:
            for possible_tooltip_drawer in possible_tooltip_drawers:
                height += font_size
                if possible_tooltip_drawer.tooltip_box.width > width:
                    width = possible_tooltip_drawer.tooltip_box.width
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    height += font_size

        mouse_x, mouse_y = pygame.mouse.get_pos()
        below_screen = False #if goes below bottom side
        beyond_screen = False #if goes beyond right side
        if (global_manager.get('display_height') + 10 - mouse_y) - height < 0:
            below_screen = True
        if mouse_x + width > global_manager.get('display_width'):
            beyond_screen = True
        
        stopping = False
        for possible_tooltip_drawer in possible_tooltip_drawers:
            if possible_tooltip_drawer == global_manager.get('current_instructions_page'):
                possible_tooltip_drawer.draw_tooltip(below_screen, beyond_screen, height, width, y_displacement)
                y_displacement += scaling.unscale_width(font_size, global_manager)
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    y_displacement += scaling.unscale_width(font_size, global_manager)
                stopping = True
            if (possible_tooltip_drawer in global_manager.get('button_list') and possible_tooltip_drawer.in_notification) and not stopping:
                possible_tooltip_drawer.draw_tooltip(below_screen, beyond_screen, height, width, y_displacement)
                y_displacement += scaling.unscale_width(font_size, global_manager)
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    y_displacement += scaling.unscale_width(font_size, global_manager)
                stopping = True
                
        if not stopping:
            for possible_tooltip_drawer in possible_tooltip_drawers:
                possible_tooltip_drawer.draw_tooltip(below_screen, beyond_screen, height, width, y_displacement)
                y_displacement += scaling.unscale_width(font_size, global_manager)
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    y_displacement += scaling.unscale_width(font_size, global_manager)

def draw_text_box(global_manager):
    '''
    Description:
        Draws the text input and output box at the bottom left of the screen along with the text it contains
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    greatest_width = scaling.scale_width(300, global_manager)
    max_screen_lines = (scaling.scale_height(global_manager.get('default_display_height') // global_manager.get('font_size'), global_manager)) - 1
    max_text_box_lines = (scaling.scale_height(global_manager.get('text_box_height') // global_manager.get('font_size'), global_manager)) - 1
    font_name = global_manager.get('font_name')
    font_size = global_manager.get('font_size')
    for text_index in range(len(global_manager.get('text_list'))):
        if text_index < max_text_box_lines:
            if text_tools.message_width(global_manager.get('text_list')[-text_index - 1], font_size, font_name) > greatest_width:
                greatest_width = text_tools.message_width(global_manager.get('text_list')[-text_index - 1], font_size, font_name) #manages the width of already printed text lines
    if global_manager.get('input_manager').taking_input:
        if text_tools.message_width("Response: " + global_manager.get('message'), font_size, font_name) > greatest_width: #manages width of user input
            greatest_width = text_tools.message_width("Response: " + global_manager.get('message'), font_size, font_name)
    else:
        if text_tools.message_width(global_manager.get('message'), font_size, font_name) > greatest_width: #manages width of user input
            greatest_width = text_tools.message_width(global_manager.get('message'), font_size, font_name)
    text_box_width = greatest_width + scaling.scale_width(10, global_manager)
    x, y = scaling.scale_coordinates(0, global_manager.get('default_display_height') - global_manager.get('text_box_height'), global_manager)
    pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')['white'], (x, y, text_box_width, global_manager.get('text_box_height'))) #draws white rect to prevent overlapping
    if global_manager.get('typing'):
        color = 'red'
    else:
        color = 'black'
    x, y = scaling.scale_coordinates(0, global_manager.get('default_display_height') - global_manager.get('text_box_height'), global_manager)
    pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')[color], (x, y, text_box_width, global_manager.get('text_box_height')), scaling.scale_height(3, global_manager))
    pygame.draw.line(global_manager.get('game_display'), global_manager.get('color_dict')[color], (0, global_manager.get('display_height') - (font_size + scaling.scale_height(5, global_manager))),
        (text_box_width, global_manager.get('display_height') - (font_size + scaling.scale_height(5, global_manager))))

    global_manager.set('text_list', text_tools.manage_text_list(global_manager.get('text_list'), max_screen_lines)) #number of lines
    
    for text_index in range(len(global_manager.get('text_list'))):
        if text_index < max_text_box_lines:
            textsurface = global_manager.get('myfont').render(global_manager.get('text_list')[(-1 * text_index) - 1], False, (0, 0, 0))
            global_manager.get('game_display').blit(textsurface,(scaling.scale_width(10, global_manager), (-1 * font_size * text_index) + global_manager.get('display_height') - ((2 * font_size) + scaling.scale_height(5, global_manager))))
    if global_manager.get('input_manager').taking_input:
        textsurface = global_manager.get('myfont').render('Response: ' + global_manager.get('message'), False, (0, 0, 0))
    else:
        textsurface = global_manager.get('myfont').render(global_manager.get('message'), False, (0, 0, 0))
    global_manager.get('game_display').blit(textsurface,(scaling.scale_width(10, global_manager), global_manager.get('display_height') - (font_size + scaling.scale_height(5, global_manager))))

def manage_rmb_down(clicked_button, global_manager):
    '''
    Description:
        If the player is right clicking on a grid cell, cycles the order of the units in the cell. Otherwise, has same functionality as manage_lmb_down
    Input:
        boolean clicked_button: True if this click clicked a button, otherwise False
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    stopping = False
    if (not clicked_button) and action_possible(global_manager):
        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                for current_cell in current_grid.cell_list:
                    if current_cell.touching_mouse():
                        stopping = True #if doesn't reach this point, do same as lmb
                        if len(current_cell.contained_mobs) > 1:
                            moved_mob = current_cell.contained_mobs[1]
                            for current_image in moved_mob.images:
                                if not current_image.current_cell == 'none':
                                    while not moved_mob == current_image.current_cell.contained_mobs[0]:
                                        current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
                            global_manager.set('show_selection_outlines', True)
                            global_manager.set('last_selection_outline_switch', time.time())
                            if global_manager.get('minimap_grid') in moved_mob.grids:
                                global_manager.get('minimap_grid').calibrate(moved_mob.x, moved_mob.y)
                            moved_mob.select()
                            if moved_mob.is_pmob:
                                moved_mob.selection_sound()
                            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), moved_mob.images[0].current_cell.tile)
    elif global_manager.get('drawing_automatic_route'):
        stopping = True
        global_manager.set('drawing_automatic_route', False)
        if len(global_manager.get('displayed_mob').base_automatic_route) > 1:
            destination_coordinates = (global_manager.get('displayed_mob').base_automatic_route[-1][0], global_manager.get('displayed_mob').base_automatic_route[-1][1])
            if global_manager.get('displayed_mob').is_vehicle and global_manager.get('displayed_mob').vehicle_type == 'train' and not global_manager.get('strategic_map_grid').find_cell(destination_coordinates[0], destination_coordinates[1]).has_intact_building('train_station'):
                global_manager.get('displayed_mob').clear_automatic_route()
                text_tools.print_to_screen("A train's automatic route must start and end at a train station.", global_manager)
                text_tools.print_to_screen("The invalid route has been erased.", global_manager)
            else:
                text_tools.print_to_screen("Route saved", global_manager)
        else:
            global_manager.get('displayed_mob').clear_automatic_route()
            text_tools.print_to_screen("The created route must go between at least 2 tiles", global_manager)
        global_manager.get('minimap_grid').calibrate(global_manager.get('displayed_mob').x, global_manager.get('displayed_mob').y)
        actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), global_manager.get('displayed_mob').images[0].current_cell.tile)
    if not stopping:
        manage_lmb_down(clicked_button, global_manager)
    
def manage_lmb_down(clicked_button, global_manager):
    '''
    Description:
        If the player is choosing a movement destination and the player clicks on a cell, chooses that cell as the movement destination. If the player is choosing a movement destination but did not click a cell, cancels the movement
            destination selection process. Otherwise, if the player clicks on a cell, selects the top mob in that cell if any are present and moves the minimap to that cell. If the player clicks on a button, calls the on_click function
            of that button. If nothing was clicked, deselects the selected mob if any is selected
    Input:
        boolean clicked_button: True if this click clicked a button, otherwise False
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if action_possible(global_manager) or global_manager.get('choosing_destination') or global_manager.get('choosing_advertised_commodity') or global_manager.get('drawing_automatic_route'):
        if (not clicked_button and (not (global_manager.get('choosing_destination') or global_manager.get('choosing_advertised_commodity') or global_manager.get('drawing_automatic_route')))):#do not do selecting operations if user was trying to click a button #and action_possible(global_manager)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            selected_new_mob = False
            if (not global_manager.get('capital')):
                actor_utility.deselect_all(global_manager)
            if global_manager.get('current_game_mode') == 'ministers':
                minister_utility.calibrate_minister_info_display(global_manager, 'none')
            else:
                actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), 'none')
            for current_grid in global_manager.get('grid_list'):
                if global_manager.get('current_game_mode') in current_grid.modes:
                    for current_cell in current_grid.cell_list:
                        if current_cell.touching_mouse():
                            if current_cell.visible:
                                my_cell = current_cell
                                if len(current_cell.contained_mobs) > 0:
                                    selected_new_mob = True
                                    current_cell.contained_mobs[0].select()
                                    if current_cell.contained_mobs[0].is_pmob:
                                        current_cell.contained_mobs[0].selection_sound()
                                    if current_grid == global_manager.get('minimap_grid'):
                                        main_x, main_y = global_manager.get('minimap_grid').get_main_grid_coordinates(current_cell.x, current_cell.y) #main_x, main_y = global_manager.get('strategic_map_grid').get_main_grid_coordinates(current_cell.x, current_cell.y)
                                        main_cell = global_manager.get('strategic_map_grid').find_cell(main_x, main_y)
                                        if not main_cell == 'none':
                                            main_tile = main_cell.tile
                                            if not main_tile == 'none':
                                                actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), main_tile)
                                    else: #elif current_grid == global_manager.get('strategic_map_grid'):
                                        actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), current_cell.tile)
            if selected_new_mob:
                selected_list = actor_utility.get_selected_list(global_manager)
                if len(selected_list) == 1 and selected_list[0].grids[0] == global_manager.get('minimap_grid').attached_grid: #do not calibrate minimap if selecting someone outside of attached grid
                    global_manager.get('minimap_grid').calibrate(selected_list[0].x, selected_list[0].y)
                    
            else:
                click_move_minimap(global_manager)
                
        elif (not clicked_button) and global_manager.get('choosing_destination'): #if clicking to move somewhere
            chooser = global_manager.get('choosing_destination_info_dict')['chooser']
            chose_destination = False
            for current_grid in global_manager.get('grid_list'): #destination_grids:
                for current_cell in current_grid.cell_list:
                    if current_cell.touching_mouse():
                        click_move_minimap(global_manager)
                        target_cell = 'none'
                        if current_cell.grid.is_abstract_grid:
                            target_cell = current_cell
                        else:
                            target_cell = global_manager.get('strategic_map_grid').find_cell(global_manager.get('minimap_grid').center_x, global_manager.get('minimap_grid').center_y) #center
                        if not current_grid in chooser.grids:
                            stopping = False
                            if not current_grid.is_abstract_grid: #if grid has more than 1 cell, check if correct part of grid
                                destination_x, destination_y = target_cell.tile.get_main_grid_coordinates()
                                if (not (destination_y == 0 or (destination_y == 1 and target_cell.has_intact_building('port')))) and destination_x >= 0 and destination_x < global_manager.get('strategic_map_grid').coordinate_width: #or is harbor
                                    text_tools.print_to_screen("You can only send ships to coastal waters and coastal ports.", global_manager)
                                    stopping = True
                            chose_destination = True
                            if not stopping:
                                chooser.end_turn_destination = target_cell.tile
                                global_manager.set('show_selection_outlines', True)
                                global_manager.set('last_selection_outline_switch', time.time())#outlines should be shown immediately when destination chosen
                                chooser.remove_from_turn_queue()
                                actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), chooser)
                                actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), chooser.images[0].current_cell.tile)
                        else: #can not move to same continent
                            text_tools.print_to_screen("You can only send ships to other theatres.", global_manager)
            global_manager.set('choosing_destination', False)
            global_manager.set('choosing_destination_info_dict', {})
            
        elif (not clicked_button) and global_manager.get('choosing_advertised_commodity'):
            global_manager.set('choosing_advertised_commodity', False)
            global_manager.set('choosing_advertised_commodity_info_dict', {})
            
        elif (not clicked_button) and global_manager.get('drawing_automatic_route'):
            #chooser = global_manager.get('choosing_destination_info_dict')['chooser']
            #chose_destination = False
            for current_grid in global_manager.get('grid_list'): #destination_grids:
                for current_cell in current_grid.cell_list:
                    if current_cell.touching_mouse():
                        #target_cell = 'none'
                        if current_cell.grid.is_abstract_grid:
                            text_tools.print_to_screen("Only tiles adjacent to the most recently chosen destination can be added to the movement route.", global_manager)
                        else:
                            displayed_mob = global_manager.get('displayed_mob')
                            if current_cell.grid.is_mini_grid:
                                target_tile = current_cell.tile.get_equivalent_tile()
                                if target_tile == 'none':
                                    return()
                                target_cell = target_tile.cell
                            else:
                                target_cell = current_cell
                            #target_cell = global_manager.get('strategic_map_grid').find_cell(global_manager.get('minimap_grid').center_x, global_manager.get('minimap_grid').center_y)
                            destination_x, destination_y = (target_cell.x, target_cell.y)#target_cell.tile.get_main_grid_coordinates()
                            previous_destination_x, previous_destination_y = displayed_mob.base_automatic_route[-1]
                            if utility.find_coordinate_distance((destination_x, destination_y), (previous_destination_x, previous_destination_y)) == 1:
                                destination_infrastructure = target_cell.get_building('infrastructure')
                                if not target_cell.visible:
                                    text_tools.print_to_screen("Movement routes can not be created through unexplored tiles.", global_manager)
                                    return()
                                elif displayed_mob.is_vehicle and displayed_mob.vehicle_type == 'train' and not target_cell.has_building('railroad'):
                                    text_tools.print_to_screen("Trains can only create movement routes along railroads.", global_manager)
                                    return()
                                elif target_cell.terrain == 'water' and not displayed_mob.can_swim:
                                    text_tools.print_to_screen("This unit can not create movement routes through water.", global_manager)
                                    return()
                                elif target_cell.terrain == 'water' and displayed_mob.can_swim and (not displayed_mob.can_swim_ocean) and destination_y == 0:
                                    text_tools.print_to_screen("This unit can not create movement routes through ocean water.", global_manager)
                                    return()
                                elif target_cell.terrain == 'water' and displayed_mob.can_swim and (not displayed_mob.can_swim_river) and destination_y > 0:
                                    text_tools.print_to_screen("This unit can not create movement routes through river water.", global_manager)
                                    return()
                                elif (not target_cell.terrain == 'water') and (not displayed_mob.can_walk) and not target_cell.has_intact_building('port'):
                                    text_tools.print_to_screen("This unit can not create movement routes on land, except through ports.", global_manager)
                                    return()
                                                                     
                                displayed_mob.add_to_automatic_route((destination_x, destination_y))
                                click_move_minimap(global_manager)
                                global_manager.set('show_selection_outlines', True)
                                global_manager.set('last_selection_outline_switch', time.time())
                            else:
                                text_tools.print_to_screen("Only tiles adjacent to the most recently chosen destination can be added to the movement route.", global_manager)
                                
        elif not clicked_button:
            click_move_minimap(global_manager)

def click_move_minimap(global_manager): 
    '''
    Description:
        When a cell on the strategic map grid is clicked, centers the minimap on that cell
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    mouse_x, mouse_y = pygame.mouse.get_pos()
    breaking = False
    for current_grid in global_manager.get('grid_list'): #if grid clicked, move minimap to location clicked
        if current_grid.can_show():
            for current_cell in current_grid.cell_list:
                if current_cell.touching_mouse():
                    if current_grid == global_manager.get('minimap_grid'): #if minimap clicked, calibrate to corresponding place on main map
                        if not current_cell.terrain == 'none': #if off map, do not move minimap there
                            main_x, main_y = current_grid.get_main_grid_coordinates(current_cell.x, current_cell.y)
                            global_manager.get('minimap_grid').calibrate(main_x, main_y)
                    elif current_grid == global_manager.get('strategic_map_grid'):
                        global_manager.get('minimap_grid').calibrate(current_cell.x, current_cell.y)
                    else: #if abstract grid, show the inventory of the tile clicked without calibrating minimap
                        actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), current_grid.cell_list[0].tile)
                    breaking = True
                    break
                if breaking:
                    break
            if breaking:
                 break
