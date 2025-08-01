# Contains UUID management singleton


class uuid_manager:
    """
    Object that assigns unique identifiers (UUIDs) to objects
    """

    def __init__(self):
        """
        Initializes this object
        """
        self.next_available_uuid: int = 0

    def assign_uuid(self) -> str:
        """
        Description:
            Assigns a new UUID to an object
        Input:
            None
        Output:
            string: The newly assigned UUID
        """
        current_uuid = self.next_available_uuid
        self.next_available_uuid += 1
        return str(current_uuid)
