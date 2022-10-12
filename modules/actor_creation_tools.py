#Contains functionality for creating new instances of mobs, buildings, dice, and ministers

import random
from . import mobs
from .mob_types import workers
from .mob_types import officers
from .mob_types import caravans
from .mob_types import construction_gangs
from .mob_types import expeditions
from .mob_types import missionaries
from .mob_types import porters
from .mob_types import work_crews
from .mob_types import vehicles
from .mob_types import battalions
from .mob_types import native_warriors
from .mob_types import beasts
from . import buildings
from . import ministers
from . import notification_tools
from . import utility
from . import actor_utility
from . import market_tools
from . import dice

class actor_creation_manager_template(): #can get instance from anywhere and create actors with it without importing respective actor module
    '''
    Object that creates new mobs and buildings based on inputted values
    '''
    def __init__(self):
        '''
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        '''
        nothing = 0
        
    def create(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes a mob, building, or loan based on inputted values
        Input:
            boolean from_save: True if the object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize the object, with contents varying based on the type of object
                'init_type': string value - Always required, determines type of object created
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            actor: Returns the mob or building that was created
        '''
        init_type = input_dict['init_type']
        #mobs
        if init_type == 'mob':
            new_actor = mobs.mob(from_save, input_dict, global_manager)
        elif init_type == 'workers':
            new_actor = workers.worker(from_save, input_dict, global_manager)
        elif init_type == 'slaves':
            new_actor = workers.slave_worker(from_save, input_dict, global_manager)
        elif init_type == 'church_volunteers':
            new_actor = workers.church_volunteers(from_save, input_dict, global_manager)
        elif init_type == 'train':
            new_actor = vehicles.train(from_save, input_dict, global_manager)
        elif init_type == 'ship':
            new_actor = vehicles.ship(from_save, input_dict, global_manager)
        elif init_type == 'boat':
            new_actor = vehicles.boat(from_save, input_dict, global_manager)
        elif init_type in global_manager.get('officer_types'):
            if init_type == 'evangelist':
                new_actor = officers.evangelist(from_save, input_dict, global_manager)
            elif init_type == 'merchant':
                new_actor = officers.merchant(from_save, input_dict, global_manager)
            else:
                new_actor = officers.officer(from_save, input_dict, global_manager)
        elif init_type == 'native_warriors':
            new_actor = native_warriors.native_warriors(from_save, input_dict, global_manager)
        elif init_type == 'beast':
            new_actor = beasts.beast(from_save, input_dict, global_manager)
                
        #groups
        elif init_type == 'porters':
            new_actor = porters.porters(from_save, input_dict, global_manager)
        elif init_type == 'work_crew':
            new_actor = work_crews.work_crew(from_save, input_dict, global_manager)
        elif init_type == 'construction_gang':
            new_actor = construction_gangs.construction_gang(from_save, input_dict, global_manager)
        elif init_type == 'caravan':
            new_actor = caravans.caravan(from_save, input_dict, global_manager)
        elif init_type == 'missionaries':
            new_actor = missionaries.missionaries(from_save, input_dict, global_manager)
        elif init_type == 'expedition':
            new_actor = expeditions.expedition(from_save, input_dict, global_manager)
        elif init_type == 'battalion':
            new_actor = battalions.battalion(from_save, input_dict, global_manager)
        elif init_type == 'safari':
            new_actor = battalions.safari(from_save, input_dict, global_manager)

        #buildings
        elif init_type == 'infrastructure':
            new_actor = buildings.infrastructure_building(from_save, input_dict, global_manager)
        elif init_type == 'trading_post':
            new_actor = buildings.trading_post(from_save, input_dict, global_manager)
        elif init_type == 'mission':
            new_actor = buildings.mission(from_save, input_dict, global_manager)
        elif init_type == 'fort':
            new_actor = buildings.fort(from_save, input_dict, global_manager)
        elif init_type == 'train_station':
            new_actor = buildings.train_station(from_save, input_dict, global_manager)
        elif init_type == 'port':
            new_actor = buildings.port(from_save, input_dict, global_manager)
        elif init_type == 'warehouses':
            new_actor = buildings.warehouses(from_save, input_dict, global_manager)
        elif init_type == 'resource':
            new_actor = buildings.resource_building(from_save, input_dict, global_manager)
        elif init_type == 'slums':
            new_actor = buildings.slums(from_save, input_dict, global_manager)

        #loans
        elif init_type == 'loan':
            new_actor = market_tools.loan(from_save, input_dict, global_manager)
            
        return(new_actor)

    def display_recruitment_choice_notification(self, choice_info_dict, recruitment_name, global_manager):
        '''
        Description:
            Displays a choice notification to verify the recruitment of a unit
        Input:
            dictionary choice_info_dict: dictionary containing various information needed for the choice notification
                'recruitment_type': string value - Type of unit to recruit, like 'European worker'
                'cost': double value - Recruitment cost of the unit
                'mob_image_id': string value - File path to the image used by the recruited unit
                'type': string value - Type of choice notification to display, always 'recruitment' for recruitment notificatoins
                'source_type': string value - Only used when recruiting African workers, tracks whether workers came from available village workers, slums, or a labor broker
            string recruitment_name: Name used in the notification to signify the unit, like 'explorer'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        recruitment_type = recruitment_name
        if recruitment_name in ['slave workers', 'steamship']:
            verb = 'purchase'
        elif recruitment_name in ['African workers', 'European workers']:
            verb = 'hire'
            if recruitment_name == 'African workers':
                recruitment_type = choice_info_dict['source_type'] + ' workers' #slums workers or village workers
        else:
            verb = 'recruit'
        if recruitment_name == 'African workers' and choice_info_dict['source_type'] == 'labor broker':
            message = 'Are you sure you want to pay a labor broker ' + str(choice_info_dict['cost']) + ' money to hire a unit of African workers from a nearby village? /n /n' 
        elif recruitment_name in ['slave workers', 'African workers', 'European workers']:
            message = 'Are you sure you want to ' + verb + ' a unit of ' + recruitment_name + ' for ' + str(choice_info_dict['cost']) + ' money? /n /n'
        else:
            message = 'Are you sure you want to ' + verb + ' ' + utility.generate_article(recruitment_name) + ' ' + recruitment_name + ' for ' + str(choice_info_dict['cost']) + ' money? /n /n'
        actor_utility.update_recruitment_descriptions(global_manager, recruitment_type)
        message += global_manager.get('recruitment_string_descriptions')[recruitment_type]
        
        notification_tools.display_choice_notification(message, ['recruitment', 'none'], choice_info_dict, global_manager) #message, choices, choice_info_dict, global_manager

    def create_group(self, worker, officer, global_manager): #use when merging groups. At beginning of game, instead of using this, create a group which creates its worker and officer and merges them
        '''
        Description:
            Creates a group out of the inputted worker and officer. Once the group is created, it's component officer and worker will not be able to be directly seen or interacted with until the group is disbanded
                independently until the group is disbanded
        Input:
            worker worker: worker to create a group out of
            officer officer: officer to create a group out of
        Output:
            None
        '''
        input_dict = {}
        input_dict['coordinates'] = (officer.x, officer.y)
        input_dict['grids'] = officer.grids
        input_dict['worker'] = worker
        input_dict['officer'] = officer
        input_dict['modes'] = input_dict['grids'][0].modes #if created in Africa grid, should be ['strategic']. If created in Europe, should be ['strategic', 'europe']
        input_dict['init_type'] = global_manager.get('officer_group_type_dict')[officer.officer_type]
        input_dict['image'] = 'mobs/' + officer.officer_type + '/' + input_dict['init_type'] + '_' + worker.worker_type + '.png' #mobs/merchant/caravan.png
        if input_dict['init_type'] in ['safari', 'expedition']:
            input_dict['canoes_image'] = 'mobs/' + officer.officer_type + '/canoe_' + worker.worker_type + '.png'
        if not officer.officer_type == 'major':
            name = ''
            for character in input_dict['init_type']:
                if not character == '_':
                    name += character
                else:
                    name += ' '
        else: #battalions have special naming convention based on worker type
            if worker.worker_type == 'European':
                name = 'imperial battalion'
            else:
                name = 'colonial battalion'
        input_dict['name'] = name
        return(self.create(False, input_dict, global_manager))

    def create_placeholder_ministers(self, global_manager):
        '''
        Description:
            Creates a set number of unappointed ministers at the start of the game
        Input:
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        for i in range(0, global_manager.get('minister_limit') - 2 + random.randrange(-2, 3)):
            self.create_minister(global_manager)

    def create_minister(self, global_manager):
        '''
        Description:
            Creates a minister with a randomized face, name, skills, and corruption threshold
        Input:
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        new_minister = ministers.minister(False, {}, global_manager)

    def load_minister(self, input_dict, global_manager):
        '''
        Description:
            Initializes a minister based on the inputted values
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'name': string value - The minister's name
                'current_position': string value - Office that the minister is currently occupying, or 'none' if no office occupied
                'general_skill': int value - Value from 1 to 3 that changes what is added to or subtracted from dice rolls
                'specific_skills': dictionary value - String keys corresponding to int values to record skill values for each minister office
                'corruption': int value - Measure of how corrupt a minister is, with 6 having a 1/2 chance to steal, 5 having 1/3 chance, etc.
                'image_id': string value - File path to the image used by the minister
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        new_minister = ministers.minister(True, input_dict, global_manager)

    def display_die(self, coordinates, width, height, modes, num_sides, result_outcome_dict, outcome_color_dict, final_result, global_manager):
        '''
        Description:
            Initializes a die object through the global manager-accessible actor_creation_manager, removing the need to import the die module and create circular imports 
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this die
            int width: Pixel width of this die
            int height: Pixel height of this die
            string list modes: Game modes during which this button can appear
            int num_sides: Number of sides for this die
            string/int dictionary result_outcome_dict: dictionary of string result type keys and int die result values determining which die results are successes/failures or critical successes/failures
            string/int outcome_color_dict: dictionary of string color name keys and int die result values determining what colors are shown for certain die results
            int final_result: Predetermined final result of this roll that the die will end on
            global_manager_template global_manager: Object that accesses shared variables
        Ouptut:
            None
        '''
        dice.die(coordinates, width, height, modes, num_sides, result_outcome_dict, outcome_color_dict, final_result, global_manager)
    
