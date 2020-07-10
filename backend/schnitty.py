from pynput import keyboard

import webotsgym as wg


class Schnitty():
    def __init__(self, direction_type="heading"):
        self.config = wg.WbtConfig()
        self.config.direction_type = direction_type
        self.com = wg.com.Communication(self.config)

        self.dheading = 0.05
        self.dspeed = 0.05
        self._init_action()
        self.grid = False

    def _init_action(self):
        self.act = wg.com.ActionOut(self.config)
        self.act.speed = 0
        self.act.dir = 0

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
            self.com.send_discrete_move(move)
        else:
            self.act.print_action()
            self.com.send_command(self.act)

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False


if __name__ == "__main__":
    print("================== Hi, my name is Schnitty ==================")
    schnitty = Schnitty(direction_type="steering")
    schnitty.action()
