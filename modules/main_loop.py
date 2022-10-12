#Contains game's main loop

import time
import pygame
from . import main_loop_tools
from . import utility
from . import text_tools
from . import turn_management_tools
from . import actor_utility

def main_loop(global_manager):
    '''
    Description:
        Controls the main loop of the program, handling events such as mouse clicks and button presses, controlling timers, and drawing shapes and images. The program will end once this function stops
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    while not global_manager.get('crashed'):
        if len(global_manager.get('notification_list')) == 0:
            stopping = False
        global_manager.get('input_manager').update_input()
        if global_manager.get('input_manager').taking_input:
            typing = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global_manager.set('crashed', True)
            if global_manager.get('r_shift') == 'down' or global_manager.get('l_shift') == 'down':
                global_manager.set('capital', True)
            else:
                global_manager.set('capital', False)
            if global_manager.get('r_ctrl') == 'down' or global_manager.get('l_ctrl') == 'down':
                global_manager.set('ctrl', True)
            else:
                global_manager.set('ctrl', False)
            if event.type == pygame.KEYDOWN:
                for current_button in global_manager.get('button_list'):
                    if current_button.can_show() and not global_manager.get('typing'):
                        if current_button.has_keybind:
                            if event.key == current_button.keybind_id:
                                if current_button.has_released:
                                    current_button.on_click()
                                    current_button.has_released = False
                                    current_button.being_pressed = True
                                    break
                            else:#stop confirming an important button press if user starts doing something else
                                current_button.confirming = False
                                current_button.being_pressed = False
                        else:
                            current_button.confirming = False
                            current_button.being_pressed = False
                    else:
                        current_button.confirming = False
                        current_button.being_pressed = False
                if event.key == pygame.K_RSHIFT:
                    global_manager.set('r_shift', 'down')
                if event.key == pygame.K_LSHIFT:
                    global_manager.set('l_shift', 'down')
                if event.key == pygame.K_RCTRL:
                    global_manager.set('r_ctrl', 'down')
                if event.key == pygame.K_LCTRL:
                    global_manager.set('l_ctrl', 'down')
                if event.key == pygame.K_ESCAPE:
                    global_manager.set('typing', False)
                    global_manager.set('message', '')
                if event.key == pygame.K_SPACE:
                    if global_manager.get('typing'):
                        global_manager.set('message', utility.add_to_message(global_manager.get('message'), ' ')) #add space to message and set message to it
                if event.key == pygame.K_BACKSPACE:
                    if global_manager.get('typing'):
                        global_manager.set('message', global_manager.get('message')[:-1]) #remove last character from message and set message to it

                key_codes = [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p]
                key_codes += [pygame.K_q, pygame.K_r, pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z]
                key_codes += [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]
                lowercase_key_values = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
                uppercase_key_values = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')']

                for key_index in range(len(key_codes)):
                    correct_key = False
                    if event.key == key_codes[key_index]:
                        correct_key = True
                        if global_manager.get('typing') and not global_manager.get('capital'):
                            global_manager.set('message', utility.add_to_message(global_manager.get('message'), lowercase_key_values[key_index]))
                        elif global_manager.get('typing') and global_manager.get('capital'):
                            global_manager.set('message', utility.add_to_message(global_manager.get('message'), uppercase_key_values[key_index]))
                    if correct_key:
                        break
                        
            if event.type == pygame.KEYUP:
                for current_button in global_manager.get('button_list'):
                    if not global_manager.get('typing') or current_button.keybind_id == pygame.K_TAB or current_button.keybind_id == pygame.K_e:
                        if current_button.has_keybind:
                            if event.key == current_button.keybind_id:
                                current_button.on_release()
                                current_button.has_released = True
                if event.key == pygame.K_RSHIFT:
                    global_manager.set('r_shift', 'up')
                if event.key == pygame.K_LSHIFT:
                    global_manager.set('l_shift', 'up')
                if event.key == pygame.K_LCTRL:
                    global_manager.set('l_ctrl', 'up')
                if event.key == pygame.K_RCTRL:
                    global_manager.set('r_ctrl', 'up')
                if event.key == pygame.K_RETURN:
                    if global_manager.get('typing'):
                        if global_manager.get('input_manager').taking_input:
                            #input_response = message
                            global_manager.get('input_manager').taking_input = False
                            text_tools.print_to_screen('Response: ' + global_manager.get('message'), global_manager)
                            input_manager.receive_input(global_manager.get('message'))
                            check_pointer_removal('not typing')
                        else:
                            text_tools.print_to_screen(global_manager.get('message'), global_manager)
                        global_manager.set('typing', False)
                        global_manager.set('message', '')
                    else:
                        global_manager.set('typing', True)
        global_manager.set('old_lmb_down', global_manager.get('lmb_down'))
        global_manager.set('old_rmb_down', global_manager.get('rmb_down'))
        global_manager.set('old_mmb_down', global_manager.get('mmb_down'))
        lmb_down, mmb_down, rmb_down = pygame.mouse.get_pressed()
        global_manager.set('lmb_down', lmb_down)
        global_manager.set('mmb_down', mmb_down)
        global_manager.set('rmb_down', rmb_down)

        if not global_manager.get('old_rmb_down') == global_manager.get('rmb_down'): #if rmb changes
            if not global_manager.get('rmb_down'): #if user just released rmb
                clicked_button = False
                stopping = False
                if global_manager.get('current_instructions_page') == 'none':
                    for current_button in global_manager.get('button_list'):
                        if current_button.touching_mouse() and current_button.can_show() and current_button in global_manager.get('notification_list') and not stopping:
                            current_button.on_rmb_click()#prioritize clicking buttons that appear above other buttons and don't press the ones 
                            current_button.on_rmb_release()
                            clicked_button = True
                            stopping = True
                else:
                    if global_manager.get('current_instructions_page').touching_mouse() and global_manager.get('current_instructions_page').can_show():
                        global_manager.get('current_instructions_page').on_rmb_click()
                        clicked_button = True
                        stopping = True
                if not stopping:
                    for current_button in global_manager.get('button_list'):
                        if current_button.touching_mouse() and current_button.can_show():
                            current_button.on_rmb_click()
                            current_button.on_rmb_release()
                            clicked_button = True
                main_loop_tools.manage_rmb_down(clicked_button, global_manager)

        if not global_manager.get('old_lmb_down') == global_manager.get('lmb_down'):#if lmb changes
            if not global_manager.get('lmb_down'):#if user just released lmb
                clicked_button = False
                stopping = False
                if global_manager.get('current_instructions_page') == 'none':
                    for current_button in global_manager.get('button_list'):#here
                        if current_button.touching_mouse() and current_button.can_show() and (current_button.in_notification) and not stopping: #if notification, click before other buttons
                            current_button.on_click()#prioritize clicking buttons that appear above other buttons and don't press the ones 
                            current_button.on_release()
                            clicked_button = True
                            stopping = True
                            break
                else:
                    if global_manager.get('current_instructions_page').touching_mouse() and global_manager.get('current_instructions_page').can_show(): #if instructions, click before other buttons
                        global_manager.get('current_instructions_page').on_click()
                        clicked_button = True
                        stopping = True
                        break
                if not stopping:
                    for current_button in global_manager.get('button_list'):
                        if current_button.touching_mouse() and current_button.can_show() and not clicked_button: #only click 1 button at a time
                            current_button.on_click()
                            current_button.on_release()
                            clicked_button = True
                            break
                main_loop_tools.manage_lmb_down(clicked_button, global_manager)#whether button was clicked or not determines whether characters are deselected

        if (global_manager.get('lmb_down') or global_manager.get('rmb_down')):
            for current_button in global_manager.get('button_list'):
                if current_button.touching_mouse() and current_button.can_show():
                    current_button.showing_outline = True
                elif not current_button.being_pressed:
                    current_button.showing_outline = False
        else:
            for current_button in global_manager.get('button_list'):
                if not current_button.being_pressed:
                    current_button.showing_outline = False

        if not global_manager.get('loading'):
            main_loop_tools.update_display(global_manager)
        else:
            main_loop_tools.draw_loading_screen(global_manager)
        current_time = time.time()
        global_manager.set('current_time', current_time)
        if global_manager.get('current_time') - global_manager.get('last_selection_outline_switch') > 1:
            global_manager.set('show_selection_outlines', utility.toggle(global_manager.get('show_selection_outlines')))
            global_manager.set('last_selection_outline_switch', time.time())

        if not global_manager.get('player_turn') and global_manager.get('previous_turn_time') + global_manager.get('end_turn_wait_time') <= time.time(): #if enough time has passed based on delay from previous movement
            enemy_turn_done = True
            for enemy in global_manager.get('npmob_list'):
                if not enemy.turn_done:
                    enemy_turn_done = False
                    break
            if enemy_turn_done:
                global_manager.set('player_turn', True)
                global_manager.set('enemy_combat_phase', True)
                turn_management_tools.manage_combat(global_manager)
            else:
                current_enemy = global_manager.get('enemy_turn_queue')[0]

                enemy_coordinates = (current_enemy.x, current_enemy.y)
                removed = False
                spawning = False
                did_nothing = False
                moving = False
                if current_enemy.npmob_type == 'native_warriors' and current_enemy.despawning:
                    if current_enemy.selected or not current_enemy.visible():
                        current_enemy.remove()
                        removed = True
                        
                elif current_enemy.npmob_type == 'native_warriors' and current_enemy.creation_turn == global_manager.get('turn'): #if unit just created
                    spawn_cell = current_enemy.grids[0].find_cell(current_enemy.x, current_enemy.y)
                    if (global_manager.get('minimap_grid').center_x, global_manager.get('minimap_grid').center_y) == (current_enemy.x, current_enemy.y) and spawn_cell.visible: #if camera just moved to spawn location to show spawning
                        spawning = True
                        current_enemy.show_images()
                        current_enemy.select()
                        current_enemy.attack_on_spawn()
                        current_enemy.turn_done = True
                    else: #if camera did not move to spawn location
                        spawning = True
                        if spawn_cell.visible: #if spawn location visible but camera hasn't moved there yet, move camera there
                            global_manager.get('minimap_grid').calibrate(current_enemy.x, current_enemy.y)
                        else: #if spawn location not visible, end turn
                            current_enemy.show_images()
                            current_enemy.turn_done = True 
            
                elif not current_enemy.visible(): #if not just spawned and hidden, do action without displaying
                    if current_enemy.selected:
                        actor_utility.deselect_all(global_manager)
                    current_enemy.end_turn_move()
                    moving = True
                    
                elif current_enemy.selected: #if enemy is selected and did not just spawn, move it while minimap follows
                    if not current_enemy.creation_turn == global_manager.get('turn'): #don't do anything on first turn, but still move camera to spawn location if visible
                        current_enemy.end_turn_move() #do_turn()
                        moving = True
                        if current_enemy.visible():
                            if not current_enemy.selected:
                                current_enemy.select()
                                global_manager.get('minimap_grid').calibrate(current_enemy.x, current_enemy.y)
                            else:
                                global_manager.get('minimap_grid').calibrate(current_enemy.x, current_enemy.y)
                        else:
                            actor_utility.deselect_all(global_manager)
                    else:
                        current_enemy.turn_done = True
                    
                if (not (removed or spawning)) and (not current_enemy.creation_turn == global_manager.get('turn')) and current_enemy.visible(): #if unit visible and not selected, start its turn
                    if current_enemy.npmob_type == 'native_warriors' and current_enemy.find_closest_target() == 'none' and not current_enemy.despawning: #if native warriors have no target, they stand still and no movement is shown
                        did_nothing = True
                        current_enemy.turn_done = True
                    
                    elif current_enemy.npmob_type == 'beast' and current_enemy.find_closest_target == current_enemy.images[0].current_cell and not current_enemy.images[0].current_cell.has_pmob():
                        #if beasts stand still and don't attack anything, no movement is shown
                        did_nothing = True
                        current_enemy.turn_done = True
                    elif current_enemy.visible(): #if unit will do an action, move the camera to it and select it
                        current_enemy.select()
                        global_manager.get('minimap_grid').calibrate(current_enemy.x, current_enemy.y)
                                                                     
                elif current_enemy.creation_turn == global_manager.get('turn') and not spawning: #if enemy visible but just spawned, end turn
                    did_nothing = True
                    current_enemy.turn_done = True

                if removed: #show unit despawning if visible
                    current_enemy.turn_done = True
                    if not current_enemy.visible():
                        global_manager.set('end_turn_wait_time', 0)
                    else:
                        global_manager.set('end_turn_wait_time', 1)
                    global_manager.get('enemy_turn_queue').pop(0)
                    
                else: #If unit visible, have short delay depending on action taken to let user see it
                    new_enemy_coordinates = (current_enemy.x, current_enemy.y)
                    if (not spawning) and (did_nothing or not current_enemy.visible()): #do not wait if not visible or nothing to show, exception for spawning units, which may not be visible as user watches them spawn
                        global_manager.set('end_turn_wait_time', 0)
                    elif spawning and not current_enemy.grids[0].find_cell(current_enemy.x, current_enemy.y).visible: #do not wait if spawning unit won't be visible even after it spawns
                        global_manager.set('end_turn_wait_time', 0)
                    elif moving and not enemy.turn_done:#if will move again after this
                        global_manager.set('end_turn_wait_time', 0.25)
                    else: #if done with turn
                        global_manager.set('end_turn_wait_time', 0.5)

                    if current_enemy.turn_done:
                        global_manager.get('enemy_turn_queue').pop(0)
            if global_manager.get('DEBUG_fast_turn'):
                global_manager.set('end_turn_wait_time', 0)
            global_manager.set('previous_turn_time', time.time())
    
            
        for actor in global_manager.get('actor_list'):
            for current_image in actor.images:
                if not current_image.image_description == current_image.previous_idle_image and time.time() >= current_image.last_image_switch + 0.6:
                    current_image.set_image(current_image.previous_idle_image)
        start_time = time.time()
        global_manager.set('start_time', start_time)
        global_manager.set('current_time', time.time())
