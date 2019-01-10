#include "sym_table.h"

void sym_create(int size) {
    sym_table = malloc(sizeof(SYM_ENTRY)*size);
    sym_top = 0;
    sym_global_tail = -1;
}

void sym_destroy() {
    for (int i = 1; i <= sym_top; i++) {
        if (sym_table[i].isArray) {
            free(sym_table[i].dims);
        }
        free(sym_table[i].id);
    }
    free(sym_table);
}

void sym_enter_base(char* id, SYM_TYPE type) {
    sym_top++;
    // default values
    sym_table[sym_top].id = id;
    sym_table[sym_top].type = type;
    sym_table[sym_top].isArray = FALSE;
    sym_table[sym_top].isConst = FALSE;
    sym_table[sym_top].size = 0;

    // for error check
    sym_table[sym_top].addr = -1551;
}

void sym_enter(char* id, SYM_TYPE type, int level) {
    sym_enter_base(id, type);
    sym_table[sym_top].size = 1;
    sym_table[sym_top].level = level;
}

void sym_enter_const(char* id, SYM_TYPE type, int val) {
    sym_enter_base(id, type);
    if (type == boolean) {
        sym_table[sym_top].addr = val == 0 ? 0 : 1;
    } else {
        sym_table[sym_top].addr = val;
    }
    sym_table[sym_top].isConst = TRUE;
}

void sym_enter_array(char* id, SYM_TYPE type, int level, int* dims, int ndim, int size) {
    sym_enter_base(id, type);
    sym_table[sym_top].level = level;
    sym_table[sym_top].ndim = ndim;
    sym_table[sym_top].dims = dims;
    sym_table[sym_top].size = size;
    sym_table[sym_top].isArray = TRUE;
}

int sym_position(char* id) {
    int pos = sym_top;
    // search for locals
    while (pos > 0 && sym_table[pos].type != function) {
        if (strcmp(sym_table[pos].id, id) == 0) {
            break;
        }
        pos--;
    }

    // search for globals
    if (sym_table[pos].type == function) {
        pos = sym_global_tail;
        while (pos > 0) {
            if (strcmp(sym_table[pos].id, id) == 0) {
                break;
            }
            pos--;
        }
    }

    return pos;
}

int sym_position_func(char* id) {
    int pos = sym_top;
    while (pos > 0) {
        if (strcmp(sym_table[pos].id, id) == 0) {
            break;
        }
        pos--;
    }
    return pos;
}

void sym_set_index() {
    int pos = sym_top;
    while (pos > 0 && sym_table[pos].type != function) {
        pos--;
    }
    
    int index = sym_global_tail == -1 ? 0 : 3;
    for (int i = pos + 1; i <= sym_top; i++) {
        if (!sym_table[i].isConst) {
            sym_table[i].addr = index;
            index += sym_table[i].size;
        }
    }
}

void sym_output(FILE* out) {
    char name[][5] = {
        "void", "bool", "char", "int", "func"
    };
    for (int i = 1; i <= sym_top; i++) {
        fprintf(out, "%s %s %s %d %d %d ",
        sym_table[i].id, name[sym_table[i].type],
        sym_table[i].isConst ? "const" : (sym_table[i].isArray ? "array" : "n/a"),
        sym_table[i].addr, sym_table[i].size, sym_table[i].level);
        if (sym_table[i].isArray) {
            fprintf(out, "dims=[");
            for (int j = 0; j < sym_table[i].ndim; j++) {
                fprintf(out, "%d%c", sym_table[i].dims[j],
                j == sym_table[i].ndim-1 ? ']' : ',');
            }
        } else if (sym_table[i].type == function) {
            fprintf(out, "argc=%d,ret_type=%s", sym_table[i].argc,
            name[sym_table[i].ret_type]);
        } else {
            fprintf(out, "n/a");
        }
        fprintf(out, "\n");
    };
}
