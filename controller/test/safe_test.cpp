#include <gtest/gtest.h>

#include "webots/safe.h"
#include "silhouette.h"


TEST(safe, check_for_tipover) {

	data_from_wb_msg_t data_from_wb;

	data_from_wb.actual_gps[1] = 0.05;
	ASSERT_TRUE(check_for_tipover(data_from_wb));

	data_from_wb.actual_gps[1] = -0.05;
	ASSERT_TRUE(check_for_tipover(data_from_wb));

	data_from_wb.actual_gps[1] = 0.01;
	ASSERT_FALSE(check_for_tipover(data_from_wb));

}

TEST(safe, touching) {

	data_from_wb_msg_t data_from_wb;

	for (int i=0; i<DIST_VECS; i++) {
		data_from_wb.distance[i] = silhouette[i];
	}

	ASSERT_FALSE(touching(data_from_wb));

	data_from_wb.distance[rand()%DIST_VECS] /= 2;

	ASSERT_TRUE(touching(data_from_wb));


}

TEST(safe, compare_direction) {

	double vec0[2] = {1, 0};
	double vec1[2] = {-1, 0};
	double vec2[2] = {0, 1};
	double vec3[2] = {0, -1};
	double vec4[2] = {0, 2};
	double vec5[2] = {1, 2};
	double vec6[2] = {2, 3};
	double vec7[2] = {-2, 3};

	ASSERT_EQ(compare_direction(vec5, vec6, 2), FORWARDS);
	ASSERT_EQ(compare_direction(vec2, vec4, 2), FORWARDS);
	ASSERT_EQ(compare_direction(vec5, vec7, 2), FORWARDS);

	ASSERT_EQ(compare_direction(vec0, vec2, 2), STOPPED);

	ASSERT_EQ(compare_direction(vec3, vec4, 2), BACKWARDS);
	ASSERT_EQ(compare_direction(vec0, vec1, 2), BACKWARDS);
	ASSERT_EQ(compare_direction(vec3, vec2, 2), BACKWARDS);
}

TEST(safe, condense_data) {

	float distance[DIST_VECS];
	for (int i = 0; i < DIST_VECS; i++) {
		distance[i] = (float) rand() * 3.5 / RAND_MAX;
	}

	ASSERT_NEAR(condense_data(distance, 5, -1), -1.0, 1.0e-10);
	ASSERT_NEAR(condense_data(distance, 5, 360), -1.0, 1.0e-10);
	ASSERT_NEAR(condense_data(distance, 0, 20), -1.0, 1.0e-10);
	ASSERT_NEAR(condense_data(distance, -1, 20), -1.0, 1.0e-10);
	ASSERT_NEAR(condense_data(distance, 360, 20), -1.0, 1.0e-10);

	for (int i = 0; i < 40; i++) {
		int angle = rand() % DIST_VECS;

		ASSERT_NEAR(condense_data(distance, 1, angle), distance[angle], 1.0e-10);

		float sum = 0.0;
		int width = rand() % DIST_VECS;

		int new_angle = angle + DIST_VECS;

		for (int i = new_angle - width/2; i < new_angle + (width+1)/2; i++) {
			sum += distance[i%DIST_VECS];
		}

		float avg = sum / width;

		// printf("Width: %d\t angle: %d\n", width, angle);

		ASSERT_NEAR(condense_data(distance, width, angle), avg, 1.0e-10);
		ASSERT_GE(condense_data(distance, width, angle), 0.0);
	}

	for (int i = 0; i < DIST_VECS; i++) {
		distance[i] = 1.0;
	}

	ASSERT_NEAR(condense_data(distance, 2, 10), 1.0, 1.0e-10);
	ASSERT_NEAR(condense_data(distance, 20, 170), 1.0, 1.0e-10);
	ASSERT_NEAR(condense_data(distance, 21, 20), 1.0, 1.0e-10);
	ASSERT_NEAR(condense_data(distance, 81, 0), 1.0, 1.0e-10);
}

TEST(safe, too_close_to_obstacle) {

	float distance[DIST_VECS];
	for (int i = 0; i < DIST_VECS; i++) {
		distance[i] = 0.04; // CLOSEST_ALLOWED = 0.04
	}

	ASSERT_FALSE(too_close_to_obstacle(distance, -0.1));
	ASSERT_FALSE(too_close_to_obstacle(distance, 0.1));
	ASSERT_FALSE(too_close_to_obstacle(distance, 0.0));

	for (size_t i = 0; i < DIST_VECS; i++) {
		distance[i] /= 2;

		if(170 < i && i < 185) { // Obstacle in front
			ASSERT_TRUE(too_close_to_obstacle(distance, -0.1));
			ASSERT_TRUE(too_close_to_obstacle(distance, -0.1));
			ASSERT_FALSE(too_close_to_obstacle(distance, 0.1));
			ASSERT_FALSE(too_close_to_obstacle(distance, 0.1));
			ASSERT_FALSE(too_close_to_obstacle(distance, 0.0));
			ASSERT_FALSE(too_close_to_obstacle(distance, 0.0));


		} else if (315 < i && i < 325) { // Obstacle behind
			// printf("i: %d\n", i);
			ASSERT_TRUE(too_close_to_obstacle(distance, 0.1));
			ASSERT_TRUE(too_close_to_obstacle(distance, 0.1));
			ASSERT_FALSE(too_close_to_obstacle(distance, -0.1));
			ASSERT_FALSE(too_close_to_obstacle(distance, -0.1));
			ASSERT_FALSE(too_close_to_obstacle(distance, 0.0));
			ASSERT_FALSE(too_close_to_obstacle(distance, 0.0));

		}

		distance[i] *= 2;
	}
}


TEST(safe, predict_angle) {


	for (size_t i = 0; i < 20; i++) {
		double speed = (double) (2*rand()-RAND_MAX)/RAND_MAX;
		double steering = (double) (2*rand()-RAND_MAX)/RAND_MAX;

		int angle = predict_angle(FORWARDS, speed, steering);
		ASSERT_TRUE(0 <= angle && angle < DIST_VECS);

		angle = predict_angle(BACKWARDS, speed, steering);
		ASSERT_TRUE(0 <= angle && angle < DIST_VECS);

		ASSERT_EQ(predict_angle(STOPPED, speed, steering), 179);
	}


}
