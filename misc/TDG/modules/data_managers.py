#Contains functionality for objects that manage notifications, variables, files, etc.
from . import terrains

class global_manager_template():
    '''
    Object designed to manage a dictionary of shared variables and be passed between functions and objects as a simpler alternative to passing each variable or object separately
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
        self.global_dict = {}
        
    def get(self, name):
        '''
        Description:
            Returns the value in this object's dictionary corresponding to the inputted key
        Input:
            string name: Name of a key in this object's dictionary
        Output:
            any type: The value corresponding to the inputted key's entry in this object's dictionary
        '''
        return(self.global_dict[name])
    
    def set(self, name, value):
        '''
        Description:
            Sets or initializes the inputted value for the inputted key in this object's dictionary
        Input:
            string name: Name of the key in this object's dictionary to initialize/modify
            any type value: Value corresponding to the new/modified key
        Output:
            None
        '''
        self.global_dict[name] = value

class actor_creation_manager_template():
    def create(self, input_dict, global_manager):
        init_type = input_dict['init_type']
        if init_type == 'terrain':
            new_actor = terrains.terrain(input_dict, global_manager)
        elif init_type == 'point':
            new_actor = terrains.point(input_dict, global_manager)
        return(new_actor)
    