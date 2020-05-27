#define uint8 unsigned short
#define int32 int

typedef enum {
	Program4,
	Program5,
	1200RPM,
	Program1,
	Program2,
	60deg_Water,
	Program3,
	1600RPM,
	40deg_Water,
	Idle,
	FINISHED,
	50deg_Water,
	Display_Hour,
	1400RPM
} MyStm_e;

MyStm_e st;

int32 x = 0;
int32 button = 0;
int32 cycles = 0;
int32 run = 0;
int32 finish = 0;

static uint8 t704() {
	return cycles == 72000;
}

static uint8 t419() {
	return button == 5;
}

static uint8 t307() {
	return cycles == 96000;
}

static uint8 t559() {
	return run == 0;
}

static uint8 t831() {
	return button == 1;
}

static uint8 t654() {
	return finish == 1;
}

static uint8 t175() {
	return button == 2;
}

static uint8 t769() {
	return run == 1;
}

static uint8 t219() {
	return run == 1;
}

static uint8 t251() {
	return button == 3;
}

static uint8 t696() {
	return button == 5 && run == 1;
}

static uint8 t838() {
	return button == 4 && run == 1;
}

static uint8 t654() {
	return button == 3 && run == 1;
}

static uint8 t160() {
	return button == 2 && run == 1;
}

static uint8 t895() {
	return button == 1 && run == 1;
}

static uint8 t477() {
	return run == 0;
}

static uint8 t522() {
	return cycles == 84000;
}

static uint8 t249() {
	return run == 1;
}

static uint8 t462() {
	return run == 1;
}

static uint8 t660() {
	return button ==4 && x==1;
}

static uint8 t490() {
	return run == 1;
}

static uint8 STM_IMPLEMENTATION() {
	switch (st) {
		case Program4:
			if (t462()) {
				st=60deg_Water;
			}
			break;
		case 60deg_Water:
			if (t419()) {
				st=1600RPM;
			}
			if (t660()) {
				st=1400RPM;
			}
			break;
		case 40deg_Water:
			if (t831()) {
				st=1200RPM;
			}
			if (t175()) {
				st=1400RPM;
			}
			break;
		case Program1:
			if (t249()) {
				st=40deg_Water;
			}
			break;
		case 50deg_Water:
			if (t251()) {
				st=1400RPM;
			}
			break;
		case 1600RPM:
			if (t307()) {
				st=FINISHED;
			}
			break;
		case Program3:
			if (t769()) {
				st=50deg_Water;
			}
			break;
		case Program2:
			if (t490()) {
				st=40deg_Water;
			}
			break;
		case 1200RPM:
			if (t704()) {
				st=FINISHED;
			}
			break;
		case FINISHED:
			if (t654()) {
				st=Display_Hour;
			}
			break;
		case Idle:
			if (t559()) {
				st=Display_Hour;
			}
			if (t696()) {
				st=Program5;
			}
			if (t838()) {
				st=Program4;
			}
			if (t654()) {
				st=Program3;
			}
			if (t160()) {
				st=Program2;
			}
			if (t895()) {
				st=Program1;
			}
			break;
		case Display_Hour:
			if (t477()) {
				st=Idle;
			}
			break;
		case Program5:
			if (t219()) {
				st=60deg_Water;
			}
			break;
		case 1400RPM:
			if (t522()) {
				st=FINISHED;
			}
			break;
	}
}

int main() {
	return 0;
}