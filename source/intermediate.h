#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum INTER_OP {
    lit,     opr,     lod, 
    sto,     cal,     ini, 
    jmp,     jpc,     par
};

typedef struct {
    enum INTER_OP op;
    int l;
    int a;
} INTER_INST;

INTER_INST* inter_table;
int inter_top;
int inter_size;
int inter_level;

void inter_create(int size);
void inter_gen(enum INTER_OP op, int l, int a);
void inter_display(FILE* out);
void inter_destroy();
