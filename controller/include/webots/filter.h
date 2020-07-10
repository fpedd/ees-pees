#ifndef FILTER_H
#define FILTER_H

// This is where our filters for senors (and maybe sensor fusion) will go.

// Fabian, 09.07.2020
// At this point implementing filtering does not make sense anymore.
// For one, the sensor data we are receiving from the robot is provided without
// any noise (we could have introduced noise in webots, but agreed not to)
// and secondly we are currently facing other, more important challenges.
// I would have loved to experiment with "noise" / "real" sensor data and
// use information about the system to fuse / filter sensor values and get
// an accurate system state.
// We could have started with a simple moving average filter. There are waaay
// more filters we could have implemented.
// We then could have moved on to observers and represented the robot as a linear
// or non linear model.This model could then used to construct a luneberger observer
// kalman filter or even an extended kalman filter with linearizitaion in the
// most recent estimate using the jacobi matrix...

#endif // FILTER_H
