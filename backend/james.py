from pynput import keyboard

import webotsgym as wg


class James():
    def __init__(self, direction_type="heading"):
        action_class = wg.WbtActContinuous(direction_type=direction_type)
        self.env = wg.WbtGym(action_class=action_class)
        self.dheading = 0.05
        self.dspeed = 0.05
        self._init_action()

    def _init_action(self):
        self.act = wg.com.ActionOut()
        self.act.speed = 0
        self.act.heading = 0

    def action(self):
        with keyboard.Listener(on_press=self.on_press,
                               on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        if key == keyboard.Key.up:
            self.act.speed += self.dspeed
        elif key == keyboard.Key.down:
            self.act.speed -= self.dspeed
        elif key == keyboard.Key.left:
            self.act.heading -= self.dheading
        elif key == keyboard.Key.right:
            self.act.heading += self.dheading
        else:
            return
        self.act.print()
        self.env.send_command(self.act)

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False


if __name__ == "__main__":
    print("================== Hi, my name is James ==================")
    james = James(direction_type="heading")
    james.action()
