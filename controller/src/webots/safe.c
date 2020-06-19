#include "webots/safe.h"

#include <math.h>

#include "backend/backend_com.h"
#include "silhouette.h"

int safety_check(init_to_ext_msg_t init_data, ext_to_bcknd_msg_t ext_to_bcknd,
	             bcknd_to_ext_msg_t* bcknd_to_ext) {

	(void) init_data;
	(void) ext_to_bcknd;
	(void) bcknd_to_ext;

	// TODO: here we need to check if we are hitting smth and if
	// so we need to set the speed (and maybe heading) to 0  or smth similar

	// maybe: if hitting then
	// bcknd_to_ext->speed = 0;
	// bcknd_to_ext->heading = 0;

	// return 0 if action was okay
	// return 1 if we had to take over control for safety reasons
	return 0;
}

int touching(float dist[]) {

	int touching = 0;
	int currently_touching = 0;
	for (int i=0; i<DIST_VECS; i++) {
		if (dist[i] < silhouette[i] && currently_touching == 0) {
			currently_touching = 1;
		} else if (!(dist[i] < silhouette[i]) && currently_touching == 1) {
			currently_touching = 0;
			touching ++;
		}
	}

	return touching;
}


int check_for_tipover(wb_to_ext_msg_t wb_to_ext) {

	if (fabs(wb_to_ext.actual_gps[1] - 0.026) > 0.02) {
		return -1;
	} else {
		return 0;
	}
}
