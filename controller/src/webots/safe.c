#include "webots/safe.h"
#include "backend/backend_com.h"
#include "silhouette.h"

int safety_check(bcknd_to_ext_msg_t *bcknd_to_ext) {

	(void) bcknd_to_ext;

	// TODO: here we need to check if we are hitting smth and if
	// so we need to set the speed (and maybe heading) to 0  or smth similar

	// if hitting then
	// bcknd_to_ext->speed = 0;
	// bcknd_to_ext->heading = 0;

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
