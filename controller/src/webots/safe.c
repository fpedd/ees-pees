#include "webots/safe.h"


int safety_check(bcknd_to_ext_msg_t *bcknd_to_ext) {

    (void) bcknd_to_ext;

    // TODO: here we need to check if we are hitting smth and if
    // so we need to set the speed (and maybe heading) to 0  or smth similar

    // if hitting then
    // bcknd_to_ext->speed = 0;
    // bcknd_to_ext->heading = 0;

    return 0;
}
