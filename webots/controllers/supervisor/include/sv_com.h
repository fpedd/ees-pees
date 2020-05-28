#ifndef SV_COM_H
#define SV_COM_H

#define DIST_VECS    360

// supervisor --> backend
typedef struct {
	int return_code;         // return_code [int]
	float lidar_min_range;   // lidar min range in meter [float]
	float lidar_max_range;   // lidar max range in meter [float]
	int sim_time_step;       // simulation time_step in ms [int]
} __attribute__((packed)) sv_to_bcknd_msg_t;

// supervisor <-- backend
typedef struct {
	int function_code;    // function code [int]
	int seed;             // seed [int]
	int fast_simulation;  // fast_simulation [bool]
	int num_obstacles;    // num_obstacles [int]
	int world_size;       // world_size in meter [int]
} __attribute__((packed)) bcknd_to_sv_msg_t;

int sv_connect();

int sv_send(sv_to_bcknd_msg_t data);

int sv_recv(bcknd_to_sv_msg_t *data);


#endif //SV_COM_H
