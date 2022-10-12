#Contains functionality for actor display images

from ..images import free_image
from ..images import warning_image

class actor_display_free_image(free_image):
    '''
    Free image that changes its appearance to match selected mobs or tiles
    '''
    def __init__(self, coordinates, width, height, modes, actor_image_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            string actor_image_type: Type of actor whose appearance will be copied by this image
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.actor_image_type = actor_image_type
        self.actor = 'none'
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)

    def calibrate(self, new_actor):
        '''
        Description:
            Sets this image to match the inputted object's appearance to show in the actor info display
        Input:
            string/actor new_actor: If this equals 'none', hides this image. Otherwise, causes this image will match this input's appearance
        Output:
            None
        '''
        self.actor = new_actor
        if not new_actor == 'none':
            if self.actor_image_type == 'resource':
                if new_actor.cell.visible:
                    if not new_actor.resource_icon == 'none':
                        self.set_image(new_actor.resource_icon.image_dict['default'])
                    else: #show nothing if no resource
                        self.set_image('misc/empty.png')
                else: #show nothing if cell not visible
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'terrain' and not new_actor.cell.visible:
                self.set_image(new_actor.image_dict['hidden'])
            elif self.actor_image_type == 'resource_building':
                if new_actor.cell.has_building('resource'):
                    self.set_image(new_actor.cell.get_building('resource').image_dict['default']) #matches resource building
                else:
                    self.set_image('misc/empty.png')
            elif self.actor_image_type in ['port', 'train_station', 'trading_post', 'mission', 'slums', 'fort']:
                if new_actor.cell.has_building(self.actor_image_type):
                    self.set_image(new_actor.cell.get_building(self.actor_image_type).images[0].image_id)
                    #self.set_image('buildings/' + self.actor_image_type + '.png')
                else:
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'infrastructure_middle':
                contained_infrastructure = new_actor.cell.get_building('infrastructure')
                if not contained_infrastructure == 'none':
                    self.set_image(contained_infrastructure.image_dict['default'])
                else:
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'infrastructure_connection':
                contained_infrastructure = new_actor.cell.get_building('infrastructure')
                if not contained_infrastructure == 'none':
                    if contained_infrastructure.infrastructure_connection_images[self.direction].can_show():
                        self.set_image(contained_infrastructure.infrastructure_connection_images[self.direction].image_id)
                    else:
                        self.set_image('misc/empty.png')
                else:
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'veteran_icon':
                if (self.actor.is_officer or self.actor.is_group) and self.actor.veteran:
                    self.set_image('misc/veteran_icon.png')
                else:
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'disorganized_icon':
                if self.actor.disorganized:
                    self.set_image('misc/disorganized_icon.png')
                else:
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'sentry_icon':
                if self.actor.is_pmob and self.actor.sentry_mode:
                    self.set_image('misc/sentry_icon.png')
                else:
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'minister_default':
                self.set_image(new_actor.image_id)
            else:
                self.set_image(new_actor.image_dict['default'])
        else:
            self.set_image('misc/empty.png')

    def can_show(self):
        '''
        Description:
            Returns whether this image should be drawn
        Input:
            None
        Output:
            boolean: False if there is no actor in the info display, otherwise returns same value as superclass
        '''
        if self.actor == 'none':
            return(False)
        else:
            return(super().can_show())

class actor_display_infrastructure_connection_image(actor_display_free_image):
    '''
    Image appearing on tile info display to show the road/railroad connections of the displayed tile
    '''
    def __init__(self, coordinates, width, height, modes, actor_image_type, direction, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            string actor_image_type: Type of actor whose appearance will be copied by this image
            string direction: 'up', 'down', 'left', or 'right', side of tile that this image points to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.direction = direction
        super().__init__(coordinates, width, height, modes, actor_image_type, global_manager)

class mob_background_image(free_image):
    '''
    Image appearing behind the displayed actor in the actor info display
    '''
    def __init__(self, image_id, coordinates, width, height, modes, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string image_id: File path to the image used by this object
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(image_id, coordinates, width, height, modes, global_manager)
        self.actor = 'none'

    def calibrate(self, new_actor):
        '''
        Description:
            Updates which actor is in front of this image
        Input:
            string/actor new_actor: The displayed actor that goes in front of this image. If this equals 'none', there is no actor in front of it
        Output:
            None
        '''
        self.actor = new_actor

    def can_show(self):
        '''
        Description:
            Returns whether this image should be drawn
        Input:
            None
        Output:
            boolean: False if there is no actor in the info display, otherwise returns same value as superclass
        '''
        if self.actor == 'none':
            return(False)
        if self.image_id == 'misc/pmob_background.png' and not self.actor.is_pmob:
            return(False)
        if self.image_id == 'misc/npmob_background.png' and not self.actor.is_npmob:
            return(False)
        else:
            return(super().can_show())

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to that of the actor in front of it
        Input:
            None
        Output:
            None
        '''
        if not self.actor == 'none':
            tooltip_text = self.actor.tooltip_text
            self.set_tooltip(tooltip_text)
        else:
            super().update_tooltip()

class minister_background_image(mob_background_image):
    '''
    Image that appears behind a minister and changes to match their current office
    '''
    def __init__(self, image_id, coordinates, width, height, modes, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string image_id: File path to the image used by this object
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(image_id, coordinates, width, height, modes, global_manager)
        self.warning_image = warning_image(self, global_manager)
        self.warning_image.x += self.width * 0.75

    def can_show_warning(self):
        '''
        Description:
            Returns whether this image should display its warning image. It should be shown when this image is visible and its attached minister is about to be fired at the end of the turn
        Input:
            None
        Output:
            Returns whether this image should display its warning image
        '''
        if not self.actor == 'none':
            if self.actor.just_removed and self.actor.current_position == 'none':
                return(True)
        return(False)
        
    def calibrate(self, new_minister):
        '''
        Description:
            Updates which minister is in front of this image and changes its appearance to match the minister's current office
        Input:
            string/minister new_minister: The displayed minister that goes in front of this image. If this equals 'none', there is no minister in front of it
        Output:
            None
        '''
        super().calibrate(new_minister)
        if not new_minister == 'none':
            if new_minister.current_position == 'none':
                self.set_image('misc/mob_background.png')
            else:
                self.set_image('ministers/icons/' + self.global_manager.get('minister_type_dict')[new_minister.current_position] + '.png')

class label_image(free_image):
    '''
    Free image that is attached to a label and will only show when the label is showing
    '''
    def __init__(self, coordinates, width, height, modes, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            label attached_label: The label that this image is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.attached_label = attached_label
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this image should be drawn
        Input:
            None
        Output:
            boolean: False if this image's label is not showing, otherwise returns same value as superclass
        '''
        if self.attached_label.can_show():
            return(super().can_show())
        else:
            return(False)
