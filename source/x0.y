%{
#include <stdio.h>
#include <stdlib.h>
#include "intermediate.h"
#include "sym_table.h"

extern FILE *yyin;
extern int yylineno;
extern int yytext;

int type_casting(SYM_TYPE lhs, SYM_TYPE rhs);
int type_conversion(SYM_TYPE a, SYM_TYPE b);
void backpatch_link(int addr, int list);
int merge_link(int addr, int list);
void fetch_value(int sym);
void save_value(int sym);

int inSwitch;
int current_func;
int loop_depth;
int dimensions[100];
%}

%union {
    char* id;
    int int_val;
    int type_val;
    struct { int back_list, forward_list; } lists;
    struct { int sym, dim; } arr;
    struct { int type, sym; } exp;
    struct { int type, value; } lit;
}

%token <id> ID STRING
%token <int_val> NUM ASCII BOOL_VAL
%token INT CHAR BOOL VOID CONST
%token MAIN
%token IF ELSE
%token WHILE DO SWITCH CASE FOR REPEAT UNTIL DEFAULT
%token READ WRITE
%token CONTINUE BREAK EXIT RET
%token NOT INCRE DECRE ODD

%right ASGN
%left OR
%left AND
%left EQ NE '^'
%left LE GE LT GT
%left '+' '-'
%left '*' '/' '%'

%nonassoc LOWER_THAN_ELSE 
%nonassoc ELSE

%type <int_val> arguments argument_list // argc
%type <int_val> func_name call_func var // sym entry index
%type <int_val> declaration_list variable_seq // count of variable size
%type <int_val> declare_subscripts // dims of array
%type <int_val> gen_jmp gen_jpc continue_stat break_stat gen_case_jpc get_inter_addr // inter index
%type <int_val> default_stat case_list case_stat  // forward list

%type <type_val> ret_type type expression condition additive_boolean_expr boolean_expr 
%type <type_val> simple_expr additive_expr term factor read_expr
%type <exp> unary_expr // sym and type

%type <lists> statement_list statement compound_stat if_stat // lists for backpatch
%type <arr> exp_subscripts call_func_head // sym and dims
%type <lit> literal // sym and value

%%

program: {
    inter_gen(ini, 0, 0);
    inter_gen(cal, -1, 0);
    inter_top = 2;
} global_decls {
    sym_global_tail = sym_top;
} function_list {
    if (inter_table[1].a == 0) {
        yyerror("Main function not found");
    }
}
;

global_decls: /* empty */
| '{' declaration_list '}'
;

function_list: /* empty */
| function function_list
;

function: ret_type func_name arguments '{' declaration_list {
    sym_table[$2].argc = $3;
    sym_table[$2].size = $3 + $5 + 3;
    sym_table[$2].ret_type = $1;
    inter_gen(ini, 0, sym_table[$2].size);
}
statement_list '}' {
    inter_gen(opr, $1, 0);
    inter_level--;
}
;

ret_type: /* empty */ { $$ = vacuum; }
| VOID { $$ = vacuum; }
| CHAR { $$ = character; }
| BOOL { $$ = boolean; }
| INT { $$ = integer; }
;

arguments: /* empty */ { $$ = 0; }
| '(' ')' { $$ = 0; }
| '(' argument argument_list ')' { $$ = $3 + 1; }
;

argument_list: /* empty */ { $$ = 0; }
| ',' argument argument_list { $$ = $3 + 1; }
;

argument: type ID {
    if (sym_position($2) == 0) {
        sym_enter($2, $1, inter_level);
    } else {
        yyerror("Duplicate identifier");
    }
}
;

func_name: ID {
    if (sym_position_func($1) == 0) {
        sym_enter($1, function, inter_level);
        $$ = sym_top;
    } else {
        yyerror("Duplicate identifier");
        $$ = 0;
    }
    sym_table[sym_top].addr = inter_top;
    current_func = sym_top;
    inter_level++;
}
| MAIN {
    if (sym_position_func("main") == 0) {
        sym_enter("main", function, inter_level);
        $$ = sym_top;
    } else {
        yyerror("Duplicate identifier");
        $$ = 0;
    }
    sym_table[sym_top].addr = inter_top;
    current_func = sym_top;
    inter_level++;

    int size = 0;
    for (int i = 1; i <= sym_global_tail; i++) {
        size += sym_table[i].size;
    }
    inter_table[0].a = size;
    inter_table[1].a = inter_top;
}
;

declaration_list: /* empty */ { 
    $$ = 0;
    sym_set_index(); 
}
| variable_seq ';' declaration_list { 
    $$ = $1 + $3;
}
| const_seq ';' declaration_list {
    $$ = $3;
}
;

const_seq: CONST type ID ASGN literal {
    if (sym_position($3) != 0) {
        yyerror("Duplicate identifier");
    }
    type_casting($2, $5.type);
    sym_enter_const($3, $2, $5.value);
}
| const_seq ',' ID ASGN literal {
    if (sym_position($3) != 0) {
        yyerror("Duplicate identifier");
    }
    type_casting(sym_table[sym_top].type, $5.type);
    sym_enter_const($3, sym_table[sym_top].type, $5.value);
}
;

variable_seq: type ID declare_subscripts { 
    if (sym_position($2) != 0) {
        yyerror("Duplicate identifier");
    }
    $$ = 1;
    if ($3 == 0) {
        sym_enter($2, $1, inter_level);
    } else if ($3 >= 100) {
        yyerror("Unable to handle an array with over 100 dimensions");
    } else {
        int* dims = malloc(sizeof(int)*$3);
        for (int i = 0; i < $3; i++) {
            dims[i] = dimensions[$3 - i - 1];
            $$ = $$ * dimensions[i];
        }
        sym_enter_array($2, $1, inter_level, dims, $3, $$);
    }
}
| variable_seq ',' ID declare_subscripts { 
    if (sym_position($3) != 0) {
        yyerror("Duplicate identifier");
    }
    $$ = 1;
    if ($4 == 0) {
        sym_enter($3, sym_table[sym_top].type, inter_level);
    } else if ($4 >= 100) {
        yyerror("Unable to handle an array with over 100 dimensions");
    } else {
        int* dims = malloc(sizeof(int)*$4);
        for (int i = 0; i < $4; i++) {
            dims[i] = dimensions[$4 - i - 1];
            $$ = $$ * dimensions[i];
        }
        sym_enter_array($3, sym_table[sym_top].type, inter_level, dims, $4, $$);
    }
    $$ += $1;
}
;

declare_subscripts: /* empty */ {
    $$ = 0;
}
| '[' NUM ']' declare_subscripts {
    if ($2 < 0) {
        yyerror("Fetch array size from a non-positive literal number");
        dimensions[$4] = 1;
    } else {
        if ($4 < 100) {
            dimensions[$4] = $2;
        }
    }
    $$ = $4 + 1;
}
| '[' var ']' declare_subscripts {
    if (sym_table[$2].isConst && sym_table[$2].addr > 0) {
        if ($4 < 100) {
            dimensions[$4] = sym_table[$2].addr;
        }
    } else {
        yyerror("Fetch array size from a non-constant or non-positive variable");
        dimensions[$4] = 1;
    }
    $$ = $4 + 1;
}
;

statement_list: /* empty */ {
    $$.back_list = 0;
    $$.forward_list = 0;
}
| statement statement_list {
    $$.back_list = merge_link($1.back_list, $2.back_list);
    $$.forward_list = merge_link($1.forward_list, $2.forward_list);
}
;

statement: if_stat {
    $$.back_list = $1.back_list;
    $$.forward_list = $1.forward_list;
}
| write_stat {
    $$.back_list = 0;
    $$.forward_list = 0;
}
| compound_stat {
    $$.back_list = $1.back_list;
    $$.forward_list = $1.forward_list;
}
| expression_stat {
    $$.back_list = 0;
    $$.forward_list = 0;
}
| while_stat {
    $$.back_list = 0;
    $$.forward_list = 0;
}
| switch_stat {
    $$.back_list = 0;
    $$.forward_list = 0;
}
| for_stat {
    $$.back_list = 0;
    $$.forward_list = 0;
}
| do_while_stat {
    $$.back_list = 0;
    $$.forward_list = 0;
}
| repeat_stat {
    $$.back_list = 0;
    $$.forward_list = 0;
}
| break_stat {
    $$.back_list = 0;
    $$.forward_list = $1;
}
| continue_stat {
    $$.back_list = $1;
    $$.forward_list = 0;
}
| exit_stat {
    $$.back_list = 0;
    $$.forward_list = 0;
}
| return_stat {
    $$.back_list = 0;
    $$.forward_list = 0;
}
;

if_stat: IF '(' expression ')' gen_jpc 
statement %prec LOWER_THAN_ELSE {
    inter_table[$5].a = inter_top;
    $$.forward_list = $6.forward_list;
    $$.back_list = $6.back_list;
}
| IF '(' expression ')' gen_jpc 
statement ELSE gen_jmp statement { 
    inter_table[$5].a = $8 + 1;
    inter_table[$8].a = inter_top;
    $$.forward_list = merge_link($6.forward_list, $9.forward_list);
    $$.back_list = merge_link($6.back_list, $9.back_list);
}
;

while_stat: WHILE get_inter_addr '(' expression ')' 
incre_depth gen_jpc statement {
    inter_gen(jmp, 0, $2);
    inter_table[$7].a = inter_top;
    backpatch_link($8.forward_list, inter_top);
    backpatch_link($8.back_list, $2);
    loop_depth--;
}
;

switch_stat: SWITCH '(' expression ')' '{' {
    inSwitch++;
} case_list '}' {
    backpatch_link($7, inter_top);
    inter_gen(opr, 0, 22);
    inSwitch--;
}
;

case_list: default_stat {
    $$ = $1;
}
| case_stat case_list {
    $$ = merge_link($1, $2);
}
;

default_stat: /* empty */ {
    $$ = 0;
}
| DEFAULT ':' statement_list {
    $$ = $3.forward_list;
}
;

case_stat: CASE literal { inter_gen(lit, 0, $2.value); } gen_case_jpc ':' 
statement_list {
    $$ = $6.forward_list;
    inter_table[$4].a = inter_top;
}
;

gen_case_jpc: {
    inter_gen(opr, 0, 21);
    $$ = inter_top;
    inter_gen(jpc, 0, 0);
}
;

for_stat: FOR '(' expression_stat get_inter_addr for_cond_stat 
gen_jpc gen_jmp expression { inter_gen(opr, 0, 22); } gen_jmp 
')' get_inter_addr incre_depth statement {
    inter_gen(jmp, 0, $7 + 1);
    inter_table[$6].a = inter_top;
    inter_table[$7].a = $12;
    inter_table[$10].a = $4;
    backpatch_link($14.forward_list, inter_top);
    backpatch_link($14.back_list, $7 + 1);
    loop_depth--;
}
| FOR '(' expression_stat get_inter_addr for_cond_stat
 gen_jpc ')' incre_depth statement {
    inter_gen(jmp, 0, $4);
    inter_table[$6].a = inter_top;
    backpatch_link($9.forward_list, inter_top);
    backpatch_link($9.back_list, $4);
}
;

for_cond_stat: ';' {
    inter_gen(lit, 0, 1);
}
| expression ';'
;

do_while_stat: DO get_inter_addr incre_depth statement WHILE 
'(' expression gen_jpc gen_jmp ')' ';' {
    inter_table[$8].a = inter_top;
    inter_table[$9].a = $2;
    backpatch_link($4.forward_list, inter_top);
    backpatch_link($4.back_list, $2);
}
;

repeat_stat: REPEAT get_inter_addr incre_depth statement UNTIL 
'(' expression gen_jpc ')' ';' {
    inter_table[$8].a = $2;
    backpatch_link($4.forward_list, inter_top);
    backpatch_link($4.back_list, $2);
}
;

continue_stat: CONTINUE ';' {
    if (loop_depth <= 0) {
        yyerror("Continue statement outside of loops");
        $$ = 0;
    } else {
        $$ = inter_top;
        inter_gen(jmp, 0, 0);
    }
}
;

break_stat: BREAK ';' {
    if (loop_depth <= 0 && inSwitch <= 0) {
        yyerror("Break statement outside of loops or switch");
        $$ = 0;
    } else {
        $$ = inter_top;
        inter_gen(jmp, 0, 0);
    }
}
;

write_stat: WRITE expression ';' {
    inter_gen(opr, $2, 14);
}
| WRITE STRING ';' {
    for (int i = 1; i < strlen($2) - 1; i++) {
        inter_gen(lit, 0, $2[i]);
        inter_gen(opr, character, 14);
    }
}
| WRITE ';' {
    inter_gen(opr, 0, 15);
}
;

exit_stat: EXIT ';' {
    inter_gen(jmp, 0, 0);
}
;

compound_stat: '{' statement_list '}' {
    $$.back_list = $2.back_list;
    $$.forward_list = $2.forward_list;
}
;

expression_stat: expression ';' {
    if ($1 != vacuum) {
        inter_gen(opr, 0, 22);
    }
}
| ';'
;

return_stat: RET ';' {
    if (sym_table[current_func].ret_type == vacuum) {
        inter_gen(opr, 0, 0);
    } else {
        yyerror("Return nothing in a non-void function");
    }
}
| RET expression ';' {
    if (sym_table[current_func].ret_type == vacuum) {
        yyerror("Return a value in a void function");
    } else {
        type_casting(sym_table[current_func].ret_type, $2);
        inter_gen(opr, sym_table[current_func].ret_type, 0);
    }
}
;

expression: var ASGN expression {
    $$ = sym_table[$1].type;
    type_casting($$, $3);
    if ($$ == 1) {
        inter_gen(opr, 1, 25);
    }
    save_value($1);
}
| condition { $$ = $1; }
;

condition: additive_boolean_expr { $$ = $1; }
| condition OR additive_boolean_expr { 
    $$ = boolean;
    inter_gen(opr, 0, 19); 
}
;

additive_boolean_expr: boolean_expr { $$ = $1; }
| additive_boolean_expr AND boolean_expr { 
    $$ = boolean;
    inter_gen(opr, 0, 18); 
}
;

boolean_expr: simple_expr { $$ = $1; }
| boolean_expr EQ simple_expr { 
    $$ = boolean;
    inter_gen(opr, 0, 8); 
}
| boolean_expr NE simple_expr { 
    $$ = boolean;
    inter_gen(opr, 0, 9); 
}
| boolean_expr '^' simple_expr { 
    $$ = boolean;
    inter_gen(opr, 0, 20); 
}
;

simple_expr: additive_expr { $$ = $1; }
| simple_expr LT additive_expr { 
    $$ = boolean;
    inter_gen(opr, 0, 10); 
}
| simple_expr GE additive_expr { 
    $$ = boolean;
    inter_gen(opr, 0, 11); 
}
| simple_expr LE additive_expr { 
    $$ = boolean;
    inter_gen(opr, 0, 12); 
}
| simple_expr GT additive_expr { 
    $$ = boolean;
    inter_gen(opr, 0, 13); 
}
;

additive_expr: term { $$ = $1; }
| additive_expr '+' term {
    $$ = type_conversion($1, $3);
    inter_gen(opr, 0, 2);
}
| additive_expr '-' term {
    $$ = type_conversion($1, $3);
    inter_gen(opr, 0, 3);
}
;

term: factor { $$ = $1; }
| term '*' factor {
    $$ = type_conversion($1, $3);
    inter_gen(opr, 0, 4);
}
| term '/' factor {
    $$ = type_conversion($1, $3);
    inter_gen(opr, 0, 5);
}
| term '%' factor {
    $$ = type_conversion($1, $3);
    inter_gen(opr, 0, 7);
}
;

factor: unary_expr { $$ = $1.type; }
| INCRE unary_expr {
    $$ = $2.type;
    if ($2.sym == -1 || sym_table[$2.sym].isConst) {
        yyerror("Not a modifiable lvalue");
    }
    inter_gen(lit, 0, 1);
    inter_gen(opr, 0, 2);
    save_value($2.sym);
}
| DECRE unary_expr {
    $$ = $2.type;
    if ($2.sym == -1 || sym_table[$2.sym].isConst) {
        yyerror("Not a modifiable lvalue");
    }
    inter_gen(lit, 0, 1);
    inter_gen(opr, 0, 3);
    save_value($2.sym);
}
| '+' unary_expr { $$ = $2.type; }
| '-' unary_expr { $$ = $2.type; inter_gen(opr, 0, 1); }
| NOT unary_expr { $$ = boolean; inter_gen(opr, 0, 17); }
| ODD unary_expr { $$ = boolean; inter_gen(opr, 0, 6); }
| '(' type ')' unary_expr { type_casting($2, $4.type); $$ = $2; }
;

unary_expr: '(' expression ')' { $$.type = $2; $$.sym = -1; }
| var {
    $$.type = sym_table[$1].type;
    $$.sym = $1;
    fetch_value($1);
}
| var INCRE {
    $$.type = type_conversion(sym_table[$1].type, integer);
    $$.sym = -1;
    if (sym_table[$1].type == function || sym_table[$1].isConst) {
        yyerror("Not a modifiable lvalue");
    }
    fetch_value($1);
    inter_gen(opr, 0, 23);
    inter_gen(lit, 0, 1);
    inter_gen(opr, 0, 2);
    save_value($1);
    inter_gen(opr, 0, 22);
}
| var DECRE {
    $$.type = type_conversion(sym_table[$1].type, integer);
    $$.sym = -1;
    if (sym_table[$1].type == function || sym_table[$1].isConst) {
        yyerror("Not a modifiable lvalue");
    }
    fetch_value($1);
    inter_gen(opr, 0, 23);
    inter_gen(lit, 0, 1);
    inter_gen(opr, 0, 3);
    save_value($1);
    inter_gen(opr, 0, 22);
}
| literal {
    $$.type = $1.type;
    $$.sym = -1;
    inter_gen(lit, 0, $1.value);
}
| call_func {
    $$.type = sym_table[$1].ret_type;
    $$.sym = -1;
}
| read_expr {
    $$.type = $1;
    $$.sym = -1;
}
;

read_expr: READ var {
    $$ = sym_table[$2].type;
    if (sym_table[$2].isConst) {
        yyerror("Write data to a constant value");
    } else {
        inter_gen(opr, sym_table[$2].type, 16);
        save_value($2);
    }
}
;

call_func: call_func_head ')' {
    $$ = $1.sym;
    if (sym_table[$$].argc != $1.dim) {
        yyerror("Argument number not correspond with the declaration of called function");
    }
    for (int i = 1; i <= $1.dim; i++) {
        inter_gen(opr, sym_table[$$+i].type, 24);
    }
    inter_gen(cal, inter_level - sym_table[$$].level, sym_table[$1.sym].addr);
}
| ID '(' ')' {
    $$ = sym_position_func($1);
    if ($$ == 0) {
        yyerror("Function has not been declared");
    } else if (sym_table[$$].type != function) {
        yyerror("Symbol should be a function");
    } else {
        inter_gen(cal, inter_level - sym_table[$$].level, sym_table[$$].addr);
    }
}
;

call_func_head: ID '(' expression {
    $$.sym = sym_position_func($1);
    $$.dim = 1;
    if ($$.sym == 0) {
        yyerror("Function has not been declared");
    } else if (sym_table[$$.sym].type != function) {
        yyerror("Symbol should be a function");
    } else if (sym_table[$$.sym].argc < 1 || type_casting(sym_table[$$.sym+1].type, $3) <= 0) {
        yyerror("Argument type not compatible with function declaration");
    }
}
| call_func_head ',' expression {
    $$.sym = $1.sym;
    $$.dim = $1.dim + 1;
    if (sym_table[$$.sym].argc < $$.dim || type_casting(sym_table[$$.sym+$$.dim].type, $3) <= 0) {
        yyerror("Argument type not compatible with function declaration");
    }
}
;

var: ID {
    $$ = sym_position($1);
    if ($$ == 0) {
        yyerror("Variable has not been declared");
    }
}
| exp_subscripts {
    if (sym_table[$1.sym].ndim != $1.dim) {
        yyerror("Subscription dimension not correct");
    }
    $$ = $1.sym;
}
;

exp_subscripts: ID '[' expression ']' {
    $$.sym = sym_position($1);
    if ($$.sym == 0) {
        yyerror("Variable does not exist");
    }
    if (!sym_table[$$.sym].isArray) {
        yyerror("Subscript operation on a non-array variable");
    }
    $$.dim = 1;
}
| exp_subscripts {
    inter_gen(lit, 0, sym_table[$1.sym].dims[$1.dim]);
    inter_gen(opr, 0, 4);
} '[' expression ']' {
    inter_gen(opr, 0, 2);
    $$.dim = $1.dim + 1;
    $$.sym = $1.sym;
}
;

literal: NUM { 
    $$.type = integer; 
    $$.value = $1; 
}
| BOOL_VAL { 
    $$.type = boolean; 
    $$.value = $1; 
}
| ASCII { 
    $$.type = character; 
    $$.value = $1; 
}
;

type: INT { $$ = integer; }
| CHAR { $$ = character; }
| BOOL { $$ = boolean; }
;

get_inter_addr: { // get the position of instruction to be executed
    $$ = inter_top;
}
;

gen_jmp: {
    $$ = inter_top;
    inter_gen(jmp, 0, 0);
}
;

gen_jpc: {
    $$ = inter_top;
    inter_gen(jpc, 0, 0);
}
;

incre_depth: {
    loop_depth++;
}
;

%%

int type_casting(SYM_TYPE lhs, SYM_TYPE rhs) {
    if (lhs == vacuum) {
        yyerror("Void type cannot act as a lvalue");
        return -1;
    }
    if (rhs == vacuum) {
        yyerror("Void type cannot act as a operand");
        return -1;
    }
    if (lhs == function || rhs == function) {
        yyerror("Function type cannot act as a operand");
        return -1;
    }
    if (lhs < rhs) {
        printf("In line %d: Warning: downward type conversion may lost precision\n", yylineno);
        return rhs;
    } else {
        return lhs;
    }
}


int type_conversion(SYM_TYPE a, SYM_TYPE b) {
    if (a == vacuum || b == vacuum) {
        yyerror("Void type cannot act as a operand");
        return 0;
    }
    if (a == function || b == function) {
        yyerror("Function type cannot act as a operand");
        return 0;
    }
    if (a < b) {
        return b;
    } else {
        return a;
    }
}

void fetch_value(int sym) {
    if (sym == 0) {
        yyerror("Variable has not been declared");
    }
    if (sym_table[sym].type == function) {
        yyerror("Function cannot act as a rvalue");
    }
    if (sym_table[sym].isConst) { // for const
        inter_gen(lit, 0, sym_table[sym].addr);
    } else if (sym_table[sym].isArray) {
        inter_gen(lod, sym_table[sym].level - inter_level - 1, sym_table[sym].addr);    
    } else { // for var
        inter_gen(lod, inter_level - sym_table[sym].level, sym_table[sym].addr);
    }
}

void save_value(int sym) {
    if (sym == 0) {
        yyerror("Variable has not been declared");
    }
    if (sym_table[sym].type == function || sym_table[sym].isConst) {
        yyerror("Not a modifiable lvalue");
    }
    if (sym_table[sym].isArray) {
        inter_gen(sto, sym_table[sym].level - inter_level - 1, sym_table[sym].addr);
    } else {
        inter_gen(sto, inter_level - sym_table[sym].level, sym_table[sym].addr);
    }
}

int merge_link(int list1, int list2) {
    if (list2 == 0) {
        return list1;
    }
    int pos = list2;
    while (inter_table[pos].a != 0) {
        pos = inter_table[pos].a;
    }
    inter_table[pos].a = list1;
    return list2;
}

void backpatch_link(int list, int addr) {
    while (list != 0) {
        int temp = inter_table[list].a;
        inter_table[list].a = addr;
        list = temp;
    }
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Error: Illegal arguments!");
        exit(-1);
    }

    FILE* outFile = fopen("inter_code", "w");
    FILE* outSym = fopen("sym_table", "w");

    sym_create(1024);                                                                                
    inter_create(4096);
    current_func = 0;
    loop_depth = 0;
    inSwitch = 0;
    yyin = fopen(argv[1], "r");
    
    if (yyin == NULL) {
        fprintf(stderr, "Error: Cannot open file!\n");
        exit(-1);
    }

    printf("Compile started...\n");
    yyparse();
    printf("Compiler finished.\n");

    inter_display(outFile);
    sym_output(outSym);
    sym_destroy();
    inter_destroy();

    fclose(outFile);

    return 0;
}

int yyerror(char *s) {
    fprintf(stderr, "In line %d: error: %s on %s\n", yylineno, s, yytext);
}
