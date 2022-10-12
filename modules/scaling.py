#Contains functions that scale coordinates and lengths/widths to different resolutions

def scale_coordinates(x, y, global_manager):
    '''
    Description:
        Returns a version of the inputted coordinates scaled to the player's screen resolution. For example, if the inputted coordinates are at the center of the program's default screen, the returned coordinates will be in the center
            of the player's screen
    Input:
        int x: Unscaled pixel x coordinate
        int y: Unscaled pixel y coordinate
    Output:
        int: Scaled pixel x coordinate
        int: Scaled pixel y coordinate
    '''
    x_ratio = global_manager.get('display_width')/global_manager.get('default_display_width')
    y_ratio = global_manager.get('display_height')/global_manager.get('default_display_height')
    scaled_x = round(x * x_ratio)
    scaled_y = round(y * y_ratio)
    return(scaled_x, scaled_y)

def scale_width(width, global_manager):
    '''
    Description:
        Returns a version of the inputted width scaled to the player's screen resolution. For example, if the inputted width is as wide as the program's default screen, the returned width will be as wide as the player's screen
    Input:
        int width: Unscaled pixel width
    Output:
        int: Scaled pixel width
    '''
    ratio = global_manager.get('display_width')/global_manager.get('default_display_width')
    scaled_width = round(width * ratio)
    return(scaled_width)

def scale_height(height, global_manager):
    '''
    Description:
        Returns a version of the inputted height scaled to the player's screen resolution. For example, if the inputted height is as tall as the program's default screen, the returned height will be as tall as the player's screen
    Input:
        int height: Unscaled pixel height
    Output:
        int: Scaled pixel height
    '''
    ratio = global_manager.get('display_height')/global_manager.get('default_display_height')
    scaled_height = round(height * ratio)
    return(scaled_height)

def unscale_width(width, global_manager):
    '''
    Description:
        Returns a version of the inputted width scaled to the program's default screen resolution. For example, if the inputted width is as wide as the player's screen, the returned width will be as wide as the program's default screen
    Input:
        int width: Scaled pixel width
    Output:
        int: Unscaled pixel width
    '''
    ratio = global_manager.get('display_width')/global_manager.get('default_display_width')
    unscaled_width = round(width / ratio)
    return(unscaled_width)

def unscale_height(height, global_manager):
    '''
    Description:
        Returns a version of the inputted height scaled to the program's default screen resolution. For example, if the inputted height is as tall as the player's screen, the returned height will be as tall as the program's default
            screen
    Input:
        int height: Scaled pixel height
    Output:
        int: Unscaled pixel height
    '''
    ratio = global_manager.get('display_height')/global_manager.get('default_display_height')
    unscaled_height = round(height / ratio)
    return(unscaled_height)

