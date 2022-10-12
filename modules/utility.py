#Contains miscellaneous functions, like removing an item from a list or finding the distance between 2 points

def find_object_distance(first, second):
    '''
    Description:
        Returns the distance between the positions of the inputted objects. Functions correctly regardless of whether the x and y coordinate attributes are pixel coordinates or grid coordinates
    Input:
        object first: Object with x and y coordinate attributes
        object second: Object with x and y coordinate attributes
    Output:
        double: Returns the distance between the positions of the inputted objects
    '''
    return((((first.x - second.x) ** 2) + ((first.y - second.y) ** 2)) ** 0.5)

def find_coordinate_distance(first, second):
    '''
    Description:
        Returns the distance between the positions of the inputted coordinates. Functions correctly regardless of whether the x and y coordinates are pixel coordinates or grid coordinates
    Input:
        int tuple first: Two values representing x and y coordinates
        int tuple second: Two values representing x and y coordinates
    Output:
        double: Returns the distance between the positions of the inputted coordinates
    '''
    first_x, first_y = first
    second_x, second_y = second
    return((((first_x - second_x) ** 2) + ((first_y - second_y) ** 2)) ** 0.5)

def find_grid_distance(first, second):
    '''
    Description:
        Returns the sum of the horizontal and vertical distances between the positions of the inputted objects. Works for calculating movement distance on a grid. Returns -1 for objects on different grids
    Input:
        object first: Object with x and y coordinate attributes
        object second: Object with x and y coordinate attributes
    Output:
        int: Returns the sum of the horizontal and vertical distance between the positions of the inputted objects
    '''
    horizontal_distance = abs(first.x - second.x)
    vertical_distance = abs(first.y - second.y)
    if not first.grids[0] in second.grids:
        return(-1)
    return(horizontal_distance + vertical_distance)
    
def remove_from_list(received_list, item_to_remove):
    '''
    Description:
        Returns a version of the inputted list with all instances of the inputted item removed
    Input:
        any type list received list: list to remove items from
        any type item_to_remove: Item to remove from the list
    Output:
        any type list: Returns a version of the inputted list with all instances of the inputted item removed
    '''
    output_list = []
    for item in received_list:
        if not item == item_to_remove:
            output_list.append(item)
    return(output_list)

def copy_list(received_list): #allows setting to new list by copying data instead of just pointer
    '''
    Description:
        Returns a copy of the inputted list, allowing passing by value rather than reference
    Input:
        list received_list: list to Copy
    Output:
        list: Returns a copy of the inputted list
    '''
    return_list = []
    for item in received_list:
        return_list.append(item)
    return(return_list)
        
def toggle(variable):
    '''
    Description:
        Returns the opposite of the inputted boolean
    Input:
        boolean variable: boolean whose opposite value will be returned
    Output:
        boolean: Returns True if the inputted boolean is False, otherwise returns False
    '''
    if variable == True:
        return(False)
    elif variable == False:
        return(True)

def generate_article(word):
    '''
    Description:
        Returns 'an' if the inputted word starts with a vowel or 'a' if the inputted word does not start with a vowel. In certain exception cases, the correct article will be returned regardless of the first letter. Used to correctly
            describe a word
    Input:
        string word: Word to generate an article for
    Output:
        string: Returns 'an' if the inputed word starts with a vowel, otherwise returns 'a'
    '''
    vowels = ['a', 'e', 'i', 'o', 'u']
    plural_exceptions = []
    a_an_exceptions = ['European', 'unit']
    if word[-1] == 's' and (not word in plural_exceptions):
        return('')
    elif word[0] in vowels and (not word in a_an_exceptions):
        return('an')
    else:
        return('a')

def generate_plural(amount):
    '''
    Description:
        Returns an empty string if the inputted amount is equal to 1. Otherwise returns 's'. Allows the correct words to be used when describing a variable's value
    Input:
        int amount: It is determined whether this value is plural or not
    Output:
        string: Returns an empty string if the inputted amount is equal to 1, otherwise returns 's'
    '''
    if amount == 1:
        return('')
    else:
        return('s')

def generate_capitalized_article(word):
    '''
    Description:
        Returns 'An' if the inputted word starts with a vowel or 'A' if the inputted word does not start with a vowel. In certain exception cases, the correct article will be returned regardless of the first letter. Used to correctly
            describe a word at the beginning of a sentence
    Input:
        string word: Word to generate an article for
    Output:
        string: Returns 'An' if the inputed word starts with a vowel, otherwise returns 'A'
    '''
    vowels = ['a', 'e', 'i', 'o', 'u']
    plural_exceptions = []
    a_an_exceptions = ['European', 'unit']
    if word[-1] == 's' and (not word in plural_exceptions):
        return(' ')
    elif word[0] in vowels and (not word in a_an_exceptions):
        return('An ')
    else:
        return('A ')
    
def add_to_message(message, new):
    '''
    Description:
        Returns a concatenated version of the inputted strings, with the second string appearing after the first one in the concatenated version
    Input:
        string message: string to be concatenated with the other string
        string new: string to be concatenated with the other string
    Output:
        string: Returns a concatenated version of the inputted strings
    '''
    return (message + new)

def conjugate(infinitive, amount, tense = 'present'):
    '''
    Description:
        Returns a singular or plural conjugated version of the inputted verb
    Input:
        string infinitive: base word to conjugate, like "be" or "attack"
        int amount: quantity of subject, determining if singular or plural verb should be used
        string tense = 'present': tense of verb, determining version of verb, like 'was' or 'is', to use
    Output:
        string: Returns conjugated word with the correct number, like "is" or "attacks"
    '''
    if infinitive == 'be':
        if tense == 'present':
            if amount == 1:
                return('is')
            else:
                return('are')
        elif tense == 'preterite':
            if amount == 1:
                return('was')
            else:
                return('were')
    else:
        if amount == 1:
            return(infinitive + 's')
        else:
            return(infinitive)
    return('none')

def capitalize(string):
    '''
    Description:
        Capitalizes the first letter of the inputted string and returns the resulting string. Unlike python's default capitalize method, does not make the rest of the string lowercase
    Input:
        string string: string that is being capitalized
    Output:
        string: Returns capitalized string
    '''
    if len(string) > 1:
        return(string[:1].capitalize() + string[1:])
    else:
        return(string[:1].capitalize())
