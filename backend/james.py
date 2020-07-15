from pynput import keyboard

import webotsgym as wg


class James():
    """Create default class james to control the robot.

    Options:
    With james you can decide to drive the robot by your own
    in the discrete or continuous action space.
    With the keyboard you can increase or decrease the speed
    change the heading in the continuous action space by the default.
    In the discrete action space every key press will trigger
    an action in the respective direction.

    For adjustment option see __init__!
    """

    def __init__(self, direction_type="heading"):
        """Initialize default james with direction type.

        Default Settings:
        Action space: continuous action space
        Heading changes: 0.05 in comparison to pre-state by key press.
        Speed changes: 0.05 in comparison to pre-state by key press.

        Options:
        Change to grid action space -> self.grid = True
        Adjust difference for heading -> self.dheading = [0 to 1]
        Adjust difference for speed -> self.dspeed = [0 to 1]
        """
        self.config = wg.WbtConfig()
        self.config.direction_type = direction_type
        self.com = wg.com.Communication(self.config)

        self.dheading = 0.05
        self.dspeed = 0.05
        self._init_action()
        self.grid = False

    def _init_action(self):
        """Initialize the speed and dir the robot starts with."""
        self.act = wg.com.ActionOut(self.config)
        self.act.speed = 0
        self.act.dir = 0

    def action(self):
        """Listen to keyboard."""
        with keyboard.Listener(on_press=self.on_press,
                               on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        """Create action and send it to the controller.

        Depending on grid or continuous the key press of space
        or arrows keys will trigger action and send it to the controller.

        The space toggles between the continuous and grid world.
        """
        # TOGGLE with space
        if key == keyboard.Key.space:
            self.grid = not self.grid
            print("----------- TOGGLED TO GRID = ", self.grid, "-----------")
            return
        # Action by key
        if key == keyboard.Key.up:
            if self.grid is True:
                move = 1
                print("Move Up")
            else:
                self.act.speed += self.dspeed
        elif key == keyboard.Key.down:
            if self.grid is True:
                move = 3
                print("Move Down")
            else:
                self.act.speed -= self.dspeed
        elif key == keyboard.Key.left:
            if self.grid is True:
                move = 2
                print("Move Left")
            else:
                self.act.dir -= self.dheading
        elif key == keyboard.Key.right:
            if self.grid is True:
                move = 4
                print("Move Right")
            else:
                self.act.dir += self.dheading
        else:
            return

        # Outpacket by grid value
        if self.grid is True:
            self.com.send_grid_move(move, safety=True)
        else:
            self.act.print_action()
            self.com.send_command(self.act)

    def on_release(self, key):
        """Return False to end webots through ESC key."""
        if key == keyboard.Key.esc:
            return False


if __name__ == "__main__":
    print("================== Hi, my name is James ==================")
    schnitty = James(direction_type="steering")
    schnitty.action()
