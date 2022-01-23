class UserException(Exception):
    message: str = ""

    def __init__(self):
        super().__init__(self.message)


class UserInstanceNotRecognised(UserException):

    message = (
        "User instance not recognized. The file must represent an instance of User."
    )


class UserNotSetup(UserException):

    message = (
        "User profile has not been set up.\nEither run from the command line to run the user setup wizard, "
        "or manually set domain and password properties in your application.\n"
        "Refer to documentation for further details."
    )
