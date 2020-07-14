import pickle

def save_object(obj, path):
    """Save object via pickle."""
    filehandler = open(path, 'wb')
    pickle.dump(obj, filehandler)


def load_object(path):
    """Load object via pickle."""
    filehandler = open(path, 'rb')
    return (pickle.load(filehandler))