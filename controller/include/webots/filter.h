#ifndef FILTER_H
#define FILTER_H

// This is where our filters for senors (and maybe sensor fusion) will go.

// Implementing filtering does not make sense at this point.
// For one, the sensor data we are receiving from the robot is provided without
// any noise (we could have introduced noise in webots, but agreed not to).
// This is of course is not very realistic, as sensor data in the "real world" contains
// huge amounts of noise and uncertainty.
// Secondly we are currently facing other, more important, challenges.
// We would have loved to experiment with "noise" / "real" sensor data and
// use information about the system (our robot) to fuse / filter sensor values
// and this way get an accurate system state from the provided sensor data
// as one would do in the “real world”.
// We could have started with a simple moving average filter. However, there are
// many more filter types we could have implemented.
// We then could have moved on to state observers and represented the robot as a linear
// or nonlinear model. This model could then have been used to construct a
// luneberger observer, kalman filter, or even an extended kalman filter with
// linearization in the most recent estimate using a jacobi matrix…


#endif // FILTER_H
