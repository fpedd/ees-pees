from pynput import keyboard
import time
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
            print("Move Up")
        elif key == keyboard.Key.down:
            move = 3
            print("Move Down")
        elif key == keyboard.Key.left:
            move = 2
            print("Move Left")
        elif key == keyboard.Key.right:
            move = 4
            print("Move Right")
        else:
            return
        self.com.send_discrete_move(move)

        # ------------------ wait for action to finish -------------------------
        time.sleep(0.1)  # give controller some time to update internal data
        self.com.send_data_request()
        while self.com.state._discrete_action_done != 1:
            self.com.send_data_request()
            time.sleep(0.1)
        print("Action done")

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False


if __name__ == "__main__":
    print("==================   this is timmy  ==================")
    timmy = Timmy(direction_type="heading")
    timmy.action()
