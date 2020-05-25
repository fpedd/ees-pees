/*
 * Copyright 1996-2020 Cyberbotics Ltd.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <webots/device.h>
#include <webots/led.h>
#include <webots/motor.h>
#include <webots/robot.h>
#include <webots/lidar.h>
#include <webots/gps.h>
#include <webots/compass.h>

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>




int main(int argc, char **argv) {
  wb_robot_init();

  const int timestep = (int)wb_robot_get_basic_time_step();

  printf("This  C controller is a WIP playground for basic setup\n\n");

  WbDeviceTag motor, steer, lidar, gps, compass;
  motor   = wb_robot_get_device("motor");
  steer   = wb_robot_get_device("pivot");
  lidar   = wb_robot_get_device("lidar");
  gps     = wb_robot_get_device("gps");
  compass = wb_robot_get_device("compass");
  
    // configure devices
    // Switch to velocity control mode for unbounded motors.
  wb_motor_set_position(motor, INFINITY);
  wb_lidar_enable(lidar, timestep);
  wb_lidar_disable_point_cloud(lidar);
  wb_gps_enable(gps, timestep);
  wb_compass_enable(compass, timestep);
  
  /*
    // Print lidar properties
  printf("Frequency: %f\n", wb_lidar_get_frequency(lidar));
  printf("MAXFreq: %f\n", wb_lidar_get_max_frequency(lidar));
  printf("MINFreq: %f\n", wb_lidar_get_min_frequency(lidar));
  printf("FOV: %f\n", wb_lidar_get_fov(lidar));
  printf("MAXRange: %f\n", wb_lidar_get_max_range(lidar));
  printf("MINRange: %f\n", wb_lidar_get_min_range(lidar));
  printf("Resolution: %i\n", wb_lidar_get_horizontal_resolution(lidar));
  printf("SamplPer: %i\n", wb_lidar_get_sampling_period(lidar));
  */
  int res = wb_lidar_get_horizontal_resolution(lidar);
    
  // Loop until the simulator stops the controller.
  while (wb_robot_step(timestep) != -1) {
    const double current_time = wb_robot_get_time();
    //printf("Time: %f\n", current_time);
    
      // read values from devices
    const float*   lidar_data = wb_lidar_get_range_image(lidar); //lidar_data[res]
    const float* compass_data = wb_compass_get_values(compass);  //compass_data[3]
    const double*    gps_data = wb_gps_get_values(gps);	         //gps_data[3]

    //printf("F: %.2f - L: %.2f - R: %.2f - B: %.2f\n", lidar_data[180], lidar_data[90], lidar_data[270], lidar_data[0]);
    /* Determine silhuette
    for(int b = 0; b < 360; b++) {
      printf("%f, ", lidar_data[b]);
    }
    printf("end;; \n");*/
    
      // Unbounded motors: velocity control.
    const double v = 0 * wb_motor_get_max_velocity(motor);
    wb_motor_set_velocity(motor, v);        
    
    // position control for steering
    double p = 0.5;
    p = p * (wb_motor_get_max_position(steer) - wb_motor_get_min_position(steer)) + wb_motor_get_min_position(steer);
    wb_motor_set_position(steer, p);
  };

  wb_robot_cleanup();

  return EXIT_SUCCESS;
}
