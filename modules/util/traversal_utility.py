# Contains functions to manage interface collection traversal, doing particular actions for each element with simple decision-making

import modules.constants.status as status


def draw_interface_elements(interface_elements):
    """
    Description:
        Recursively traverses through each of the inputted interface elements and their member trees, updating each element's showing attribute to its current can_show()
            value and, if it showing, drawing it - if an element is not showing, elements below it can not show either
    Input:
        interface_element list interface_elements: List of interface elements to traverse through - no element in the list should be a member of any other element in the
            list, either directly or indirectly. This will preferably be the list of all 'root' elements
    """
    for current_interface_element in interface_elements:
        collection_traversal(
            current_interface_element,
            pretraversal_action=set_showing,
            alternative_action=set_not_showing,
            condition=check_showing,
            posttraversal_action=update_collection,
        )
    for current_interface_element in status.draw_list:
        current_interface_element.draw()
    status.draw_list = []


def collection_traversal(current_element, **kwargs):
    """
    Description:
        Recursively traverses through an interface element/collection, any of its members, any of their members, and so on, doing a particular action for each member based
            on whether the condition is true for that member
    Input:
        interface_element current_element: Element being traversed through
        dictionary kwargs: All keyword arguments expected to be present besides posttraversal action - increases readability of function calls
            function pretraversal_action(interface_element)=None: Called before traversing through a particular element's members
            function alternative_action(interface_element)=None: Given as pretraversal action for lower recursive calls if condition was false for a collection
            function condition(interface_element)=None: Checked before traversing through a particular element's members - determines whether that element will continue
                having a choice between 2 actions or automatically choose the alternative action each time
            function posttraversal_action(interface_element)=None: Called after traversing through a particular element's members, if present
    Output:
        None
    """
    pretraversal_action = kwargs.get("pretraversal_action")
    alternative_action = kwargs.get("alternative_action")
    posttraversal_action = kwargs.get("posttraversal_action")
    condition = kwargs.get("condition")
    if hasattr(current_element, "members"):
        for member_element in current_element.members:
            if pretraversal_action(
                member_element
            ):  # pretraversal returns False to skip lower traversals if they would have no effect
                if pretraversal_action != alternative_action:
                    if condition(member_element):
                        collection_traversal(
                            member_element,
                            pretraversal_action=pretraversal_action,
                            alternative_action=alternative_action,
                            condition=condition,
                            posttraversal_action=posttraversal_action,
                        )
                    else:  # if condition false, do alternative action for every element below without checking condition
                        collection_traversal(
                            member_element,
                            pretraversal_action=alternative_action,
                            alternative_action=alternative_action,
                            condition=condition,
                        )
                else:  # if condition was false previously, continue doing alternative action for every element below without checking condition
                    collection_traversal(
                        member_element,
                        pretraversal_action=alternative_action,
                        alternative_action=alternative_action,
                        condition=condition,
                    )
            if posttraversal_action:
                posttraversal_action(member_element)
    if (
        not hasattr(current_element, "has_parent_collection")
    ) or not current_element.has_parent_collection:  # if independent element
        pretraversal_action(current_element)
        if posttraversal_action:
            posttraversal_action(current_element)


def set_showing(current_element):
    """
    Description:
        Updates the inputted elements showing attribute
    Input:
        interface_element current_element: Element being traversed through
    Output:
        None
    """
    old_showing = current_element.showing
    current_element.showing = current_element.can_show()
    return (
        old_showing or current_element.showing
    )  # if wasn't showing and still not showing, lower collection elements don't need to be updated - can skip traversal


def update_collection(current_element):
    """
    Description:
        Updates the inputted element's collection and tells it to draw, if it is showing
    Input:
        interface_element current_element: Element being traversed through
    Output:
        None
    """
    if current_element.showing:
        if hasattr(current_element, "members"):
            current_element.update_collection()
        if current_element.can_draw():
            status.draw_list.append(current_element)


def set_not_showing(current_element):
    """
    Description:
        Sets the inputted elements showing attribute to False
    Input:
        interface_element current_element: Element being traversed through
    Output:
        None
    """
    if not current_element.showing:
        return False
    current_element.showing = False
    return True


def check_showing(current_element):
    """
    Description:
        Returns whether the inputted element is showing
    Input:
        interface_element current_element: Element being traversed through
    Output:
        boolean: Returns whether the inputted element is showing
    """
    return current_element.showing
