#Contains functions that randomly generate village names

import random

def create_village_name():
    '''
    Description:
        Returns a randomly generated village name
    Input:
        None
    Output:
        string: Randomly generated village name
    '''
    l = random.randrange(1, 4) + 1 + random.randrange(1, 4) + 1
    vname = ''
    ch = random.randrange(1, 6) + 1
    if ch < 6:
        lm = 1
    elif ch == 6:
        lm = -1
    if lm == 1:
        vname = add_consonant(vname)
    elif lm == -1:
        vname = add_vowel(vname)
    for i in range(0, l):#lowercase L, not 1
        ch = random.randrange(1, 19) + 1
        if ch < 15:
            lm = lm * -1
        elif ch == 19:
            vname = add_space(vname)
        if lm == 1:
            vname = add_consonant(vname)
        elif lm == -1:
            vname = add_vowel(vname)
    final_vname = ''
    for letter_index in range(0, len(vname)):
        if not vname[letter_index] == 'space' and not letter_index == 0 and not vname[letter_index - 1] == ' ':
            current_letter = vname[letter_index].lower()
        else:
            current_letter = vname[letter_index]
        final_vname = final_vname + current_letter
    return(final_vname)

def add_space(base):
    '''
    Description:
        Returns a version of the inputted string with a space added to it
    Input:
        string base: string to add a space to
    Output:
        string: Version of the inputted string with a space added to it
    '''
    return(base + ' ')

def add_vowel(base):
    '''
    Description:
        Returns a version of the inputted string with a random vowel added to it, with the vowel being chosen from a weighted list
    Input:
        string base: string to add a vowel to
    Output:
        string: Version of the inputted string with a random vowel added to it
    '''
    weighted_vowels = ['A', 'A', 'A', 'A', 'A', 'E', 'E', 'I', 'I', 'O', 'O', 'O', 'U', 'U']
    return(base + random.choice(weighted_vowels))

def add_consonant(base):
    '''
    Description:
        Returns a version of the inputted string with a random consonant added to it, with the consonant being chosen from a weighted list
    Input:
        string base: string to add a consonant to
    Output:
        string: Version of the inputted string with a random consonant added to it
    '''
    weighted_consonants = ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'N', 'N', 'N', 'N', 'N', 'N', 'P', 'Q', 'R', 'S', 'S', 'S', 'T', 'T', 'T', 'V', 'W', 'X', 'Y', 'Z']
    return(base + random.choice(weighted_consonants))
