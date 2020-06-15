#include <gtest/gtest.h>

#include "webots/navi.h"

TEST(navi, get_heading) {

	float start1[] = {0, 0};
	float dest1[] = {0, 1};
	ASSERT_NEAR(navi_get_heading(start1, dest1), 0.0, 1.0e-10);

	float start2[] = {0, 0};
	float dest2[] = {1, 0};
	ASSERT_NEAR(navi_get_heading(start2, dest2), -0.5, 1.0e-10);

	float start3[] = {0, 0};
	float dest3[] = {-1, 0};
	ASSERT_NEAR(navi_get_heading(start3, dest3), 0.5, 1.0e-10);

	float start4[] = {0, 0};
	float dest4[] = {1, 1};
	ASSERT_NEAR(navi_get_heading(start4, dest4), -0.25, 1.0e-10);

	float start5[] = {0, 0};
	float dest5[] = {0, -1};
	ASSERT_NEAR(navi_get_heading(start5, dest5), 1.0, 1.0e-10);

	float start6[] = {0, 0};
	float dest6[] = {-1, -1};
	ASSERT_NEAR(navi_get_heading(start6, dest6), 0.75, 1.0e-10);

	float start7[] = {0, 0};
	float dest7[] = {0, 0};
	ASSERT_NEAR(navi_get_heading(start7, dest7), 0.0, 1.0e-10);

}

TEST(navi, get_distance) {

	float start1[] = {0, 0};
	float dest1[] = {0, 1};
	ASSERT_NEAR(navi_get_distance(start1, dest1), 1.0, 1.0e-5);

	float start2[] = {0, 0};
	float dest2[] = {1, 0};
	ASSERT_NEAR(navi_get_distance(start2, dest2), 1.0, 1.0e-5);

	float start3[] = {0, 0};
	float dest3[] = {-1, 0};
	ASSERT_NEAR(navi_get_distance(start3, dest3), 1.0, 1.0e-5);

	float start4[] = {0, 0};
	float dest4[] = {1, 1};
	ASSERT_NEAR(navi_get_distance(start4, dest4), 1.41421356237, 1.0e-5);

	float start5[] = {0, 0};
	float dest5[] = {0, -1};
	ASSERT_NEAR(navi_get_distance(start5, dest5), 1.0, 1.0e-5);

	float start6[] = {0, 0};
	float dest6[] = {-1, -1};
	ASSERT_NEAR(navi_get_distance(start6, dest6), 1.41421356237, 1.0e-5);

	float start7[] = {0, 0};
	float dest7[] = {0, 0};
	ASSERT_NEAR(navi_get_distance(start7, dest7), 0.0, 1.0e-5);

}

TEST(navi, check_back) {

	float start1 = 0.0;
	float dest1 = 0.0;
	ASSERT_EQ(navi_check_back(start1, dest1), 0);

	float start2 = 0.0;
	float dest2 = -0.25;
	ASSERT_EQ(navi_check_back(start2, dest2), 0);

	float start3 = 0.0;
	float dest3 = 0.49;
	ASSERT_EQ(navi_check_back(start3, dest3), 0);

	float start4 = -0.9;
	float dest4 = 0.0;
	ASSERT_EQ(navi_check_back(start4, dest4), 1);

	float start5 = -0.9;
	float dest5 = -0.45;
	ASSERT_EQ(navi_check_back(start5, dest5), 0);

	float start6 = 0.8;
	float dest6 = 0.25;
	ASSERT_EQ(navi_check_back(start6, dest6), 1);

	float start7 = -0.95;
	float dest7 = 0.8;
	ASSERT_EQ(navi_check_back(start7, dest7), 0);

	float start8 = 0.8;
	float dest8 = -0.8;
	ASSERT_EQ(navi_check_back(start8, dest8), 0);

	float start9 = -0.8;
	float dest9 = 0.8;
	ASSERT_EQ(navi_check_back(start9, dest9), 0);

	float start10 = -0.8;
	float dest10 = -0.25;
	ASSERT_EQ(navi_check_back(start10, dest10), 1);

	float start11 = 0.8;
	float dest11 = 0.25;
	ASSERT_EQ(navi_check_back(start11, dest11), 1);

	float start12 = -0.5;
	float dest12 = 0.5;
	ASSERT_EQ(navi_check_back(start12, dest12), 1);

	float start13 = 0.5;
	float dest13 = -0.5;
	ASSERT_EQ(navi_check_back(start13, dest13), 1);

}
