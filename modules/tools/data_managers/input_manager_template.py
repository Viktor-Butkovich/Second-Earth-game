from ...util import text_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class input_manager_template:
    """
    Object designed to manage the passing of typed input from the text box to different parts of the program
    """

    def __init__(self):
        """
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        """
        self.previous_input = ""
        self.taking_input = False
        self.old_taking_input = self.taking_input
        self.stored_input = ""
        self.send_input_to: callable = None

    def check_for_input(self):
        """
        Description:
            Returns true if input was just being taken and is no longer being taken, showing that there is input ready. Otherwise, returns False.
        Input:
            None
        Output:
            boolean: True if input was just being taken and is no longer being taken, showing that there is input ready. Otherwise, returns False.
        """
        if self.old_taking_input == True and self.taking_input == False:
            return True
        else:
            return False

    def start_receiving_input(self, solicitant: callable, prompt: str = None):
        """
        Description:
            Displays the prompt for the user to enter input and prepares to receive input and send it to the part of the program requesting input
        Input:
            callable solicitant: Function to call with message as input
            string prompt: Prompt given to the player to enter input
        Output:
            None
        """
        text_utility.print_to_screen(prompt)
        constants.notification_manager.display_notification(
            {
                "message": prompt
                + "/n /n(Type in red text box in lower left, press enter when done)",
                "extra_parameters": {"can_remove": False},
            }
        )
        self.send_input_to = solicitant
        self.taking_input = True
        flags.typing = True

    def update_input(self):
        """
        Description:
            Updates whether this object is currently taking input
        Input:
            None
        Output:
            None
        """
        self.old_taking_input = self.taking_input

    def receive_input(self, received_input):
        """
        Description:
            Sends the inputted string to the part of the program that initially requested input
        Input:
            String received_input: Input entered by the user into the text box
        Output:
            None
        """
        self.send_input_to(received_input)
        self.taking_input = False
        flags.typing = True
        status.displayed_notification.on_click(override_can_remove=True)
