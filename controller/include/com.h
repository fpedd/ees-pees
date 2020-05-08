#ifndef COM_H
#define COM_H

#define DIMS         3
#define DIST_VECS    360

typedef struct {
    unsigned int msg_cnt;   // for internal use by com
    unsigned int time_stmp;    // for internal use by com
    float target_gps[DIMS];
    float actual_gps[DIMS];
    float compass[DIMS];
    float distance[DIST_VECS];
    unsigned int touching;
} to_bcknd_msg_t;

typedef struct {
    unsigned int msg_cnt;   // for internal use by com
    unsigned int time_stmp;    // for internal use by com
    float heading;
    float speed;
} from_bcknd_msg_t;

int com_init();

int com_send(to_bcknd_msg_t data);

int com_recv(from_bcknd_msg_t data);

#endif // COM_H
