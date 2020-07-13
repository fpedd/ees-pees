#include <gtest/gtest.h>

#include "util.h"

TEST(util, round_with_factor) {

	ASSERT_NEAR(round_with_factor(-0.23481, 0.3), -0.15, 1.0e-5);
	ASSERT_NEAR(round_with_factor(-0.89712, 0.3), -0.75, 1.0e-5);
	ASSERT_NEAR(round_with_factor(-1.42131, 0.3), -1.35, 1.0e-5);
	ASSERT_NEAR(round_with_factor(-0.74523, 0.3), -0.75, 1.0e-5);

	ASSERT_NEAR(round_with_factor(0.23481, 0.25), 0.125, 1.0e-5);
	ASSERT_NEAR(round_with_factor(0.89712, 0.25), 0.875, 1.0e-5);
	ASSERT_NEAR(round_with_factor(1.42131, 0.25), 1.375, 1.0e-5);
	ASSERT_NEAR(round_with_factor(0.74523, 0.25), 0.625, 1.0e-5);

	ASSERT_NEAR(round_with_factor(0.23481, 0.5), 0.25, 1.0e-5);
	ASSERT_NEAR(round_with_factor(0.89712, 0.5), 0.75, 1.0e-5);
	ASSERT_NEAR(round_with_factor(1.42131, 0.5), 1.25, 1.0e-5);
	ASSERT_NEAR(round_with_factor(0.74523, 0.5), 0.75, 1.0e-5);

}
