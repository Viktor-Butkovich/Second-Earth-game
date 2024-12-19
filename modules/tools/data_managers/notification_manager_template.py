from ...util import scaling
import modules.constants.constants as constants
import modules.constants.status as status


class notification_manager_template:
    """
    Object that controls the displaying of notifications
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
        self.notification_queue = []
        self.lock = False
        self.default_notification_y = 500
        self.default_notification_height = 300
        self.update_notification_layout()
        self.notification_modes = [
            constants.STRATEGIC_MODE,
            constants.EARTH_MODE,
            constants.MINISTERS_MODE,
            constants.TRIAL_MODE,
            constants.MAIN_MENU_MODE,
            constants.NEW_GAME_SETUP_MODE,
        ]
        self.font = constants.fonts["default_notification"]

    def update_notification_layout(self, notification_height=0):
        """
        Description:
            Changes where notifications are displayed depending on the current game mode to avoid blocking relevant information. Also changes the height of the notification based on how much text it contains
        Input:
            int notification_height = 0: Height in pixels of the notification text. If the notification text height is greater than the default notification height, the notification will scale its height to the text
        Output:
            None
        """
        self.notification_width = 500
        self.notification_height = self.default_notification_height
        self.notification_y = self.default_notification_y
        self.notification_x = 610
        if notification_height > self.notification_height:
            self.notification_height = notification_height
        self.notification_y -= self.notification_height / 2

    def format_message(self, message):
        """
        Description:
            Converts a message string with newlines designated by /n's to a list of strings
        Input:
            string message: Initial message string
        Output:
            string list: Returns list of strings extracted from input string
        """
        new_message = []
        next_line = ""
        next_word = ""
        for index in range(len(message)):
            if not (
                (not (index + 2) > len(message) and message[index] + message[index + 1])
                == "/n"
            ):  # don't add if /n
                if not (
                    index > 0 and message[index - 1] + message[index] == "/n"
                ):  # if on n after /, skip
                    next_word += message[index]
            if message[index] == " ":
                if (
                    self.font.calculate_size(next_line + next_word)
                    > self.notification_width
                ):
                    new_message.append(next_line)
                    next_line = ""
                next_line += next_word
                next_word = ""
            elif (
                not (index + 2) > len(message) and message[index] + message[index + 1]
            ) == "/n":  # don't check for /n if at last index
                new_message.append(next_line)
                next_line = ""
                next_line += next_word
                next_word = ""
        if self.font.calculate_size(next_line + next_word) > self.notification_width:
            new_message.append(next_line)
            next_line = ""
        next_line += next_word
        new_message.append(next_line)
        return new_message

    def handle_next_notification(self, transferred_interface_elements=None):
        """
        Description:
            Creates the next queued notification, if any, whenever a notification is removed
        Input:
            None
        Output:
            None
        """
        valid_transfer = False
        if status.displayed_notification == None or True == True:
            if self.notification_queue:
                if transferred_interface_elements and (
                    self.notification_queue[0].get("notification_type", None)
                    in [
                        constants.ACTION_NOTIFICATION,
                        constants.DICE_ROLLING_NOTIFICATION,
                    ]
                    or "choices" in self.notification_queue[0]
                ):
                    valid_transfer = True
                    if "attached_interface_elements" in self.notification_queue[0]:
                        self.notification_queue[0]["attached_interface_elements"] = (
                            transferred_interface_elements
                            + self.notification_queue[0]["attached_interface_elements"]
                        )
                    else:
                        self.notification_queue[0][
                            "attached_interface_elements"
                        ] = transferred_interface_elements
                self.notification_to_front(self.notification_queue.pop(0))

        if transferred_interface_elements and not valid_transfer:
            for element in transferred_interface_elements:
                element.remove_recursive(complete=True)

    def set_lock(self, new_lock):
        """
        Description:
            Sets this notification manager's lock to the new lock value - any notifications received when locked will be displayed once the lock is removed
        Input:
            boolean new_lock: New lock value
        Output:
            None
        """
        self.lock = new_lock
        if (not new_lock) and status.displayed_notification == None:
            self.handle_next_notification()

    def display_notification(
        self, input_dict, insert_index=None
    ):  # default, exploration, or roll
        """
        Description:
            Adds a future notification to the notification queue with the inputted text and type. If other notifications are already in the notification queue, adds this notification to the back, causing it to appear last. When a
                notification is closed, the next notification in the queue is shown
        Input:
            dictionary notification_dict: Dictionary containing details regarding the notification, with 'message' being the only required parameter
        Output:
            None
        """
        if self.lock or self.notification_queue or status.displayed_notification:
            if insert_index != None:
                self.notification_queue.insert(insert_index, input_dict)
            else:
                self.notification_queue.append(input_dict)
        else:
            self.notification_to_front(input_dict)

    def notification_to_front(self, notification_dict):
        """
        Description:
            Displays and returns new notification with text matching the inputted string and a type based on what is in the front of this object's notification type queue
        Input:
            dictionary notification_dict: Dictionary containing details regarding the notification, with 'message' being the only required parameter
        Output:
            Notification: Returns the created notification
        """
        message = notification_dict[
            "message"
        ]  # message should be the only required parameter

        height = (
            len(self.format_message(message))
            * constants.fonts["default_notification"].size
        )
        self.update_notification_layout(height)

        if "notification_type" in notification_dict:
            notification_type = notification_dict["notification_type"]
        elif "choices" in notification_dict:
            notification_type = constants.CHOICE_NOTIFICATION
        elif "zoom_destination" in notification_dict:
            notification_type = constants.ZOOM_NOTIFICATION
        else:
            notification_type = constants.NOTIFICATION

        if "num_dice" in notification_dict:
            notification_dice = notification_dict["num_dice"]
        else:
            notification_dice = 0

        if (
            "attached_interface_elements" in notification_dict
            and notification_dict["attached_interface_elements"]
        ):
            attached_interface_elements = notification_dict[
                "attached_interface_elements"
            ]
        else:
            attached_interface_elements = None

        transfer_interface_elements = False
        if "transfer_interface_elements" in notification_dict:
            transfer_interface_elements = notification_dict[
                "transfer_interface_elements"
            ]

        if (
            "extra_parameters" in notification_dict
            and notification_dict["extra_parameters"]
        ):
            extra_parameters = notification_dict["extra_parameters"]
        else:
            extra_parameters = None

        input_dict = {
            "coordinates": scaling.scale_coordinates(
                self.notification_x, self.notification_y
            ),
            "ideal_width": scaling.scale_width(self.notification_width),
            "minimum_height": scaling.scale_height(self.notification_height),
            "modes": self.notification_modes,
            "image_id": "misc/default_notification.png",
            "message": message,
            "notification_dice": notification_dice,
            "init_type": notification_type,
            "attached_interface_elements": attached_interface_elements,
            "transfer_interface_elements": transfer_interface_elements,
            "extra_parameters": extra_parameters,
        }

        input_dict["on_reveal"] = notification_dict.get("on_reveal", None)
        input_dict["on_remove"] = notification_dict.get("on_remove", [])
        if input_dict["on_remove"] == None:
            input_dict["on_remove"] = []
        if notification_type == constants.CHOICE_NOTIFICATION:
            del input_dict["notification_dice"]
            input_dict["button_types"] = notification_dict["choices"]
            input_dict["choice_info_dict"] = input_dict["extra_parameters"]
        elif notification_type == constants.ZOOM_NOTIFICATION:
            del input_dict["notification_dice"]
            input_dict["target"] = notification_dict["zoom_destination"]
        new_notification = constants.actor_creation_manager.create_interface_element(
            input_dict
        )
        if notification_type == constants.DICE_ROLLING_NOTIFICATION:
            for current_die in status.dice_list:
                current_die.start_rolling()

        if "audio" in notification_dict and notification_dict["audio"]:
            if type(notification_dict["audio"]) == list:
                sound_list = notification_dict["audio"]
            else:
                sound_list = [notification_dict["audio"]]
            channel = None
            for current_sound in sound_list:
                in_sequence = False
                if type(current_sound) == dict:
                    sound_file = current_sound["sound_id"]
                    if current_sound.get("dampen_music", False):
                        constants.sound_manager.dampen_music(
                            current_sound.get("dampen_time_interval", 0.5)
                        )
                    in_sequence = current_sound.get("in_sequence", False)
                    volume = current_sound.get("volume", 0.3)
                else:
                    sound_file = current_sound
                    volume = 0.3
                if in_sequence and channel:
                    constants.sound_manager.queue_sound(
                        sound_file, channel, volume=volume
                    )
                else:
                    channel = constants.sound_manager.play_sound(
                        sound_file, volume=volume
                    )
        return new_notification

    def clear_notification_queue(self):
        """
        Description:
            Clears the notification queue
        Input:
            None
        Output:
            None
        """
        self.notification_queue = []
