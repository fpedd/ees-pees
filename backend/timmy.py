from pynput import keyboard

import webotsgym.communicate as communicate


class Timmy():
    def __init__(self, direction_type="heading"):
        self.dheading = 0.05
        self.dspeed = 0.05
        self.com = communicate.Com()

    def action(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        if key == keyboard.Key.up:
            move = 1
        elif key == keyboard.Key.down:
            move = 3
        elif key == keyboard.Key.left:
            move = 2
        elif key == keyboard.Key.right:
            move = 4
        else:
            return
        print(move)
        self.com.send_discrete_move(move)

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False


if __name__ == "__main__":
    timmy = Timmy(direction_type="heading")
    timmy.action()
