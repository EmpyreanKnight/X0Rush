%{
    #include <string.h>
    #include <stdlib.h>
    #include "x0.tab.h"
%}

%option yylineno
%option noinput nounput noyywrap
alpha [a-zA-Z_]
digit [0-9]

%%
[ \t\n] { /* ignore whitespace */ }
[/][/].* { /* ignore line comment */ };
[/][*](.*\n)*.*[*][/] { /* ignore block comment */ };

"void" { return VOID; };
"int"  { return INT; };
"char" { return CHAR; };
"bool" { return BOOL; };

"main"  { return MAIN; };
"if"    { return IF; };
"else"  { return ELSE; };
"while" { return WHILE; };
"read"  { return READ; };
"write" { return WRITE; };

"const" { return CONST; };
"for" { return FOR; };
"do" { return DO; };
"repeat" { return REPEAT; };
"until" { return UNTIL; }
"switch" { return SWITCH; };
"case" { return CASE; };

"default" { return DEFAULT; }
"break" { return BREAK; };
"continue" { return CONTINUE; };
"exit" { return EXIT; };
"return" { return RET; };
"odd" { return ODD; };

"||" { return OR; }
"&&" { return AND; };
"!"  { return NOT; };
"++" { return INCRE; };
"--" {return DECRE; };

"true" { yylval.int_val = 1; return BOOL_VAL; }
"false" { yylval.int_val = 0; return BOOL_VAL; }

{alpha}({alpha}|{digit})* { yylval.id = strdup(yytext); return ID; };
{digit}+ { yylval.int_val = atoi(yytext); return NUM; }

"="  { return ASGN; };
"<=" { return LE; };
">=" { return GE; };
"==" { return EQ; };
"!=" { return NE; };
">"  { return GT; };
"<"  { return LT; };

['].['] { yylval.int_val = (int)yytext[1]; return ASCII; };
["].*["] { yylval.id = strdup(yytext); return STRING; };
. { return(yytext[0]); }

%%
