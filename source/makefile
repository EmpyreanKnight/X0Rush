x0: x0.tab.c lex.yy.c
	gcc -o $@ x0.tab.c lex.yy.c intermediate.c sym_table.c -lfl

lex.yy.c: x0.l
	flex x0.l

x0.tab.c: x0.y
	bison -d x0.y

clean:
	del x0.tab.c
	del x0.tab.h
	del lex.yy.c
