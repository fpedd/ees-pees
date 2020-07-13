import os


def get_repo_dir():
    """Get directory of ees-pees."""
    p = os.path.abspath('..')
    print("P: ", p)
    home_dir = p.split("/ees-pees")[0]
	print("HOME_DIR: ", home_dir)
    repo_dir = os.path.join(home_dir, "ees-pees")
	print("REPO_DIR: ", repo_dir)
    return repo_dir
