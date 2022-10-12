#Contains functionality for actor display buttons

from ..buttons import button
from .. import main_loop_tools
from .. import utility
from .. import actor_utility
from .. import minister_utility
from .. import trial_utility
from .. import text_tools
from .. import game_transitions
from .. import notification_tools

class label_button(button):
    '''
    Button that is attached to a label, has have behavior related to the label, will only show when the label is showing
    '''
    def __init__(self, coordinates, width, height, button_type, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string button_type: Determines the function of this button, like 'end turn'
            pygame key object keybind_id: Determines the keybind id that activates this button, like pygame.K_n
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.attached_label = attached_label
        super().__init__(coordinates, width, height, 'blue', button_type, keybind_id, modes, image_id, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass if this button's label is showing, otherwise returns False. Exception for sell commodity buttons, which will not be not be able to sell consumer goods and will be hidden when
                attached to an inventory label showing consumer goods
        '''
        if self.attached_label.can_show():
            if not ((self.button_type == 'sell commodity' or self.button_type == 'sell all commodity') and self.attached_label.current_commodity == 'consumer goods'):
                return(super().can_show())
        return(False)

    def set_y(self, attached_label): 
        ''' 
        Description:
            Sets this button's y position to line up the center of this button and its label
        Input:
            actor_display_label attached_label: Label to match this button's y position with
        Output:
            None
        '''
        height_difference = self.height - attached_label.height
        y_displacement = height_difference / 2
        self.y = attached_label.y - y_displacement
        self.Rect.y = self.global_manager.get('display_height') - (attached_label.y + self.height - y_displacement)
        self.outline.y = self.Rect.y - self.outline_width# - y_displacement

class worker_crew_vehicle_button(label_button):
    '''
    Button that commands a worker to crew a vehicle in its tile
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, vehicle_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle this button crews
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = vehicle_type
        self.was_showing = False
        super().__init__(coordinates, width, height, 'worker to crew', keybind_id, modes, image_id, attached_label, global_manager)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a worker to crew a vehicle in its tile
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):    
                selected_list = actor_utility.get_selected_list(self.global_manager)
                crew = self.attached_label.actor
                vehicle = self.attached_label.actor.images[0].current_cell.get_uncrewed_vehicle(self.vehicle_type, crew.worker_type)
                if (not (vehicle == 'none' or crew == 'none')) and (not vehicle.has_crew): #if vehicle and rider selected
                    if vehicle.x == crew.x and vehicle.y == crew.y: #ensure that this doesn't work across grids
                            
                        if crew.sentry_mode:
                            crew.set_sentry_mode(False)
                        if vehicle.sentry_mode:
                            vehicle.set_sentry_mode(False)
                        crew.crew_vehicle(vehicle)
                    else:
                        text_tools.print_to_screen("You must select a worker in the same tile as an uncrewed " + self.vehicle_type + " to crew the " + self.vehicle_type + ".", self.global_manager)
                else:
                    if crew.worker_type == 'slave':
                        text_tools.print_to_screen("Slave workers can not crew vehicles.", self.global_manager)
                    elif crew.worker_type == 'African' and not self.attached_label.actor.images[0].current_cell.get_uncrewed_vehicle(self.vehicle_type, 'European') == 'none':
                        text_tools.print_to_screen("Only European workers can crew steamships.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You must select a worker in the same tile as an uncrewed " + self.vehicle_type + " to crew the " + self.vehicle_type + ".", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not crew a " + self.vehicle_type + ".", self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if a worker is not selected or if its tile does not have an uncrewed vehicle of the correct type, otherwise returns False
        '''
        result = super().can_show()
        if result:
            if (not (self.attached_label.actor.is_worker and not self.attached_label.actor.worker_type == 'religious')) or (not self.attached_label.actor.images[0].current_cell.has_uncrewed_vehicle(self.vehicle_type)):
                result = False
        if not result == self.was_showing: #if visibility changes, update actor info display
            self.was_showing = result
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self.attached_label.actor)
        self.was_showing = result
        return(result)

class embark_all_passengers_button(label_button):
    '''
    Button that commands a vehicle to take all other mobs in its tile as passengers
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        super().__init__(coordinates, width, height, 'embark all', keybind_id, modes, image_id, attached_label, global_manager)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to take all other mobs in its tile as passengers
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                vehicle = self.attached_label.actor
                can_embark = True
                if self.vehicle_type == 'train':
                    if vehicle.images[0].current_cell.contained_buildings['train_station'] == 'none':
                        text_tools.print_to_screen("A train can only pick up passengers at a train station.", self.global_manager)
                        can_embark = False
                if can_embark:
                    if vehicle.sentry_mode:
                        vehicle.set_sentry_mode(False)
                    for contained_mob in vehicle.images[0].current_cell.contained_mobs:
                        passenger = contained_mob
                        if passenger.controllable and not passenger.is_vehicle: #vehicles and enemies won't be picked up as passengers
                            passenger.embark_vehicle(vehicle)
                    self.global_manager.get('sound_manager').play_sound('voices/ship 1')
            else:
                text_tools.print_to_screen("You are busy and can not embark all passengers.", self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.has_crew: #do not show if ship does not have crew
                return(False)
            if (not self.vehicle_type == self.attached_label.actor.vehicle_type) and (not self.attached_label.actor.vehicle_type == 'vehicle'): #update vehicle type and image when shown if type has changed, like train to ship
                self.vehicle_type = self.attached_label.actor.vehicle_type
                self.image.set_image('buttons/embark_' + self.vehicle_type + '_button.png')
        return(result)

class disembark_all_passengers_button(label_button):
    '''
    Button that commands a vehicle to eject all of its passengers
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        super().__init__(coordinates, width, height, 'disembark all', keybind_id, modes, image_id, attached_label, global_manager)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to eject all of its passengers
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                vehicle = self.attached_label.actor
                can_disembark = True
                if self.vehicle_type == 'train':
                    if vehicle.images[0].current_cell.contained_buildings['train_station'] == 'none':
                        text_tools.print_to_screen("A train can only drop off passengers at a train station.", self.global_manager)
                        can_disembark = False
                if can_disembark:
                    if vehicle.sentry_mode:
                        vehicle.set_sentry_mode(False)
                    if len(vehicle.contained_mobs) > 0:
                        vehicle.contained_mobs[-1].selection_sound()
                    vehicle.eject_passengers()
            else:
                text_tools.print_to_screen("You are busy and can not disembark all passengers.", self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.has_crew: #do not show if ship does not have crew
                return(False)
            if (not self.vehicle_type == self.attached_label.actor.vehicle_type) and (not self.attached_label.actor.vehicle_type == 'vehicle'): #update vehicle type and image when shown if type has changed, like train to ship
                self.vehicle_type = self.attached_label.actor.vehicle_type
                self.image.set_image('buttons/disembark_' + self.vehicle_type + '_button.png')
        return(result)

class crew_vehicle_button(label_button):
    '''
    Button that commands a vehicle to take a worker in its tile as crew. Also updates this button to reflect a train or ship depending on the selected vehicle
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        super().__init__(coordinates, width, height, 'crew', keybind_id, modes, image_id, attached_label, global_manager)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to take a worker in its tile as crew
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):    
                vehicle = self.attached_label.actor
                is_steamship = False
                if vehicle.can_swim and vehicle.can_swim_ocean: #if steamship
                    is_steamship = True
                    crew = vehicle.images[0].current_cell.get_worker(['European'])
                else: 
                    crew = vehicle.images[0].current_cell.get_worker(['African', 'European']) #'none'
                
                if (not (vehicle == 'none' or crew == 'none')) and (not vehicle.has_crew): #if vehicle and rider selected
                    if vehicle.x == crew.x and vehicle.y == crew.y: #ensure that this doesn't work across grids
                        if crew.sentry_mode:
                            crew.set_sentry_mode(False)
                        if vehicle.sentry_mode:
                            vehicle.set_sentry_mode(False)
                        crew.crew_vehicle(vehicle)
                    else:
                        if is_steamship:
                            text_tools.print_to_screen("You must select an uncrewed " + self.vehicle_type + " in the same tile as a European worker to crew the " + self.vehicle_type + ".", self.global_manager)
                        else:
                            text_tools.print_to_screen("You must select an uncrewed " + self.vehicle_type + " in the same tile as a non-slave worker to crew the " + self.vehicle_type + ".", self.global_manager)
                else:
                    if is_steamship:
                        text_tools.print_to_screen("You must select an uncrewed " + self.vehicle_type + " in the same tile as a European worker to crew the " + self.vehicle_type + ".", self.global_manager)
                    else:
                        text_tools.print_to_screen("You must select an uncrewed " + self.vehicle_type + " in the same tile as a non-slave worker to crew the " + self.vehicle_type + ".", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not crew a " + self.vehicle_type + ".", self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has crew, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if self.attached_label.actor.has_crew:
                return(False)
            if (not self.vehicle_type == self.attached_label.actor.vehicle_type) and (not self.attached_label.actor.vehicle_type == 'vehicle'): #update vehicle type and image when shown if type has changed, like train to ship
                self.vehicle_type = self.attached_label.actor.vehicle_type
                self.image.set_image('buttons/crew_' + self.vehicle_type + '_button.png')
        return(result)

class uncrew_vehicle_button(label_button):
    '''
    Button that commands a vehicle's crew to leave the vehicle
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        super().__init__(coordinates, width, height, 'uncrew', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.has_crew:
                return(False)
            if (not self.vehicle_type == self.attached_label.actor.vehicle_type) and (not self.attached_label.actor.vehicle_type == 'vehicle'):
                self.vehicle_type = self.attached_label.actor.vehicle_type
                self.image.set_image('buttons/uncrew_' + self.vehicle_type + '_button.png')
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle's crew to leave the vehicle
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                vehicle = self.attached_label.actor
                crew = vehicle.crew
                if len(vehicle.contained_mobs) == 0 and len(vehicle.get_held_commodities()) == 0:
                    crew.uncrew_vehicle(vehicle)
                    actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), vehicle)
                else:
                    text_tools.print_to_screen("You can not remove the crew from a " + self.vehicle_type + " with passengers or cargo.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not remove a " + self.vehicle_type + "'s crew.", self.global_manager)

class merge_button(label_button):
    '''
    Button that merges a selected officer with a worker in the same tile to form a group
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'merge', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not an officer, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.is_officer:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button merges a selected officer with a worker in the same tile to form a group
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):    
                selected_list = actor_utility.get_selected_list(self.global_manager)
                if len(selected_list) == 1:
                    officer = 'none'
                    worker = 'none'
                    for current_selected in selected_list:
                        if current_selected in self.global_manager.get('officer_list'):
                            officer = current_selected
                            if officer.officer_type == 'evangelist': #if evangelist, look for church volunteers
                                worker = officer.images[0].current_cell.get_worker(['religious'])
                            else:
                                worker = officer.images[0].current_cell.get_worker(['African', 'European', 'slave'])
                    if not (officer == 'none' or worker == 'none'): #if worker and officer selected
                        if officer.x == worker.x and officer.y == worker.y:
                            if worker.sentry_mode:
                                worker.set_sentry_mode(False)
                            if officer.sentry_mode:
                                officer.set_sentry_mode(False)
                            self.global_manager.get('actor_creation_manager').create_group(worker, officer, self.global_manager)
                        else:
                            if (not officer == 'none') and officer.officer_type == 'evangelist':
                                text_tools.print_to_screen("You must select an evangelist in the same tile as church volunteers to create missionaries.", self.global_manager)
                            else:  
                                text_tools.print_to_screen("You must select an officer in the same tile as a worker to create a group.", self.global_manager)
                    else:
                        if (not officer == 'none') and officer.officer_type == 'evangelist':
                            text_tools.print_to_screen("You must select an evangelist in the same tile as church volunteers to create missionaries.", self.global_manager)
                        else:  
                            text_tools.print_to_screen("You must select an officer in the same tile as a worker to create a group.", self.global_manager)
                else:
                    text_tools.print_to_screen("You must select an officer in the same tile as a worker to create a group.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not form a group.", self.global_manager)


class split_button(label_button):
    '''
    Button that splits a selected group into its component officer and worker
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'split', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a group, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.is_group:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button splits a selected group into its component officer and worker
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                displayed_mob = self.global_manager.get('displayed_mob')#selected_list = actor_utility.get_selected_list(self.global_manager)
                if (not displayed_mob == 'none') and displayed_mob.is_group:
                    if not (displayed_mob.can_hold_commodities and len(displayed_mob.get_held_commodities()) > 0): #do not disband if trying to disband a porter who is carrying commodities
                        displayed_mob.disband()
                    else:
                        text_tools.print_to_screen("You can not split a unit that is carrying commodities.", self.global_manager)
                else:
                    text_tools.print_to_screen("Only a group can be split it into a worker and an officer.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not split a group.", self.global_manager)

class enable_sentry_mode_button(label_button):
    '''
    Button that enables sentry mode for a unit, causing it to not be added to the turn cycle queue
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'enable sentry mode', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob and is not already in sentry mode, otherwise returns False
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.is_pmob:
                return(False)
            elif self.attached_label.actor.sentry_mode:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button activates sentry mode for the selected unit
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                self.attached_label.actor.set_sentry_mode(True)
            else:
                text_tools.print_to_screen("You are busy and can not enable sentry mode.", self.global_manager)

class disable_sentry_mode_button(label_button):
    '''
    Button that disables sentry mode for a unit, causing it to not be added to the turn cycle queue
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'disable sentry mode', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob and is in sentry mode, otherwise returns False
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.is_pmob:
                return(False)
            elif not self.attached_label.actor.sentry_mode:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button deactivates sentry mode for the selected unit
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                self.attached_label.actor.set_sentry_mode(False)
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self.attached_label.actor)
            else:
                text_tools.print_to_screen("You are busy and can not disable sentry mode.", self.global_manager)

class end_unit_turn_button(label_button):
    '''
    Button that ends a unit's turn, removing it from the current turn's turn cycle queue
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'end unit turn', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob in the turn queue, otherwise returns False
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.is_pmob:
                return(False)
            elif not self.attached_label.actor in self.global_manager.get('player_turn_queue'):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected unit from the current turn's turn cycle queue
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                self.attached_label.actor.remove_from_turn_queue()
                game_transitions.cycle_player_turn(self.global_manager)
                #actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self.attached_label.actor)
            else:
                text_tools.print_to_screen("You are busy and can not end this unit's turn.", self.global_manager)

class remove_work_crew_button(label_button):
    '''
    Button that removes a work crew from a building
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, building_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            string building_type: Determines type of building this button removes workers from, like 'resource building'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'remove worker', keybind_id, modes, image_id, attached_label, global_manager)
        self.building_type = building_type
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if there is not a corresponding work crew to remove, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.attached_list[self.attached_label.list_index].in_building:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes a work crew from a building
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                self.attached_label.attached_list[self.attached_label.list_index].leave_building(self.attached_label.actor.cell.contained_buildings[self.building_type])
            else:
                text_tools.print_to_screen("You are busy and can not remove a work crew from a building.", self.global_manager)

class disembark_vehicle_button(label_button):
    '''
    Button that disembarks a passenger from a vehicle
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        super().__init__(coordinates, width, height, 'disembark', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if there is not a corresponding passenger to disembark, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.attached_list[self.attached_label.list_index].in_vehicle:
                return(False)
            old_vehicle_type = self.vehicle_type
            self.vehicle_type = self.attached_label.actor.vehicle_type
            if not self.vehicle_type == old_vehicle_type and not self.vehicle_type == 'none': #if changed
                self.image.set_image('buttons/disembark_' + self.vehicle_type + '_button.png')
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button disembarks a passenger from a vehicle
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                if len(self.attached_label.actor.contained_mobs) > 0:
                    can_disembark = True
                    if self.vehicle_type == 'train':
                        if self.attached_label.actor.images[0].current_cell.contained_buildings['train_station'] == 'none':
                            text_tools.print_to_screen("A train can only drop off passengers at a train station.", self.global_manager)
                            can_disembark = False
                    if can_disembark:
                        #if self.attached_label.actor.is_vehicle and self.attached_label.actor.vehicle_type == 'train': #trains can not move after dropping cargo or passenger
                        #    self.attached_label.actor.set_movement_points(0)
                        passenger = self.attached_label.attached_list[self.attached_label.list_index]
                        if passenger.sentry_mode:
                            passenger.set_sentry_mode(False)
                        passenger.selection_sound()
                        self.attached_label.attached_list[self.attached_label.list_index].disembark_vehicle(self.attached_label.actor)
                else:
                    text_tools.print_to_screen("You must select a " + self.vehicle_type + "with passengers to disembark passengers.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not disembark from a " + self.vehicle_type + ".", self.global_manager)

class embark_vehicle_button(label_button):
    '''
    Button that commands a selected mob to embark a vehicle of the correct type in the same tile
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, vehicle_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle this button embarks
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = vehicle_type
        self.was_showing = False
        super().__init__(coordinates, width, height, 'embark', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob can not embark vehicles or if there is no vehicle in the tile to embark, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.controllable:
                result = False
            elif self.attached_label.actor.in_vehicle or self.attached_label.actor.is_vehicle:
                result = False
            elif not self.attached_label.actor.actor_type == 'minister' and not self.attached_label.actor.images[0].current_cell.has_vehicle(self.vehicle_type):
                result = False
        if not result == self.was_showing: #if visibility changes, update actor info display
            self.was_showing = result
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self.attached_label.actor)
        self.was_showing = result
        return(result)
    
    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a selected mob to embark a vehicle of the correct type in the same tile
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                if self.attached_label.actor.images[0].current_cell.has_vehicle(self.vehicle_type):
                    selected_list = actor_utility.get_selected_list(self.global_manager)
                    num_vehicles = 0
                    vehicle = self.attached_label.actor.images[0].current_cell.get_vehicle(self.vehicle_type)
                    rider = self.attached_label.actor
                    can_embark = True
                    if vehicle.vehicle_type == 'train':
                        if vehicle.images[0].current_cell.contained_buildings['train_station'] == 'none':
                            text_tools.print_to_screen("A train can only pick up passengers at a train station.", self.global_manager)
                            can_embark = False
                    if can_embark:
                        if rider.sentry_mode:
                            rider.set_sentry_mode(False)
                        if vehicle.sentry_mode:
                            vehicle.set_sentry_mode(False)
                        rider.embark_vehicle(vehicle)
                        self.global_manager.get('sound_manager').play_sound('voices/ship 1')
                else:
                    text_tools.print_to_screen("You must select a unit in the same tile as a crewed " + self.vehicle_type + " to embark.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not embark a " + self.vehicle_type + ".", self.global_manager)

class cycle_passengers_button(label_button):
    '''
    Button that cycles the order of passengers displayed in a vehicle
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        super().__init__(coordinates, width, height, 'cycle passengers', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a vehicle or if the vehicle does not have enough passengers to cycle through, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.is_vehicle:
                return(False)
            elif not len(self.attached_label.actor.contained_mobs) > 3: #only show if vehicle with 3+ passengers
                return(False)
            self.vehicle_type = self.attached_label.actor.vehicle_type
        return(result)
    
    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the order of passengers displayed in a vehicle
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                moved_mob = self.attached_label.actor.contained_mobs.pop(0)
                self.attached_label.actor.contained_mobs.append(moved_mob)
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self.attached_label.actor) #updates mob info display list to show changed passenger order
            else:
                text_tools.print_to_screen("You are busy and can not cycle passengers.", self.global_manager)

class cycle_work_crews_button(label_button):
    '''
    Button that cycles the order of work crews in a building
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.previous_showing_result = False
        super().__init__(coordinates, width, height, 'cycle work crews', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the displayed tile's cell has a resource building containing more than 3 work crews, otherwise returns False
        '''
        result = super().can_show()
        if result:
            if self.attached_label.actor.cell.contained_buildings['resource'] == 'none':
                self.previous_showing_result = False
                return(False)
            elif not len(self.attached_label.actor.cell.contained_buildings['resource'].contained_work_crews) > 3: #only show if building with 3+ work crews
                self.previous_showing_result = False
                return(False)
        if self.previous_showing_result == False and result == True:
            self.previous_showing_result = result
            self.attached_label.set_label(self.attached_label.message) #update label to update this button's location
        self.previous_showing_result = result
        return(result)
    
    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the order of work crews displayed in a building
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                moved_mob = self.attached_label.actor.cell.contained_buildings['resource'].contained_work_crews.pop(0)
                self.attached_label.actor.cell.contained_buildings['resource'].contained_work_crews.append(moved_mob)
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.attached_label.actor) #updates tile info display list to show changed work crew order
            else:
                text_tools.print_to_screen("You are busy and can not cycle work crews.", self.global_manager)

class work_crew_to_building_button(label_button):
    '''
    Button that commands a work crew to work in a certain type of building in its tile
    '''
    def __init__(self, coordinates, width, height, keybind_id, building_type, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string building_type: Type of building this label attaches workers to, like 'resource building'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.building_type = building_type
        self.attached_work_crew = 'none'
        self.attached_building = 'none'
        self.building_type = building_type
        super().__init__(coordinates, width, height, 'worker to resource', keybind_id, modes, image_id, attached_label, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def update_info(self):
        '''
        Description:
            Updates the building this button assigns workers to depending on the buildings present in this tile
        Input:
            None
        Output:
            None
        '''
        self.attached_work_crew = self.attached_label.actor
        if (not self.attached_work_crew == 'none') and self.attached_work_crew.is_work_crew:
            self.attached_building = self.attached_work_crew.images[0].current_cell.get_intact_building(self.building_type)
        else:
            self.attached_building = 'none'
    
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a work crew, otherwise returns same as superclass
        '''
        result = super().can_show()
        self.update_info()
        if result:
            if (not self.attached_work_crew == 'none') and not (self.attached_work_crew.is_work_crew): #if selected but not worker, return false
                return(False)
        return(result)
    
    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip depending on the building it assigns workers to
        Input:
            None
        Output:
            None
        '''
        if not (self.attached_work_crew == 'none' or self.attached_building == 'none'):
            if self.building_type == 'resource':
                self.set_tooltip(['Assigns the selected work crew to the ' + self.attached_building.name + ', producing ' + self.attached_building.resource_type + ' over time.'])
            else:
                self.set_tooltip(['placeholder'])
        elif not self.attached_work_crew == 'none':
            if self.building_type == 'resource':
                self.set_tooltip(['Assigns the selected work crew to a resource building, producing commodities over time.'])
        else:
            self.set_tooltip(['placeholder'])

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a work crew to work in a certain type of building in its tile
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                if not self.attached_building == 'none':
                    if self.attached_building.scale > len(self.attached_building.contained_work_crews): #if has extra space
                        self.showing_outline = True
                        if self.attached_work_crew.sentry_mode:
                            self.attached_work_crew.set_sentry_mode(False)
                        self.attached_work_crew.work_building(self.attached_building)
                    else:
                        text_tools.print_to_screen("This building is at its work crew capacity.", self.global_manager)
                        text_tools.print_to_screen("Upgrade the building's scale to increase work crew capacity.", self.global_manager)
                else:
                    text_tools.print_to_screen("This work crew must be in the same tile as a resource production building to work in it", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not attach a work crew to a building.", self.global_manager)
            

class trade_button(label_button):
    '''
    Button that commands a caravan to trade with a village
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'trade', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of trading, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not self.attached_label.actor.can_trade):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a caravan to trade with a village
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if current_mob.movement_points >= 1:
                    if self.global_manager.get('money') >= self.global_manager.get('action_prices')['trade']:
                        current_cell = current_mob.images[0].current_cell
                        if current_cell.has_building('village'):
                            if current_cell.get_building('village').population > 0:
                                if current_mob.get_inventory('consumer goods') > 0:
                                    if minister_utility.positions_filled(self.global_manager): #current_mob.check_if_minister_appointed():
                                        if current_mob.sentry_mode:
                                            current_mob.set_sentry_mode(False)
                                        current_mob.start_trade()
                                    else:
                                        text_tools.print_to_screen("You can not do any actions until all ministers have been appointed.", self.global_manager)
                                else:
                                    text_tools.print_to_screen("Trading requires at least 1 unit of consumer goods.", self.global_manager)
                            else:
                                text_tools.print_to_screen("Trading is only possible in a village with population above 0.", self.global_manager)
                        else:
                            text_tools.print_to_screen("Trading is only possible in a village.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You do not have the " + str(self.global_manager.get('action_prices')['trade']) + " money needed to trade with a village.", self.global_manager)
                else:
                    text_tools.print_to_screen("Trading requires all remaining movement points, at least 1", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not trade.", self.global_manager)

class convert_button(label_button):
    '''
    Button that commands a missionaries to convert a native village
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'convert', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a group of missionaries, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not self.attached_label.actor.can_convert):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands missionaries to convert a native village
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if current_mob.movement_points >= 1:
                    if self.global_manager.get('money') >= self.global_manager.get('action_prices')['convert']:
                        current_cell = current_mob.images[0].current_cell
                        if current_cell.has_building('village'):
                            if current_cell.get_building('village').aggressiveness > 1:
                                if current_cell.get_building('village').population > 0:
                                    if current_mob.check_if_minister_appointed():
                                        if current_mob.sentry_mode:
                                            current_mob.set_sentry_mode(False)
                                        current_mob.start_converting()
                                else:
                                    text_tools.print_to_screen("This village has no population and can not be converted.", self.global_manager)
                            else:
                                text_tools.print_to_screen("This village already has the minimum aggressiveness and can not be converted.", self.global_manager)
                        else:
                            text_tools.print_to_screen("Converting is only possible in a village.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You do not have the " + str(self.global_manager.get('action_prices')['convert']) + " money needed to attempt to convert the natives.", self.global_manager)
                else:
                    text_tools.print_to_screen("Converting requires all remaining movement points, at least 1.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not convert.", self.global_manager)

class capture_slaves_button(label_button):
    '''
    Button that commands a battalion to capture slaves from a village
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        super().__init__(coordinates, width, height, 'capture slaves', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a group of missionaries, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not self.attached_label.actor.is_battalion):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a battalion to capture slaves from a native village
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if current_mob.movement_points >= 1:
                    if self.global_manager.get('money') >= self.global_manager.get('action_prices')['capture_slaves']:
                        current_cell = current_mob.images[0].current_cell
                        if current_cell.has_building('village'):
                            if current_cell.get_building('village').population > 0:
                                if current_mob.check_if_minister_appointed():
                                    if current_mob.sentry_mode:
                                        current_mob.set_sentry_mode(False)
                                    current_mob.start_capture_slaves()
                            else:
                                text_tools.print_to_screen("This village has no remaining population to be captured.", self.global_manager)
                        else:
                            text_tools.print_to_screen("Capturing slaves is only possible in a village.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You do not have the " + str(self.global_manager.get('action_prices')['capture_slaves']) + " money needed to attempt to capture slaves.", self.global_manager)
                else:
                    text_tools.print_to_screen("Capturing slaves requires all remaining movement points, at least 1.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not capture slaves.", self.global_manager)

class evangelist_campaign_button(label_button):
    '''
    Button that commands an evangelist to start a religious campaign in Europe
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, campaign_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            string campaign_type: 'religious campaign' or 'public relations campaign', determines which kind of evangelist campaign this button starts
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        #'religious campaign' or 'public relations campaign'
        super().__init__(coordinates, width, height, campaign_type, keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not an evangelist, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not (self.attached_label.actor.is_officer and self.attached_label.actor.officer_type == 'evangelist')):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands an evangelist to start a religious or public relations campaign, depending on button's campaign
                type
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if self.global_manager.get('europe_grid') in current_mob.grids:
                    if current_mob.movement_points >= 1:
                        if self.button_type == 'religious campaign':
                            if self.global_manager.get('money') >= self.global_manager.get('action_prices')['religious_campaign']:
                                if current_mob.check_if_minister_appointed():
                                    if current_mob.sentry_mode:
                                        current_mob.set_sentry_mode(False)
                                    current_mob.start_religious_campaign()
                            else:
                                text_tools.print_to_screen("You do not have the " + str(self.global_manager.get('action_prices')['public_relations_campaign']) + " money needed for a public relations campaign.", self.global_manager)
                        elif self.button_type == 'public relations campaign':
                            if self.global_manager.get('money') >= self.global_manager.get('action_prices')['public_relations_campaign']:
                                if current_mob.check_if_minister_appointed():
                                    if current_mob.sentry_mode:
                                        current_mob.set_sentry_mode(False)
                                    current_mob.start_public_relations_campaign()
                            else:
                                text_tools.print_to_screen("You do not have the " + str(self.global_manager.get('action_prices')['religious_campaign']) + " money needed for a public relations campaign.", self.global_manager)
                    else:
                        text_tools.print_to_screen("A religious campaign requires all remaining movement points, at least 1.", self.global_manager)
                else:
                    text_tools.print_to_screen("Religious campaigns are only possible in Europe", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not start a religious campaign.", self.global_manager)

class take_loan_button(label_button):
    '''
    Button that commands a merchant to start a loan search in Europe
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'take loan', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a merchant, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not (self.attached_label.actor.is_officer and self.attached_label.actor.officer_type == 'merchant')):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a merchant to start a loan search
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if self.global_manager.get('europe_grid') in current_mob.grids:
                    if current_mob.movement_points >= 1:
                        if self.global_manager.get('money') >= self.global_manager.get('action_prices')['loan']:
                            if current_mob.check_if_minister_appointed():
                                if current_mob.sentry_mode:
                                    current_mob.set_sentry_mode(False)
                                current_mob.start_loan_search()
                        else:
                            text_tools.print_to_screen("You do not have the " + str(self.global_manager.get('action_prices')['loan_search']) + " money needed to search for a loan offer.", self.global_manager)
                    else:
                        text_tools.print_to_screen("Searching for a loan offer requires all remaining movement points, at least 1.", self.global_manager)
                else:
                    text_tools.print_to_screen("A merchant can only search for a loan while in Europe", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not search for a loan offer.", self.global_manager)

class labor_broker_button(label_button):
    '''
    Buttons that commands a vehicle without crew or an officer to use a labor broker in a port to recruit a worker from a nearby village, with a price based on the village's aggressiveness and distance
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'labor broker', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not an officer or a vehicle without crew, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not ((self.attached_label.actor.is_officer and not self.attached_label.actor.officer_type == 'evangelist') or (self.attached_label.actor.is_vehicle and self.attached_label.actor.crew == 'none'))):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands an officer or vehicle without crew to use a labor broker in a port
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if self.global_manager.get('strategic_map_grid') in current_mob.grids:
                    if current_mob.images[0].current_cell.has_intact_building('port'):
                        cost_info_list = self.get_cost()
                        if not cost_info_list == 'none':
                            if current_mob.movement_points >= 1:
                                if self.global_manager.get('money_tracker').get() >= cost_info_list[1]:
                                    if current_mob.sentry_mode:
                                        current_mob.set_sentry_mode(False)
                                    choice_info_dict = {'recruitment_type': 'African worker labor broker', 'cost': cost_info_list[1], 'mob_image_id': 'mobs/African worker/default.png', 'type': 'recruitment',
                                        'source_type': 'labor broker', 'village': cost_info_list[0]}
                                    self.global_manager.get('actor_creation_manager').display_recruitment_choice_notification(choice_info_dict, 'African workers', self.global_manager)
                                else:
                                    text_tools.print_to_screen("You can not afford the recruitment cost of " + str(cost_info_list[1]) + " for the cheapest available worker. ", self.global_manager)
                            else:
                                text_tools.print_to_screen("Using a labor broker requires all remaining movement points, at least 1.", self.global_manager)
                        else:
                            text_tools.print_to_screen("There are no eligible villages to recruit workers from.", self.global_manager)
                    else:
                        text_tools.print_to_screen("A labor broker can only be used at a port.", self.global_manager)
                else:
                    text_tools.print_to_screen("A labor broker can only be used at a port.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not use a labor broker.", self.global_manager)

    def get_cost(self):
        '''
        Description:
            Calculates and returns the cost of using a labor broker in a port at the currently selected unit's location, based on nearby villages' aggressiveness and distance from the port
        Input:
            None
        Output:
            string/list: If no valid villages are found, returns 'none'. Otherwise, returns a list with the village as the first item and the cost as the second item
        '''
        lowest_cost_village = 'none'
        lowest_cost = 0
        for current_village in self.global_manager.get('village_list'):
            if current_village.population > 0:
                distance = int(utility.find_object_distance(current_village, self.attached_label.actor))
                cost = (5 * current_village.aggressiveness) + distance
                if cost < lowest_cost or lowest_cost_village == 'none':
                    lowest_cost_village = current_village
                    lowest_cost = cost
        if lowest_cost_village == 'none':
            return('none')
        else:
            return([lowest_cost_village, lowest_cost])

class advertising_campaign_button(label_button):
    '''
    Button that starts advertising campaign commodity selection
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'advertising campaign', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a merchant, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not (self.attached_label.actor.is_officer and self.attached_label.actor.officer_type == 'merchant')):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button starts advertising campaign commodity selection, starting an advertising campaign for the selected
                commodity when one is clicked
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if self.global_manager.get('europe_grid') in current_mob.grids:
                    if current_mob.movement_points >= 1:
                        if self.global_manager.get('money') >= self.global_manager.get('action_prices')['advertising_campaign']:
                            if current_mob.check_if_minister_appointed():
                                if current_mob.sentry_mode:
                                    current_mob.set_sentry_mode(False)
                                if not self.global_manager.get('current_game_mode') == 'europe':
                                    game_transitions.set_game_mode('europe', self.global_manager)
                                    current_mob.select()
                                text_tools.print_to_screen("Select a commodity to advertise, or click elsewhere to cancel: ", self.global_manager)
                                self.global_manager.set('choosing_advertised_commodity', True)
                                #current_mob.start_religious_campaign()
                        else:
                            text_tools.print_to_screen("You do not have the " + str(self.global_manager.get('action_prices')['advertising_campaign']) + " money needed for an advertising campaign.", self.global_manager)
                    else:
                        text_tools.print_to_screen("An advertising campaign requires all remaining movement points, at least 1.", self.global_manager)
                else:
                    text_tools.print_to_screen("Advertising campaigns are only possible in Europe", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not start an advertising campaign.", self.global_manager)

class track_beasts_button(label_button):
    '''
    Button that orders a safari to spend 1 movement point to attempt to reveal beasts in its tile and adjacent explored tiles
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'track beasts', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a safari, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not (self.attached_label.actor.is_group and self.attached_label.actor.is_safari)):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a safari to attempt to track beasts
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if self.global_manager.get('strategic_map_grid') in current_mob.grids:
                    if current_mob.movement_points >= 1:
                        if self.global_manager.get('money') >= self.global_manager.get('action_prices')['track_beasts']:
                            if current_mob.check_if_minister_appointed():
                                if current_mob.sentry_mode:
                                    current_mob.set_sentry_mode(False)
                                current_mob.track_beasts()
                        else:
                            text_tools.print_to_screen("You do not have the " + str(self.global_manager.get('action_prices')['track_beasts']) + " money needed to search for a loan offer.", self.global_manager)
                    else:
                        text_tools.print_to_screen("Tracking beasts requires 1 movement point.", self.global_manager)
                else:
                    text_tools.print_to_screen("A safari can only track beasts in Africa", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not track beasts.", self.global_manager)

class switch_theatre_button(label_button):
    '''
    Button starts choosing a destination for a ship to travel between theatres, like between Europe and Africa. A destination is chosen when the player clicks a tile in another theatre.
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'switch theatre', keybind_id, modes, image_id, attached_label, global_manager)

    def on_click(self):      
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button starts choosing a destination for a ship to travel between theatres, like between Europe and Africa. A
                destination is chosen when the player clicks a tile in another theatre.
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if current_mob.movement_points >= 1:
                    if not (self.global_manager.get('strategic_map_grid') in current_mob.grids and (current_mob.y > 1 or (current_mob.y == 1 and not current_mob.images[0].current_cell.has_intact_building('port')))): #can leave if in ocean or if in coastal port
                        if current_mob.can_leave(): #not current_mob.grids[0] in self.destination_grids and
                            if current_mob.sentry_mode:
                                current_mob.set_sentry_mode(False)
                            if not self.global_manager.get('current_game_mode') == 'strategic':
                                game_transitions.set_game_mode('strategic', self.global_manager)
                                current_mob.select()
                            current_mob.clear_automatic_route()
                            current_mob.end_turn_destination = 'none'
                            self.global_manager.set('choosing_destination', True)
                            self.global_manager.set('choosing_destination_info_dict', {'chooser': current_mob}) #, 'destination_grids': self.destination_grids
                    else:
                        text_tools.print_to_screen("You are inland and can not cross the ocean.", self.global_manager) 
                else:
                    text_tools.print_to_screen("Crossing the ocean requires all remaining movement points, at least 1.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not move.", self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of traveling between theatres, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.controllable:
                return(False)
            if (not self.attached_label.actor.can_travel()): 
                return(False)
        return(result) 

class build_train_button(label_button):
    '''
    Button that commands a construction gang to assemble a train at a train station
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'build train', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of constructing buildings, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not self.attached_label.actor.can_construct):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a construction gang to assemble a train at a train station
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                self.showing_outline = True
                if self.attached_label.actor.movement_points >= 1:
                    cost = actor_utility.get_building_cost(self.global_manager, self.attached_label.actor, 'train')
                    if self.global_manager.get('money') >= cost: #self.global_manager.get('building_prices')['train']:
                        if not self.global_manager.get('europe_grid') in self.attached_label.actor.grids:
                            if not self.attached_label.actor.images[0].current_cell.terrain == 'water':
                                if self.attached_label.actor.images[0].current_cell.has_intact_building('train_station'): #not self.attached_label.actor.images[0].current_cell.contained_buildings['train_station'] == 'none': #if train station present
                                    if self.attached_label.actor.check_if_minister_appointed():
                                        if self.attached_label.actor.sentry_mode:
                                            self.attached_label.actor.set_sentry_mode(False)
                                        self.construct()
                                else:
                                    text_tools.print_to_screen("A train can only be assembled on a train station.", self.global_manager)
                            else:
                                text_tools.print_to_screen("A train can only be assembled on a train station.", self.global_manager)
                        else:
                            text_tools.print_to_screen("A train can only be assembled on a train station.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You do not have the " + str(cost) + " money needed to assemble a train.", self.global_manager)
                else:
                    text_tools.print_to_screen("You do not have enough movement points to assemble a train.", self.global_manager)
                    text_tools.print_to_screen("You have " + str(self.attached_label.actor.movement_points) + " movement points while 1 is required.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not build a train.", self.global_manager)

    def construct(self):
        '''
        Description:
            Commands the selected mob to construct a train
        Input:
            None
        Output:
            None
        '''
        building_info_dict = {}
        building_info_dict['building_type'] = 'train'
        building_info_dict['building_name'] = 'train'
        self.attached_label.actor.start_construction(building_info_dict)

class build_steamboat_button(label_button):
    '''
    Button that commands a construction gang to assemble a steammboat at a port
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'build steamboat', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of constructing buildings, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not self.attached_label.actor.can_construct):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a construction gang to assemble a steamboat at a port
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                self.showing_outline = True
                if self.attached_label.actor.movement_points >= 1:
                    cost = actor_utility.get_building_cost(self.global_manager, self.attached_label.actor, 'steamboat')
                    if self.global_manager.get('money') >= cost:
                        if not self.global_manager.get('europe_grid') in self.attached_label.actor.grids:
                            if not self.attached_label.actor.images[0].current_cell.terrain == 'water':
                                if self.attached_label.actor.images[0].current_cell.has_intact_building('port'): #not self.attached_label.actor.images[0].current_cell.contained_buildings['train_station'] == 'none': #if train station present
                                    if self.attached_label.actor.adjacent_to_river():
                                        if self.attached_label.actor.check_if_minister_appointed():
                                            if self.attached_label.actor.sentry_mode:
                                                self.attached_label.actor.set_sentry_mode(False)
                                            self.construct()
                                    else:
                                        text_tools.print_to_screen("A steamboat assembled here would not be able to access any rivers.", self.global_manager)
                                else:
                                    text_tools.print_to_screen("A steamboat can only be assembled on a port.", self.global_manager)
                            else:
                                text_tools.print_to_screen("A steamboat can only be assembled on a port.", self.global_manager)
                        else:
                            text_tools.print_to_screen("A steamboat can only be assembled on a port.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You do not have the " + str(cost) + " money needed to assemble a steamboat.", self.global_manager)
                else:
                    text_tools.print_to_screen("You do not have enough movement points to assemble a steamboat.", self.global_manager)
                    text_tools.print_to_screen("You have " + str(self.attached_label.actor.movement_points) + " movement points while 1 is required.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not build a train.", self.global_manager)

    def construct(self):
        '''
        Description:
            Commands the selected mob to construct a steamboat
        Input:
            None
        Output:
            None
        '''
        building_info_dict = {}
        building_info_dict['building_type'] = 'steamboat'
        building_info_dict['building_name'] = 'steamboat'
        self.attached_label.actor.start_construction(building_info_dict)


class construction_button(label_button): #coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager
    '''
    Button that commands a group to construct a certain type of building
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, attached_label, building_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            label attached_label: Label that this button is attached to
            string building_type: Type of building that this button builds, like 'resource'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.building_type = building_type
        self.attached_mob = 'none'
        self.attached_tile = 'none'
        self.building_name = 'none'
        self.requirement = 'can_construct'
        image_id = 'buttons/default_button.png'
        if self.building_type == 'resource':
            self.attached_resource = 'none'
            image_id = global_manager.get('resource_building_button_dict')['none']
        elif self.building_type == 'port':
            image_id = 'buildings/buttons/port.png'
            self.building_name = 'port'
        elif self.building_type == 'infrastructure':
            self.road_image_id = 'buildings/buttons/road.png'
            self.railroad_image_id = 'buildings/buttons/railroad.png'
            image_id = self.road_image_id
        elif self.building_type == 'train_station':
            image_id = 'buildings/buttons/train_station.png'
            self.building_name = 'train station'
        elif self.building_type == 'trading_post':
            image_id = 'buildings/buttons/trading_post.png'
            self.building_name = 'trading post'
            self.requirement = 'can_trade'
        elif self.building_type == 'mission':
            image_id = 'buildings/buttons/mission.png'
            self.building_name = 'mission'
            self.requirement = 'can_convert'
        elif self.building_type == 'fort':
            image_id = 'buildings/buttons/fort.png'
            self.building_name = 'fort'
            self.requirement = 'is_battalion'
        super().__init__(coordinates, width, height, 'construction', keybind_id, modes, image_id, attached_label, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def update_info(self):
        '''
        Description:
            Updates the exact kind of building constructed by this button depending on what is in the selected mob's tile, like building a road or upgrading a previously constructed road to a railroad
        Input:
            None
        Output:
            None
        '''
        self.attached_mob = self.attached_label.actor #new_attached_mob
        if (not self.attached_mob == 'none') and (not self.attached_mob.images[0].current_cell == 'none'):
            self.attached_tile = self.attached_mob.images[0].current_cell.tile
            if self.attached_mob.can_construct:
                if self.building_type == 'resource':
                    if self.attached_tile.cell.resource in self.global_manager.get('collectable_resources'):
                        self.attached_resource = self.attached_tile.cell.resource
                        self.image.set_image(self.global_manager.get('resource_building_button_dict')[self.attached_resource])
                        if self.attached_resource in ['gold', 'iron', 'copper', 'diamond']: #'coffee', 'copper', 'diamond', 'exotic wood', 'fruit', 'gold', 'iron', 'ivory', 'rubber'
                            self.building_name = self.attached_resource + ' mine'
                        elif self.attached_resource in ['exotic wood', 'fruit', 'rubber', 'coffee']:
                            self.building_name = self.attached_resource + ' plantation'
                        elif self.attached_resource == 'ivory':
                            self.building_name = 'ivory camp'
                    else:
                        self.attached_resource = 'none'
                        self.building_name = 'none'
                        self.image.set_image(self.global_manager.get('resource_building_button_dict')['none'])
                elif self.building_type == 'infrastructure':
                    current_infrastructure = self.attached_tile.cell.contained_buildings['infrastructure']
                    if current_infrastructure == 'none':
                        self.building_name = 'road'
                        self.image.set_image('buildings/buttons/road.png')
                    else: #if has road or railroad, show railroad icon
                        self.building_name = 'railroad'
                        self.image.set_image('buildings/buttons/railroad.png')

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of constructing the building that this button constructs, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            self.update_info()
            can_create = 'none'
            if self.requirement == 'can_construct':
                can_create = self.attached_label.actor.can_construct
            elif self.requirement == 'can_trade':
                can_create = self.attached_label.actor.can_trade
            elif self.requirement == 'can_convert':
                can_create = self.attached_label.actor.can_convert
            elif self.requirement == 'is_battalion':
                can_create = self.attached_label.actor.is_battalion
            if not can_create: #show if unit selected can create this building
                return(False)
            if not self.attached_tile == 'none':
                if self.attached_tile.cell.has_building(self.building_type) and not self.building_type == 'infrastructure': #if building already present, do not show
                    return(False)
        return(result) 

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip depending on the type of building it constructs
        Input:
            None
        Output:
            None
        '''
        message = []
        if self.building_type == 'resource':
            if self.attached_resource == 'none':
                message.append('Builds a resource production facility to which work crews can attach to produces commodities over time.')
                message.append('Can only be built in the same tile as a resource.')
            else:
                message.append('Builds a ' + self.building_name + ' to which work crews can attach to produce ' + self.attached_resource + ' over time')
                message.append('Can only be built in the same tile as a ' + self.attached_resource + ' resource.')

        elif self.building_type == 'port':
            message.append('Builds a port, allowing steamships and steamboats to enter this tile')
            message.append('Can only be built adjacent to water')

        elif self.building_type == 'train_station':
            message.append('Builds a train station, allowing trains to pick up and drop off passengers and cargo')
            message.append('Can only be built on a railroad')
            
        elif self.building_type == 'infrastructure':
            if self.building_name == 'railroad':
                message.append("Upgrades this tile's road into a railroad, allowing trains to move through this tile")
                message.append("Retains the benefits of a road")
            elif self.building_name == 'road':
                message.append('Builds a road, halving the cost to move between this tile and other tiles with roads or railroads')
                message.append('A road can be upgraded into a railroad that allows trains to move through this tile')
            else:
                self.set_tooltip(message) #can't get building cost without road/railroad type
                return()
                
        elif self.building_type == 'trading_post':
            message.append('Builds a trading post, increasing the success chance and reducing the risk when caravans trade with the attached village')
            message.append('Can only be built in a village')
            
        elif self.building_type == 'mission':
            message.append('Builds a mission, increasing the success chance and reducing the risk when missionaries convert the attached village')
            message.append('Can only be built in a village')

        elif self.building_type == 'fort':
            message.append('Builds a fort, increasing the combat effectiveness of your units standing in this tile')
    
        else:
            message.append('placeholder')

        if self.building_type in ['train_station', 'port', 'resource']:
            message.append("Also upgrades this tile's warehouses by 9 inventory capacity, or creates new warehouses if none are present")
        
        base_cost = actor_utility.get_building_cost(self.global_manager, 'none', self.building_type, self.building_name)
        cost = actor_utility.get_building_cost(self.global_manager, self.attached_mob, self.building_type, self.building_name)
        
        message.append('Attempting to build costs ' + str(cost) + ' money and all remaining movement points, at least 1')
        if self.building_type in ['train', 'steamboat']:
            message.append("Unlike buildings, the cost of vehicle assembly is not impacted by local terrain")
            
        if (not self.attached_mob == 'none') and self.global_manager.get('strategic_map_grid') in self.attached_mob.grids:
            terrain = self.attached_mob.images[0].current_cell.terrain
            message.append(utility.generate_capitalized_article(self.building_name) + self.building_name + " " + utility.conjugate("cost", self.building_name) + " " + str(base_cost) + " money by default, which is multiplied by " + str(self.global_manager.get('terrain_build_cost_multiplier_dict')[terrain]) + " when built in " + terrain + " terrain")
        self.set_tooltip(message)
        

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a mob to construct a certain type of building
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                self.showing_outline = True
                if self.attached_mob.movement_points >= 1:
                    cost = actor_utility.get_building_cost(self.global_manager, self.attached_mob, self.building_type, self.building_name)
                    if self.global_manager.get('money') >= cost:
                        current_building = self.attached_tile.cell.get_building(self.building_type)
                        if current_building == 'none' or (self.building_name == 'railroad' and current_building.is_road): #able to upgrade to railroad even though road is present, later add this to all upgradable buildings
                            if self.global_manager.get('strategic_map_grid') in self.attached_mob.grids:
                                if not self.attached_tile.cell.terrain == 'water':
                                    if self.attached_label.actor.check_if_minister_appointed():
                                        if self.building_type == 'resource':
                                            if not self.attached_resource == 'none':
                                                #if self.attached_label.actor.check_if_minister_appointed():
                                                if self.attached_label.actor.sentry_mode:
                                                    self.attached_label.actor.set_sentry_mode(False)
                                                self.construct()
                                            else:
                                                text_tools.print_to_screen("This building can only be built in tiles with resources.", self.global_manager)
                                        elif self.building_type == 'port':
                                            if self.attached_mob.adjacent_to_water():
                                                if not self.attached_mob.images[0].current_cell.terrain == 'water':
                                                    #if self.attached_label.actor.check_if_minister_appointed():
                                                    if self.attached_label.actor.sentry_mode:
                                                        self.attached_label.actor.set_sentry_mode(False)
                                                    self.construct()
                                            else:
                                                text_tools.print_to_screen("This building can only be built in tiles adjacent to discovered water.", self.global_manager)
                                        elif self.building_type == 'train_station':
                                            if self.attached_tile.cell.has_intact_building('railroad'):
                                                #if self.attached_label.actor.check_if_minister_appointed():
                                                if self.attached_label.actor.sentry_mode:
                                                    self.attached_label.actor.set_sentry_mode(False)
                                                self.construct()
                                            else:
                                                text_tools.print_to_screen("This building can only be built on railroads.", self.global_manager)
                                        elif self.building_type == 'trading_post' or self.building_type == 'mission':
                                            if self.attached_tile.cell.has_building('village'):
                                                #if self.attached_label.actor.check_if_minister_appointed():
                                                if self.attached_label.actor.sentry_mode:
                                                    self.attached_label.actor.set_sentry_mode(False)
                                                self.construct()
                                            else:
                                                text_tools.print_to_screen("This building can only be built in villages.", self.global_manager)
                                        elif self.building_type in ['infrastructure', 'fort']:
                                            #if self.attached_label.actor.check_if_minister_appointed():
                                            if self.attached_label.actor.sentry_mode:
                                                self.attached_label.actor.set_sentry_mode(False)
                                            self.construct()
                                else:
                                    text_tools.print_to_screen("This building can not be built in water.", self.global_manager)
                            else:
                                text_tools.print_to_screen("This building can only be built in Africa.", self.global_manager)
                        else:
                            if self.building_type == 'infrastructure': #if railroad
                                text_tools.print_to_screen("This tile already contains a railroad.", self.global_manager)
                            else:
                                text_tools.print_to_screen("This tile already contains a " + self.building_type + " building.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You do not have the " + str(cost) + " money needed to attempt to build a " + self.building_name + ".", self.global_manager)
                else:
                    text_tools.print_to_screen("You do not have enough movement points to construct a building.", self.global_manager)
                    text_tools.print_to_screen("You have " + str(self.attached_mob.movement_points) + " movement points while 1 is required.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not start construction.", self.global_manager)
            
    def construct(self):
        '''
        Description:
            Commands the selected mob to construct a certain type of building, depending on this button's building_type
        Input:
            None
        Output:
            None
        '''
        building_info_dict = {}
        building_info_dict['building_type'] = self.building_type
        building_info_dict['building_name'] = self.building_name
        if self.building_type == 'resource':
            building_info_dict['attached_resource'] = self.attached_resource
        self.attached_mob.start_construction(building_info_dict)

class repair_button(label_button):
    '''
    Button that commands a group to repair a certain type of building
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, attached_label, building_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            label attached_label: Label that this button is attached to
            string building_type: Type of building that this button builds, like 'resource'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.building_type = building_type
        self.attached_mob = 'none'
        self.attached_tile = 'none'
        self.building_name = 'none'
        self.requirement = 'can_construct'
        image_id = 'buildings/buttons/repair_' + building_type + '.png'
        if self.building_type == 'resource':
            self.attached_resource = 'none'
        else:
            self.building_name = text_tools.remove_underscores(self.building_type)
            if self.building_type == 'trading_post':
                self.requirement = 'can_trade'
            elif self.building_type == 'mission':
                self.requirement = 'can_convert'
            elif self.building_type == 'fort':
                self.requirement = 'is_battalion'
            else:
                self.requirement = 'none'
        super().__init__(coordinates, width, height, 'construction', keybind_id, modes, image_id, attached_label, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def update_info(self):
        '''
        Description:
            If this is a resource production building repair button, updates the button's description based on the type of resource production building in the current tile
        Input:
            None
        Output:
            None
        '''
        self.attached_mob = self.attached_label.actor #new_attached_mob
        if self.building_type == 'resource':
            if (not self.attached_mob == 'none') and (not self.attached_mob.images[0].current_cell == 'none'):
                self.attached_tile = self.attached_mob.images[0].current_cell.tile
                if self.attached_mob.can_construct:
                    if self.attached_tile.cell.resource in self.global_manager.get('collectable_resources'):
                        self.attached_resource = self.attached_tile.cell.resource
                        #self.image.set_image(self.global_manager.get('resource_building_button_dict')[self.attached_resource])
                        if self.attached_resource in ['gold', 'iron', 'copper', 'diamond']: #'coffee', 'copper', 'diamond', 'exotic wood', 'fruit', 'gold', 'iron', 'ivory', 'rubber'
                            self.building_name = self.attached_resource + ' mine'
                        elif self.attached_resource in ['exotic wood', 'fruit', 'rubber', 'coffee']:
                            self.building_name = self.attached_resource + ' plantation'
                        elif self.attached_resource == 'ivory':
                            self.building_name = 'ivory camp'
                    else:
                        self.attached_resource = 'none'
                        self.building_name = 'none'
                        #self.image.set_image(self.global_manager.get('resource_building_button_dict')['none'])
        else:
            if (not self.attached_mob == 'none') and (not self.attached_mob.images[0].current_cell == 'none'):
                self.attached_tile = self.attached_mob.images[0].current_cell.tile
                self.building_name = self.building_type

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of repairing this button's building, otherwise returns same as superclass. A group can repair a building if it is able to build it, and construction gang's can
                repair any type of building
        '''
        result = super().can_show()
        if result:
            if self.attached_label.actor.can_construct or (self.attached_label.actor.can_trade and self.requirement == 'can_trade') or (self.attached_label.actor.can_convert and self.requirement == 'can_convert') or (self.attached_label.actor.is_battalion and self.requirement == 'is_battalion'):
                #construction gangs can repair all buildings, caravans can only repair trading posts, missionaries can only repair missions, battalions can only repair forts
                attached_building = self.attached_label.actor.images[0].current_cell.get_building(self.building_type)
                if (not attached_building == 'none') and attached_building.damaged:
                    self.update_info()
                    return(result)
        return(False) 

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip depending on the type of building it repairs
        Input:
            None
        Output:
            None
        '''
        message = []
        if self.can_show():
            message.append("Attempts to repair the " + self.building_name + " in this tile, restoring it to full functionality")
            if self.building_type in ['port', 'train_station', 'resource']:
                message.append("If successful, also automatically repairs this tile's warehouses")
            message.append("Attempting to repair costs " + str(self.attached_tile.cell.get_building(self.building_type).get_repair_cost()) + " money and all remaining movement points, at least 1")
        self.set_tooltip(message)  

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a mob to repair a certain type of building
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                self.showing_outline = True
                if self.attached_mob.movement_points >= 1:
                    attached_building = self.attached_label.actor.images[0].current_cell.get_building(self.building_type)
                    cost = attached_building.get_repair_cost()
                    if self.global_manager.get('money') >= cost: #self.global_manager.get('building_prices')[self.building_type] / 2:
                        if self.attached_mob.sentry_mode:
                            self.attached_mob.set_sentry_mode(False)
                        #current_building = self.attached_label.actor.images[0].current_cell.get_building(self.building_type)
                        self.repair()
                    else:
                        text_tools.print_to_screen("You do not have the " + str(cost) + " money needed to attempt to repair the " + self.building_name + ".", self.global_manager)
                else:
                    text_tools.print_to_screen("You do not have enough movement points to repair a building.", self.global_manager)
                    text_tools.print_to_screen("You have " + str(self.attached_mob.movement_points) + " movement points while 1 is required.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not start construction.", self.global_manager)
            
    def repair(self):
        '''
        Description:
            Commands the selected mob to repair a certain type of building, depending on this button's building_type
        Input:
            None
        Output:
            None
        '''
        building_info_dict = {}
        building_info_dict['building_type'] = self.building_type
        building_info_dict['building_name'] = self.building_name
        if self.building_type == 'resource':
            building_info_dict['attached_resource'] = self.attached_resource
        self.attached_mob.start_repair(building_info_dict)

class upgrade_button(label_button):
    '''
    Button that commands a construction gang to upgrade a certain aspect of a building
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, attached_label, base_building_type, upgrade_type, global_manager): #base_building_type = 'resource', upgrade_type = 'efficiency'
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            label attached_label: Label that this button is attached to
            string base_building_type: Type of building that this button upgrades, like 'resource'
            string upgrade_type: Aspect of building upgraded by this button, like 'scale' or 'efficiency'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.base_building_type = base_building_type
        self.upgrade_type = upgrade_type
        self.attached_mob = 'none'
        self.attached_tile = 'none'
        self.attached_building = 'none'
        image_id = 'buttons/upgrade_' + self.upgrade_type + '_button.png'
        super().__init__(coordinates, width, height, 'construction', keybind_id, modes, image_id, attached_label, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def update_info(self):
        '''
        Description:
            Updates which building object is attached to this button based on the selected construction gang's location relative to buildings of this button's base building type
        Input:
            None
        Output:
            None
        '''
        self.attached_building = 'none'
        self.attached_mob = self.attached_label.actor #new_attached_mob
        if (not self.attached_mob == 'none') and (not self.attached_mob.images[0].current_cell == 'none'):
            self.attached_tile = self.attached_mob.images[0].current_cell.tile
            if self.attached_mob.can_construct:
                if not self.attached_tile.cell.contained_buildings[self.base_building_type] == 'none':
                    self.attached_building = self.attached_tile.cell.get_intact_building(self.base_building_type) #contained_buildings[self.base_building_type]

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of upgrading buildings or if there is no valid building in its tile to upgrade, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            self.update_info()
            if (not self.attached_label.actor.can_construct): #show if unit selected can create this building
                return(False)
            if self.attached_building == 'none' or not self.attached_building.can_upgrade(self.upgrade_type):
                return(False)
        return(result) 

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip depending on its attached building and the aspect it upgrades
        Input:
            None
        Output:
            None
        '''
        message = []
        if not self.attached_building == 'none':
            if self.upgrade_type == 'scale':
                message.append("Increases the maximum number of work crews that can be attached to this " + self.attached_building.name + " from " + str(self.attached_building.scale) + " to " + str(self.attached_building.scale + 1) + ".")
            elif self.upgrade_type == 'efficiency':
                message.append("Increases the number of " + self.attached_building.resource_type + " production attempts made by work crews attached to this " + self.attached_building.name + " from " + str(self.attached_building.efficiency) + " to " + str(self.attached_building.efficiency + 1) + " per turn.")
            elif self.upgrade_type == 'warehouse_level':
                message.append("Increases the level of this tile's warehouses from " + str(self.attached_building.warehouse_level) + " to " + str(self.attached_building.warehouse_level + 1) + ", increasing inventory capacity by 9")
            else:
                message.append('placeholder')
            message.append('Attempting to upgrade costs ' + str(self.attached_building.get_upgrade_cost()) + ' money and increases with each future upgrade to this building.')
            message.append("Unlike new buildings, the cost of building upgrades is not impacted by local terrain")
        self.set_tooltip(message)
        

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a construction gang to upgrade part of a certain building in its tile
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                self.showing_outline = True
                if self.attached_mob.movement_points >= 1:
                    if self.global_manager.get('money') >= self.attached_building.get_upgrade_cost():
                        if self.attached_mob.sentry_mode:
                            self.attached_mob.set_sentry_mode(False)
                                                    
                        building_info_dict = {}
                        building_info_dict['upgrade_type'] = self.upgrade_type
                        building_info_dict['building_name'] = self.attached_building.name
                        building_info_dict['upgraded_building'] = self.attached_building
                        self.attached_mob.start_upgrade(building_info_dict)
                    else:
                        text_tools.print_to_screen("You do not have the " + str(self.attached_building.get_upgrade_cost()) + " money needed to upgrade this building.", self.global_manager)
                else:
                    text_tools.print_to_screen("You do not have enough movement points to upgrade a building.", self.global_manager)
                    text_tools.print_to_screen("You have " + str(self.attached_mob.movement_points) + " movement points while 1 is required.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not start upgrading.", self.global_manager)

class appoint_minister_button(label_button):
    '''
    Button that appoints the selected minister to the office corresponding to this button
    '''
    def __init__(self, coordinates, width, height, attached_label, appoint_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            label attached_label: Label that this button is attached to
            string appoint_type: Office that this button appoints ministers to, like "Minister of Trade"
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.appoint_type = appoint_type
        super().__init__(coordinates, width, height, 'appoint minister', 'none', ['ministers'], 'ministers/icons/' + global_manager.get('minister_type_dict')[self.appoint_type] + '.png', attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the minister office that this button is attached to is open, otherwise returns False
        '''
        if super().can_show():
            displayed_minister = self.global_manager.get('displayed_minister')
            if (not displayed_minister == 'none') and displayed_minister.current_position == 'none': #if there is an available minister displayed
                if self.global_manager.get('current_ministers')[self.appoint_type] == 'none': #if the position that this button appoints is available
                    return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button appoints the selected minister to the office corresponding to this button
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                self.showing_outline = True
                appointed_minister = self.global_manager.get('displayed_minister')
                if not appointed_minister.just_removed:
                    appointed_minister.respond('first hired')
                appointed_minister.appoint(self.appoint_type)
                minister_utility.calibrate_minister_info_display(self.global_manager, appointed_minister)
            else:
                text_tools.print_to_screen("You are busy and can not appoint a minister.", self.global_manager)

class remove_minister_button(label_button):
    '''
    Button that removes the selected minister from their current office
    '''
    def __init__(self, coordinates, width, height, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'remove minister', 'none', ['ministers'], 'buttons/remove_minister_button.png', attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the selected minister is currently in an office, otherwise returns False
        '''
        if super().can_show():
            displayed_minister = self.global_manager.get('displayed_minister')
            if (not displayed_minister == 'none') and (not displayed_minister.current_position == 'none'): #if there is an available minister displayed
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected minister from their current office, returning them to the pool of available
                ministers
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                self.showing_outline = True
                appointed_minister = self.global_manager.get('displayed_minister')
                #appointed_minister.appoint('none')
                public_opinion_penalty = appointed_minister.status_number
                text = "Are you sure you want to remove " + appointed_minister.name + " from office? If removed, he will return to the pool of available ministers and be available to reappoint until the end of the turn. /n /n."
                text += "Removing " + appointed_minister.name + " from office would incur a small public opinion penalty of " + str(public_opinion_penalty) + ", even if he were reappointed. /n /n"
                text += appointed_minister.name + " would expect to be reappointed to a different position by the end of the turn, and would be fired permanently and incur a much larger public opinion penalty if not reappointed. /n /n"
                if appointed_minister.status_number >= 3:
                    if appointed_minister.status_number == 4:
                        text += appointed_minister.name + " is of extremely high social status, and firing him would cause a national outrage. /n /n"
                    else:
                        text += appointed_minister.name + " is of high social status, and firing him would reflect particularly poorly on your company. /n /n"
                elif appointed_minister.status_number == 1:
                    text += appointed_minister.name + " is of low social status, and firing him would have a relatively minimal impact on your company's reputation. /n /n"
                notification_tools.display_choice_notification(text, ['confirm remove minister', 'none'], {}, self.global_manager)
                #appointed_minister.display_message(text)
                #appointed_minister.just_removed = True
                #self.global_manager.get('public_opinion_tracker').change(-1 * public_opinion_penalty)
            else:
                text_tools.print_to_screen("You are busy and can not remove a minister.", self.global_manager)

class to_trial_button(label_button):
    '''
    Button that goes to the trial screen to remove the selected minister from their current office
    '''
    def __init__(self, coordinates, width, height, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'to trial', 'none', attached_label.modes, 'buttons/to_trial_button.png', attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if a non-prosecutor minister with an office to be removed from is selected
        '''
        if super().can_show():
            displayed_minister = self.global_manager.get('displayed_minister')
            if (not displayed_minister == 'none') and (not displayed_minister.current_position in ['none', 'Prosecutor']): #if there is an available non-prosecutor minister displayed
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button goes to the trial screen to remove the selected minister from the game and confiscate a portion of their
                stolen money
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                if self.global_manager.get('money') >= self.global_manager.get('action_prices')['trial']:
                    if minister_utility.positions_filled(self.global_manager):
                        if len(self.global_manager.get('minister_list')) > 8: #if any available appointees
                            self.showing_outline = True
                            defense = self.global_manager.get('displayed_minister')
                            prosecution = self.global_manager.get('current_ministers')['Prosecutor']
                            game_transitions.set_game_mode('trial', self.global_manager)
                            minister_utility.trial_setup(defense, prosecution, self.global_manager) #sets up defense and prosecution displays
                        else:
                            text_tools.print_to_screen("There are currently no available appointees to replace this minister in the event of a successful trial.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You have not yet appointed a minister in each office.", self.global_manager)
                        text_tools.print_to_screen("Press Q to view the minister interface.", self.global_manager)
                else:
                    text_tools.print_to_screen("You do not have the " + str(self.global_manager.get('action_prices')['trial']) + " money needed to start a trial.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not start a trial.", self.global_manager)   

class fabricate_evidence_button(label_button):
    '''
    Button in the trial screen that fabricates evidence to use against the defense in the current trial. Fabricated evidence disappears at the end of the trial or at the end of the turn
    '''
    def __init__(self, coordinates, width, height, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'fabricate evidence', 'none', attached_label.modes, 'buttons/fabricate_evidence_button.png', attached_label, global_manager)

    def get_cost(self):
        '''
        Description:
            Returns the cost of fabricating another piece of evidence. The cost increases for each existing fabricated evidence against the selected minister
        Input:
            None
        Output:
            Returns the cost of fabricating another piece of evidence
        '''
        defense = self.global_manager.get('displayed_defense')
        return(trial_utility.get_fabricated_evidence_cost(defense.fabricated_evidence))

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button spends money to fabricate a piece of evidence against the selected minister
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                if self.global_manager.get('money') >= self.get_cost():
                    self.showing_outline = True
                    self.global_manager.get('money_tracker').change(-1 * self.get_cost(), 'trial fees')
                    defense = self.global_manager.get('displayed_defense')
                    prosecutor = self.global_manager.get('displayed_prosecution')
                    prosecutor.display_message(prosecutor.current_position + " " + prosecutor.name + " reports that evidence has been successfully fabricated for " + str(self.get_cost()) +
                        " money. /n /nEach new fabricated evidence will cost twice as much as the last, and fabricated evidence becomes useless at the end of the turn or after it is used in a trial. /n /n")
                    defense.fabricated_evidence += 1
                    defense.corruption_evidence += 1
                    minister_utility.calibrate_trial_info_display(self.global_manager, self.global_manager.get('defense_info_display_list'), defense) #updates trial display with new evidence
                else:
                    text_tools.print_to_screen("You do not have the " + str(self.get_cost()) + " money needed to fabricate evidence.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not fabricate evidence.", self.global_manager)

class bribe_judge_button(label_button):
    '''
    Button in the trial screen that bribes the judge to get an advantage in the next trial this turn
    '''
    def __init__(self, coordinates, width, height, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'bribe judge', 'none', attached_label.modes, 'buttons/bribe_judge_button.png', attached_label, global_manager)

    def get_cost(self):
        '''
        Description:
            Returns the cost of bribing the judge, which is as much as the first piece of fabricated evidence
        Input:
            None
        Output:
            Returns the cost of bribing the judge
        '''
        return(trial_utility.get_fabricated_evidence_cost(0)) #costs as much as 1st piece of fabricated evidence

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if judge has not been bribed yet, otherwise returns False
        '''
        if super().can_show():
            if not self.global_manager.get('prosecution_bribed_judge'):
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button spends money to bribe the judge
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                if self.global_manager.get('money') >= self.get_cost():
                    if not self.global_manager.get('prosecution_bribed_judge'):
                        self.showing_outline = True
                        self.global_manager.get('money_tracker').change(-1 * self.get_cost(), 'trial fees')
                        self.global_manager.set('prosecution_bribed_judge', True)
                        prosecutor = self.global_manager.get('displayed_prosecution')
                        prosecutor.display_message(prosecutor.current_position + " " + prosecutor.name + " reports that the judge has been successfully bribed for " + str(self.get_cost()) +
                            " money. /n /nThis may provide a bonus in the next trial this turn. /n /n")
                    else:
                        text_tools.print_to_screen("The judge has already been bribed for this trial.", self.global_manager)
                else:
                    text_tools.print_to_screen("You do not have the " + str(self.get_cost()) + " money needed to bribe the judge.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not fabricate evidence.", self.global_manager)  
    
class hire_african_workers_button(label_button):
    '''
    Button that hires available workers from the displayed village/slum
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, hire_source_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by the recruited worker
            label attached_label: Label that this button is attached to
            string hire_source_type: Type of location this button hires workers from, can be 'village' or 'slums'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.hire_source_type = hire_source_type
        if hire_source_type == 'village':
            button_type = 'hire village worker'
        elif hire_source_type == 'slums':
            button_type = 'hire slums worker'
        super().__init__(coordinates, width, height, button_type, keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if a village/slum with available workers is displayed, otherwise returns False
        '''
        if super().can_show():
            if self.hire_source_type == 'village':
                attached_village = self.global_manager.get('displayed_tile').cell.get_building('village')
                if not attached_village == 'none':
                    if attached_village.can_recruit_worker():
                        return(True)
            elif self.hire_source_type == 'slums':
                attached_slums = self.global_manager.get('displayed_tile').cell.contained_buildings['slums']
                if not attached_slums == 'none':
                    return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button hires an available worker from the displayed village/slum
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                self.showing_outline = True
                choice_info_dict = {'recruitment_type': 'African worker ' + self.hire_source_type, 'cost': 0, 'mob_image_id': 'mobs/African worker/default.png', 'type': 'recruitment', 'source_type': self.hire_source_type}
                self.global_manager.get('actor_creation_manager').display_recruitment_choice_notification(choice_info_dict, 'African workers', self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not hire a worker.", self.global_manager)

class buy_slaves_button(label_button):
    '''
    Button that buys slaves from slave traders
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by the recruited worker
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'buy slaves', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the displayed tile is in the slave traders grid, otherwise returns False
        '''
        if super().can_show():
            if not self.global_manager.get('displayed_tile') == 'none':
                if self.global_manager.get('displayed_tile').cell.grid == self.global_manager.get('slave_traders_grid'):
                    return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button buys slaves from slave traders
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                self.showing_outline = True
                self.cost = self.global_manager.get('recruitment_costs')['slave workers']
                if self.global_manager.get('money_tracker').get() >= self.cost:
                    choice_info_dict = {'recruitment_type': 'slave workers', 'cost': self.cost, 'mob_image_id': 'mobs/slave workers/default.png', 'type': 'recruitment'}
                    self.global_manager.get('actor_creation_manager').display_recruitment_choice_notification(choice_info_dict, 'slave workers', self.global_manager)
                else:
                    text_tools.print_to_screen('You do not have enough money to buy slaves.', self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not buy slaves.", self.global_manager)

class automatic_route_button(label_button):
    '''
    Button that modifies a unit's automatic movement route, with an effect depending on the button's type
    '''
    def __init__(self, coordinates, width, height, button_type, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string button_type: Determines the function of this button, like 'end turn'
            pygame key object keybind_id: Determines the keybind id that activates this button, like pygame.K_n
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, button_type, keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn. All automatic route buttons can only appear if the selected unit is porters or a crewed vehicle. Additionally, clear and follow automatic route buttons require that an automatic
                route already exists
        Input:
            None
        Output:
            boolean: Returns whether this button should be drawn
        '''
        if super().can_show():
            attached_mob = self.global_manager.get('displayed_mob')
            if attached_mob.inventory_capacity > 0 and (not (attached_mob.is_group and attached_mob.can_trade)) and (not (attached_mob.is_vehicle and attached_mob.crew == 'none')):
                if self.button_type in ['clear automatic route', 'follow automatic route']:
                    if len(attached_mob.base_automatic_route) > 0:
                        return(True)
                else:
                    return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. Clear automatic route buttons remove the selected unit's automatic route. Draw automatic route buttons enter the route
            drawing mode, in which the player can click on consecutive tiles to add them to the route. Follow automatic route buttons command the selected unit to execute its in-progress automatic route, stopping when it can not
            continue the route for any reason
        Input:
            None
        Output:
            None
        '''
        attached_mob = self.global_manager.get('displayed_mob')
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager):
                if self.global_manager.get('strategic_map_grid') in attached_mob.grids:
                    self.showing_outline = True
                    if self.button_type == 'clear automatic route':
                        attached_mob.clear_automatic_route()
                        
                    elif self.button_type == 'draw automatic route':
                        if attached_mob.is_vehicle and attached_mob.vehicle_type == 'train' and not attached_mob.images[0].current_cell.has_intact_building('train_station'):
                            text_tools.print_to_screen("A train can only start a movement route from a train station.", self.global_manager)
                            return()
                        attached_mob.clear_automatic_route()
                        attached_mob.add_to_automatic_route((attached_mob.x, attached_mob.y))
                        self.global_manager.set('drawing_automatic_route', True)
                        
                    elif self.button_type == 'follow automatic route':
                        if attached_mob.can_follow_automatic_route():
                            attached_mob.follow_automatic_route()
                        else:
                            text_tools.print_to_screen("This unit is currently not able to progress along its designated route.", self.global_manager)
                else:
                    text_tools.print_to_screen("You can only create movement routes in Africa.", self.global_manager)
            else:
                if self.button_type == 'follow automatic route':
                    text_tools.print_to_screen("You are busy and can not move this unit.", self.global_manager)
                else:
                    text_tools.print_to_screen("You are busy and can not modify this unit's movement route.", self.global_manager)
