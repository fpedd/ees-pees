from pynput import keyboard
import webotsgym.environment as environment
from webotsgym.action import ContinuousAction
from webotsgym.webot import WebotAction


class Keyboard():
    def __init__(self, callback):
        self.callback = callback
        self.dheading = 0.05
        self.dspeed = 0.05
        self._init_action()

    def _init_action(self):
        self.act = WebotAction()
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
        self.callback(self.act)

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False



class James():
    def __init__(self, direction_type="heading"):
        action_class = ContinuousAction(direction_type=direction_type)
        self.env = environment.WebotsEnv(action_class=action_class)
        kb = Keyboard(self.callback)
        kb.action()

    def callback(self, action):
        self.env.send_command_and_data_request(action)


if __name__ == "__main__":
    print("================== Hi, my name is James ==================")
    james = James(direction_type="heading")
