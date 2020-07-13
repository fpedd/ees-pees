import os


def get_repo_dir():
    """Get directory of ees-pees."""
    p = os.path.abspath('..')
    home_dir = p.split("/ees-pees/backend")[0]
    repo_dir = os.path.join(home_dir, "ees-pees")
    return repo_dir
