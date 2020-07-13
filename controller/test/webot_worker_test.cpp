#include <gtest/gtest.h>

#include "webots/webot_worker.h"

TEST(util, heading_in_norm) {
	double actual_heading = heading_in_norm(1.0, 0.0, 0.0);
	float expected_heading = 0.0;
	ASSERT_NEAR(expected_heading, actual_heading, 1.0e-10);

	actual_heading = heading_in_norm(0.0, 0.0, 1.0);
	expected_heading = -0.5;
	ASSERT_NEAR(expected_heading, actual_heading, 1.0e-10);
}
