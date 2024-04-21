class MissingRequiredActionError(Exception):
    def __init__(self, action_name, missing_action_name):
        self.message = (
            f"Action '{action_name}' requires '{missing_action_name}' to be installed."
        )
        super().__init__(self.message)

    def __str__(self):
        return self.message
