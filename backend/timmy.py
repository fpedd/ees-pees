from pynput import keyboard
import time
import webotsgym.communicate as communicate


class Timmy():
    def __init__(self, direction_type="heading"):
        self.dheading = 0.05
        self.dspeed = 0.05
        self.com = communicate.Com()

    def action(self):
        with keyboard.Listener(on_press=self.on_press,
                               on_release=self.on_release) as listener:
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

        # ------------------ wait for action to finish ------------------------
        time.sleep(0.1)  # give controller some time to update internal data
        self.com.send_data_request()
        time_out = False
        timestamp_start = self.com.state.sim_time
        while self.com.state._discrete_action_done != 1:

            print((self.com.state.sim_time - timestamp_start))
            if (self.com.state.sim_time - timestamp_start) >= 5:
                time_out = True
                break
            self.com.send_data_request()
            time.sleep(0.1)

        if time_out and self.com.state._touching:
            move = self.reverse_move(move)
            self.com.send_discrete_move(move)
            print("Move reversed")
        elif time_out:
            print("Time out")
        else:
            print("Action Done")

        print("GPS actual: " + str(self.com.state.gps_actual))

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False

    def reverse_move(self, move):
        # East -> West
        if move == 4:
            return 2
        # South -> North
        if move == 3:
            return 1
        # West -> East
        if move == 2:
            return 4
        # North -> South
        if move == 1:
            return 3
        return None


if __name__ == "__main__":
    print("================== Hi, my name is Timmy ==================")
    timmy = Timmy(direction_type="heading")
    timmy.action()
