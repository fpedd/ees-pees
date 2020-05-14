#ifndef WEBOTS_H
#define WEBOTS_H

// This will contain all code to handle the communication with the webots robot.
// It should provide all data comming from the robot and all data going to the robot
// in two structs

void wb_init_com();

void wb_test_com();

int wb_send(from_bcknd_msg_t data);

int wb_recv(to_bcknd_msg_t *data);

#endif // WEBOTS_H
