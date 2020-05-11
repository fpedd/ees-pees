# EES-PEES Robot Project Backend

## Interface to external controller - communicate.py
* `Packet` - holds the received data in `buffer` as well as some control information `time`, `count` and `success` (the packet has arrived as intented from the external controller.
* `WebotState` - holds all information about the current state of the Webot, i.e. `gps_target`, `gps_actual`, `compass`, `distance`, `touching`. State will be filled from `Packet.buffer` using internal function `fill_from_buffer(buffer).` To get the current state as numpy.ndarray call `get()`.
* `WebotAction` - blueprint for Webots actions to be used in other modules. Attributes: `heading`, `speed`.
* `Com` - Main communication class, used to receive (`recv()`) and `send(action:WebotAction)` data from the external controller.

