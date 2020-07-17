import pickle


def save_object(obj, path):
    """Save object via pickle.

    Parameter:
    ----------
    obj : object
        object that should be saved at the specific path

    path : str
        path to where to save the specific object
    """
    filehandler = open(path, 'wb')
    pickle.dump(obj, filehandler)


def load_object(path):
    """Load object via pickle.

    Parameter:
    ----------
    path : str
        path to from where to load the object
    """
    filehandler = open(path, 'rb')
    return pickle.load(filehandler)
