from pynput import keyboard

import webotsgym.environment as environment
from webotsgym.action import ContinuousAction
from webotsgym.webot import WebotAction


class Schnitty():
    def __init__(self, direction_type="heading"):
        self.dheading = 0.05
        self.dspeed = 0.05
        action_class = ContinuousAction(direction_type=direction_type)
        self.env = environment.webotsgym(action_class=action_class)
        self._init_action()
        self.grid = False

    def _init_action(self):
        self.act = WebotAction()
        self.act.speed = 0
        self.act.heading = 0

    def action(self):
        with keyboard.Listener(on_press=self.on_press,
                               on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        # TOGGLE with space
        if key == keyboard.Key.space:
            self.grid = not self.grid
            print("---------------------TOGGLED TO GRID = ", self.grid)
            return
        # Action by key
        elif key == keyboard.Key.up:
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
                self.act.heading -= self.dheading
        elif key == keyboard.Key.right:
            if self.grid is True:
                move = 4
                print("Move Right")
            else:
                self.act.heading += self.dheading
        else:
            return

        # Outpacket by grid value
        if self.grid is True:
            self.env.com.send_discrete_move(move)
        else:
            self.act.print()
            self.env.send_command(self.act)

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False


if __name__ == "__main__":
    print("================== Hi, my name is Schnitty ==================")
    schnitty = Schnitty(direction_type="heading")
    schnitty.action()
