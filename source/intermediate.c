#include "intermediate.h"

void inter_create(int size) {
    inter_size = size;
    inter_top = 0;
    inter_level = 0;
    inter_table = malloc(sizeof(INTER_INST)*size);
}

void inter_gen(enum INTER_OP op, int l, int a) {
    if (inter_top >= inter_size) {
        fprintf(stderr, "Error: program length exceeded!\n");
        exit(-1);
    }
    inter_table[inter_top].op = op;
    inter_table[inter_top].l = l;
    inter_table[inter_top].a = a;
    inter_top++;
}

void inter_display(FILE* out) {
	char name[][4]=	{
		{"lit"}, {"opr"}, {"lod"},
        {"sto"}, {"cal"}, {"ini"},
        {"jmp"}, {"jpc"},
	};
    for (int i = 0; i < inter_top; i++) {
        fprintf(out, "%d\t%s  %d\t%d\n", i, 
        name[inter_table[i].op], inter_table[i].l, inter_table[i].a);
    }
}

void inter_destroy() {
    free(inter_table);
}