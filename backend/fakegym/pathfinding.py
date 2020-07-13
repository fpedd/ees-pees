from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

class Pathfinding():
    
    def __init__(self, field, gps_actual, gps_target):
        self.field = field
        self.gps_actual = gps_actual
        self.gps_target = gps_target

    def finder_path(self, finder=AStarFinder):
        """Shortest pathfinding algorithms.

        Args:
            finder (optional): 
                Choose different algorithms. Defaults to AStarFinder.

        Returns:
            Each grid position of shortest path.
        """
        grid = self.field.copy()
        grid[grid > 0] = 99
        grid[grid == 0] = 1
        grid[grid == 99] = 0
        grid = grid.astype(int)
        grid = grid.tolist()
        grid = Grid(matrix=grid)

        # find path
        sx, sy = self.gps_actual
        tx, ty = self.gps_target
        start = grid.node(sy, sx)
        end = grid.node(ty, tx)
        finder = finder()
        path, _ = finder.find_path(start, end, grid)

        return path