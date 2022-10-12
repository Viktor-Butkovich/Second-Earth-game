#Contains functionality for buttons relating to the European headquarters screen
import random


from .buttons import button
from . import game_transitions
from . import main_loop_tools
from . import notification_tools
from . import text_tools
from . import market_tools
from . import utility
from . import actor_utility

class recruitment_button(button):
    '''
    Button that creates a new unit with a type depending on recruitment_type and places it in Europe
    '''
    def __init__(self, coordinates, width, height, color, recruitment_type, keybind_id, modes, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string color: Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
            string recruitment_type: Type of unit recruited by this button, like 'explorer'
            pygame key object keybind_id: Determines the keybind id that activates this button, like pygame.K_n
            string list modes: Game modes during which this button can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        if recruitment_type in global_manager.get('recruitment_types'):
            image_id = 'mobs/' + recruitment_type + '/button.png'
            self.mob_image_id = 'mobs/' + recruitment_type + '/default.png'
        else:
            image_id = 'misc/default_button.png'
            self.mob_image_id = 'mobs/default/default.png'
        self.recruitment_type = recruitment_type
        self.recruitment_name = ''
        for character in self.recruitment_type:
            if not character == '_':
                self.recruitment_name += character
            else:
                self.recruitment_name += ' '
        self.cost = global_manager.get('recruitment_costs')[self.recruitment_type]
        super().__init__(coordinates, width, height, color, 'recruitment', keybind_id, modes, image_id, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button creates a new unit with a type depending on recruitment_type and places it in Europe
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                if self.global_manager.get('money_tracker').get() >= self.cost:
                    choice_info_dict = {'recruitment_type': self.recruitment_type, 'cost': self.cost, 'mob_image_id': self.mob_image_id, 'type': 'recruitment'}
                    self.global_manager.get('actor_creation_manager').display_recruitment_choice_notification(choice_info_dict, self.recruitment_name, self.global_manager)
                else:
                    text_tools.print_to_screen('You do not have enough money to recruit this unit', self.global_manager)
            else:
                text_tools.print_to_screen('You are busy and can not recruit a unit', self.global_manager)

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type. This type of button has a tooltip describing the type of unit it recruits
        Input:
            None
        Output:
            None
        '''
        actor_utility.update_recruitment_descriptions(self.global_manager, self.recruitment_type)
        if self.recruitment_type == 'European workers':
            self.set_tooltip(['Recruits a unit of ' + self.recruitment_name + ' for ' + str(self.cost) + ' money.'] + self.global_manager.get('recruitment_list_descriptions')[self.recruitment_type])
        else:
            self.set_tooltip(['Recruits ' + utility.generate_article(self.recruitment_type) + ' ' + self.recruitment_name + ' for ' + str(self.cost) + ' money.'] + self.global_manager.get('recruitment_list_descriptions')[self.recruitment_type])

class buy_commodity_button(button):
    '''
    Button that buys a unit of commodity_type when clicked and has an image matching that of its commodity
    '''
    def __init__(self, coordinates, width, height, color, commodity_type, modes, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string color: Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
            string commodity_type: Type of commmodity that this button buys, like 'consumer goods'
            string list modes: Game modes during which this button can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        possible_commodity_types = global_manager.get('commodity_types')
        if commodity_type in possible_commodity_types:
            image_id = 'scenery/resources/buttons/' + commodity_type + '.png'
        else:
            image_id = 'misc/default_button.png'
        self.commodity_type = commodity_type
        self.cost = global_manager.get('commodity_prices')[self.commodity_type] #update this when price changes
        global_manager.set(commodity_type + ' buy button', self) #consumer goods buy button, used to update prices
        super().__init__(coordinates, width, height, color, 'recruitment', 'none', modes, image_id, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button buys a unit of the commodity_type commodity
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                self.cost = self.global_manager.get('commodity_prices')[self.commodity_type]
                if self.global_manager.get('money_tracker').get() >= self.cost:
                    if main_loop_tools.check_if_minister_appointed(self.global_manager.get('type_minister_dict')['trade'], self.global_manager): #requires trade minister
                        self.global_manager.get('europe_grid').cell_list[0].tile.change_inventory(self.commodity_type, 1) #adds 1 of commodity type to
                        self.global_manager.get('money_tracker').change(-1 * self.cost, 'consumer goods')
                        text_tools.print_to_screen("You have lost " + str(self.cost) + " money from buying 1 unit of consumer goods.", self.global_manager)
                        if random.randrange(1, 7) == 1: #1/6 chance
                            market_tools.change_price('consumer goods', 1, self.global_manager)
                            text_tools.print_to_screen("The price of consumer goods has increased from " + str(self.cost) + " to " + str(self.cost + 1) + ".", self.global_manager)
                else:
                    text_tools.print_to_screen('You do not have enough money to purchase this commodity', self.global_manager)
            else:
                text_tools.print_to_screen('You are busy and can not purchase commodities', self.global_manager)

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type. This type of button has a tooltip describing the commodity that it buys and its price
        Input:
            None
        Output:
            None
        '''
        self.cost = self.global_manager.get('commodity_prices')[self.commodity_type]
        self.set_tooltip(['Purchases 1 unit of ' + self.commodity_type + ' for ' + str(self.cost) + ' money.'])
        
