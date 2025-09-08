#include "vidpipe.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>

typedef struct {
    const char* input;
    size_t pos;
    int line;
    int column;
    Token* tokens;
    int token_count;
    int token_capacity;
} Lexer;

static Lexer* lexer_create(const char* input) {
    Lexer* lex = malloc(sizeof(Lexer));
    lex->input = input;
    lex->pos = 0;
    lex->line = 1;
    lex->column = 1;
    lex->token_capacity = 32;
    lex->token_count = 0;
    lex->tokens = malloc(sizeof(Token) * lex->token_capacity);
    return lex;
}

static char peek(Lexer* lex) {
    if (lex->pos >= strlen(lex->input)) return '\0';
    return lex->input[lex->pos];
}

static char peek_next(Lexer* lex) {
    if (lex->pos + 1 >= strlen(lex->input)) return '\0';
    return lex->input[lex->pos + 1];
}

static char advance(Lexer* lex) {
    char c = peek(lex);
    if (c != '\0') {
        lex->pos++;
        if (c == '\n') {
            lex->line++;
            lex->column = 1;
        } else {
            lex->column++;
        }
    }
    return c;
}

static void skip_whitespace(Lexer* lex) {
    while (isspace(peek(lex))) {
        advance(lex);
    }
}

static void add_token(Lexer* lex, TokenType type, const char* value) {
    if (lex->token_count >= lex->token_capacity) {
        lex->token_capacity *= 2;
        lex->tokens = realloc(lex->tokens, sizeof(Token) * lex->token_capacity);
    }
    
    Token* token = &lex->tokens[lex->token_count++];
    token->type = type;
    token->value = value ? strdup(value) : NULL;
    token->line = lex->line;
    token->column = lex->column;
}

static void lex_identifier(Lexer* lex) {
    int start = lex->pos;
    
    while (isalnum(peek(lex)) || peek(lex) == '-' || peek(lex) == '_') {
        advance(lex);
    }
    
    int length = lex->pos - start;
    char* value = malloc(length + 1);
    strncpy(value, lex->input + start, length);
    value[length] = '\0';
    
    add_token(lex, TOKEN_IDENTIFIER, value);
    free(value);
}

static void lex_number(Lexer* lex) {
    int start = lex->pos;
    
    while (isdigit(peek(lex))) {
        advance(lex);
    }
    
    int length = lex->pos - start;
    char* value = malloc(length + 1);
    strncpy(value, lex->input + start, length);
    value[length] = '\0';
    
    add_token(lex, TOKEN_NUMBER, value);
    free(value);
}

Token* lex(const char* input) {
    Lexer* lex = lexer_create(input);
    
    while (peek(lex) != '\0') {
        skip_whitespace(lex);
        
        if (peek(lex) == '\0') break;
        
        char c = peek(lex);
        char next = peek_next(lex);
        
        // Multi-character operators
        if (c == '-' && next == '>') {
            advance(lex);
            advance(lex);
            add_token(lex, TOKEN_ARROW, "->");
        }
        else if (c == '~' && next == '>') {
            advance(lex);
            advance(lex);
            add_token(lex, TOKEN_ASYNC_ARROW, "~>");
        }
        else if (c == '=' && next == '>') {
            advance(lex);
            advance(lex);
            add_token(lex, TOKEN_SYNC_ARROW, "=>");
        }
        else if (c == '&' && next == '>') {
            advance(lex);
            advance(lex);
            add_token(lex, TOKEN_PARALLEL, "&>");
        }
        else if (c == '+' && next == '>') {
            advance(lex);
            advance(lex);
            add_token(lex, TOKEN_MERGE, "+>");
        }
        // Single character tokens
        else if (c == '|') {
            advance(lex);
            add_token(lex, TOKEN_CHOICE, "|");
        }
        else if (c == '[') {
            advance(lex);
            add_token(lex, TOKEN_BUFFER_START, "[");
        }
        else if (c == ']') {
            advance(lex);
            add_token(lex, TOKEN_BUFFER_END, "]");
        }
        else if (c == '{') {
            advance(lex);
            add_token(lex, TOKEN_LOOP_START, "{");
        }
        else if (c == '}') {
            advance(lex);
            add_token(lex, TOKEN_LOOP_END, "}");
        }
        else if (c == '(') {
            advance(lex);
            add_token(lex, TOKEN_LPAREN, "(");
        }
        else if (c == ')') {
            advance(lex);
            add_token(lex, TOKEN_RPAREN, ")");
        }
        else if (c == ',') {
            advance(lex);
            add_token(lex, TOKEN_COMMA, ",");
        }
        // Numbers
        else if (isdigit(c)) {
            lex_number(lex);
        }
        // Identifiers
        else if (isalpha(c) || c == '_') {
            lex_identifier(lex);
        }
        // Comments
        else if (c == '#') {
            while (peek(lex) != '\n' && peek(lex) != '\0') {
                advance(lex);
            }
        }
        else {
            fprintf(stderr, "Unexpected character '%c' at line %d, column %d\n", 
                    c, lex->line, lex->column);
            advance(lex);
            add_token(lex, TOKEN_ERROR, NULL);
        }
    }
    
    add_token(lex, TOKEN_EOF, NULL);
    
    Token* result = lex->tokens;
    free(lex);
    return result;
}

void free_tokens(Token* tokens) {
    if (!tokens) return;
    
    for (int i = 0; tokens[i].type != TOKEN_EOF; i++) {
        if (tokens[i].value) {
            free(tokens[i].value);
        }
    }
    free(tokens);
}