#include <gtest/gtest.h>

#include "webots/pid.h"

TEST(pid, init) {
	pid_ctrl_t pid_1;

	// init should set all values
	pid_init(&pid_1, 1.0, 2.0, 3.0, 4.0, 5.0, true);
	ASSERT_NEAR(pid_1.k_p, 1.0, 1.0e-10);
	ASSERT_NEAR(pid_1.k_i, 2.0, 1.0e-10);
	ASSERT_NEAR(pid_1.k_d, 3.0, 1.0e-10);
	ASSERT_NEAR(pid_1.out_min, 4.0, 1.0e-10);
	ASSERT_NEAR(pid_1.out_max, 5.0, 1.0e-10);
	ASSERT_NEAR(pid_1.err_acc, 0.0, 1.0e-10);
	ASSERT_NEAR(pid_1.prev_in, 0.0, 1.0e-10);
	ASSERT_EQ(pid_1.wa, true);

	pid_ctrl_t pid_2;

	// min cant be greater than max
	pid_init(&pid_2, -1.0, -2.0, -3.0, -4.0, -5.0, false);
	ASSERT_EQ(pid_init(&pid_2, -1.0, -2.0, -3.0, -4.0, -5.0, false), -1);

	// init should also set negative values
	pid_init(&pid_2, -1.0, -2.0, -3.0, -5.0, -4.0, false);
	ASSERT_NEAR(pid_2.k_p, -1.0, 1.0e-10);
	ASSERT_NEAR(pid_2.k_i, -2.0, 1.0e-10);
	ASSERT_NEAR(pid_2.k_d, -3.0, 1.0e-10);
	ASSERT_NEAR(pid_2.out_min, -5.0, 1.0e-10);
	ASSERT_NEAR(pid_2.out_max, -4.0, 1.0e-10);
	ASSERT_NEAR(pid_2.err_acc, -0.0, 1.0e-10);
	ASSERT_NEAR(pid_2.prev_in, -0.0, 1.0e-10);
	ASSERT_EQ(pid_2.wa, false);
}


TEST(pid, run) {
	pid_ctrl_t pid_1;
	float out = 0.0;

	pid_init(&pid_1, 1.0, 2.0, 3.0, -1.0, 1.0, true);

	// time can not be zero
	ASSERT_EQ(pid_run(&pid_1, 0.0, 0.0, 0.0, &out), -1);
	ASSERT_NEAR(out, 0.0, 1.0e-10);

	// time can not be negative
	ASSERT_EQ(pid_run(&pid_1, -1.0, 0.0, 0.0, &out), -1);
	ASSERT_NEAR(out, 0.0, 1.0e-10);

	// test pid compute 1
	pid_ctrl_t pid_2;
	pid_init(&pid_2, 1.0, 2.0, 5.0, -100.0, 100.0, true);
	ASSERT_EQ(pid_run(&pid_2, 1.0, 1.0, 2.0, &out), 0);
	ASSERT_NEAR(out, -13.0, 1.0e-10);

	// test pid compute 2
	pid_ctrl_t pid_3;
	pid_init(&pid_3, 1.0, 2.0, 3.0, -100.0, 100.0, true);
	ASSERT_EQ(pid_run(&pid_3, 1.0, -1.0, 1.0, &out), 0);
	ASSERT_NEAR(out, -9.0, 1.0e-10);

	// test pid compute 3
	pid_ctrl_t pid_4;
	pid_init(&pid_4, 1.0, 2.0, 3.0, -100.0, 100.0, true);
	ASSERT_EQ(pid_run(&pid_4, 0.01, 0.673, 0.123, &out), 0);
	ASSERT_NEAR(out, -36.339000701904297, 1.0e-10);

	// test pid compute 4
	pid_ctrl_t pid_5;
	pid_init(&pid_5, 1.0, 2.0, 3.0, -100.0, 100.0, false);
	ASSERT_EQ(pid_run(&pid_5, 1.0, 1.0, 5.0, &out), 0);
	ASSERT_NEAR(out, -27.0, 1.0e-10);
	ASSERT_EQ(pid_run(&pid_5, 1.0, 1.0, 5.0, &out), 0);
	ASSERT_NEAR(out, -20.0, 1.0e-10);
	ASSERT_EQ(pid_run(&pid_5, 1.0, 1.0, 5.0, &out), 0);
	ASSERT_NEAR(out, -28.0, 1.0e-10);

}
