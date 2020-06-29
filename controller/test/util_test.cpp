#include <gtest/gtest.h>

#include "util.h"

// Keine Ahnung ob das hier stimmt haha, bitte check das nochmal :D

TEST(util, heading_in_norm) {
	double actual_heading = heading_in_norm(1.0, 0.0, 0.0);
	float expected_heading = 0.0;
	ASSERT_NEAR(expected_heading, actual_heading, 1.0e-10);

	actual_heading = heading_in_norm(0.0, 0.0, 1.0);
	expected_heading = -0.5;
	ASSERT_NEAR(expected_heading, actual_heading, 1.0e-10);
}

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
