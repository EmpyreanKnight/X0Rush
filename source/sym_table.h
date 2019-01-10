#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TRUE  1
#define FALSE 0

typedef enum _SYM_TYPE {
    vacuum,
    boolean,
    character,
    integer,
    function
} SYM_TYPE;

typedef struct {
    char* id;
    SYM_TYPE type;
    int addr;    // for const is value, for array is base address
    int size;    // not for constants
    int level;   // not for constants

    int isConst; // specially for constant
    int isArray; // for arrays
    int* dims;   // for arrays
    int ndim;    // for arrays

    int argc;          // specially for functions
    SYM_TYPE ret_type; // specially for functions
} SYM_ENTRY;

SYM_ENTRY* sym_table;
int sym_top;
int sym_global_tail;

void sym_create(int size);
void sym_destroy();
void sym_enter(char* id, SYM_TYPE type, int level);
void sym_enter_const(char* id, SYM_TYPE type, int val);
void sym_enter_array(char* id, SYM_TYPE type, int level, int* dims, int ndim, int size);
int sym_position(char* id);
int sym_position_func(char* id);
void sym_set_index();
void sym_output(FILE* out);