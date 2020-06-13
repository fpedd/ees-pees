#include <gtest/gtest.h>

#include "webots/pid.h"

TEST(pid, init) {
	pid_ctrl_t pid_1;

	pid_init(&pid_1, 1.0, 2.0, 3.0, 4.0, 5.0, true);
	ASSERT_NEAR(pid_1.k_p, 1.0, 1.0e-10);
	ASSERT_NEAR(pid_1.k_i, 2.0, 1.0e-10);
	ASSERT_NEAR(pid_1.k_d, 3.0, 1.0e-10);
	ASSERT_NEAR(pid_1.out_min, 4.0, 1.0e-10);
	ASSERT_NEAR(pid_1.out_max, 5.0, 1.0e-10);
	ASSERT_NEAR(pid_1.err_acc, 0.0, 1.0e-10);
	ASSERT_NEAR(pid_1.prev_in, 0.0, 1.0e-10);
	ASSERT_NEAR(pid_1.wa, true, 1.0e-10);

	pid_ctrl_t pid_2;

	pid_init(&pid_2, -1.0, -2.0, -3.0, -4.0, -5.0, false);
	ASSERT_EQ(pid_init(&pid_2, -1.0, -2.0, -3.0, -4.0, -5.0, false), -1);

	pid_init(&pid_2, -1.0, -2.0, -3.0, -5.0, -4.0, false);
	ASSERT_NEAR(pid_2.k_p, -1.0, 1.0e-10);
	ASSERT_NEAR(pid_2.k_i, -2.0, 1.0e-10);
	ASSERT_NEAR(pid_2.k_d, -3.0, 1.0e-10);
	ASSERT_NEAR(pid_2.out_min, -5.0, 1.0e-10);
	ASSERT_NEAR(pid_2.out_max, -4.0, 1.0e-10);
	ASSERT_NEAR(pid_2.err_acc, -0.0, 1.0e-10);
	ASSERT_NEAR(pid_2.prev_in, -0.0, 1.0e-10);
	ASSERT_NEAR(pid_2.wa, false, 1.0e-10);
}
