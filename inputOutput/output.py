import sys

__author__ = 'snorre'


def show_info_dialog(info):
    """
    :type info: str
    :param info: The info to print
    """
    sys.stdout.write(info+'\n')


def show_confirmation_dialog(question, default="yes"):
    """
    Code source: http://code.activestate.com/recipes/577058/
    :type question: str
    :param question: The question to ask the user
    :type default: str
    :param default: the default answer (if none given by user)
    :return: true if yes, false if no
    :rtype: bool
    :raise: ValueError if default not in valid
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " \
                             "(or 'y' or 'n').\n")


def show_option_dialog(question, options):
    """
    Show a list based option dialog.
    :type question: str
    :param question: the question to ask
    :type options: list
    :param options: options to choose from
    :rtype: str
    :return: choice, the chosen option
    """
    sys.stdout.write(question + "\n")
    while True:
        sys.stdout.write("Available options are:\n")
        for option in options:
            sys.stdout.write(option + "\n")
        choice = raw_input().lower().strip()
        if choice in options:
            return choice
        else:
            sys.stdout.write("Please type on of the options exactly as it is "
                             "displayed\n")


def show_input_dialog(question):
    """
    Shows a question prompting user for an input
    :type question: str
    :param question: the question to ask the user
    """
    sys.stdout.write(question)
    while True:
        choice = raw_input().lower().strip()
        if not (choice == '' or choice is None):
            return choice
        else:
            sys.stdout.write("Please type in an non-empty answer")