#include "vidpipe.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

typedef struct {
    Token* tokens;
    int pos;
} Parser;

static Parser* parser_create(Token* tokens) {
    Parser* parser = malloc(sizeof(Parser));
    parser->tokens = tokens;
    parser->pos = 0;
    return parser;
}

static void parser_destroy(Parser* parser) {
    free(parser);
}

static Token* current(Parser* parser) {
    return &parser->tokens[parser->pos];
}

static Token* advance(Parser* parser) {
    if (current(parser)->type != TOKEN_EOF) {
        parser->pos++;
    }
    return current(parser);
}

static bool check(Parser* parser, TokenType type) {
    return current(parser)->type == type;
}

static bool match(Parser* parser, TokenType type) {
    if (check(parser, type)) {
        advance(parser);
        return true;
    }
    return false;
}

static ASTNode* node_create(NodeType type) {
    ASTNode* node = malloc(sizeof(ASTNode));
    node->type = type;
    node->name = NULL;
    node->conn_type = CONN_SYNC;
    node->buffer_size = 0;
    node->child_capacity = 2;
    node->child_count = 0;
    node->children = malloc(sizeof(ASTNode*) * node->child_capacity);
    return node;
}

static void node_add_child(ASTNode* parent, ASTNode* child) {
    if (parent->child_count >= parent->child_capacity) {
        parent->child_capacity *= 2;
        parent->children = realloc(parent->children, 
                                  sizeof(ASTNode*) * parent->child_capacity);
    }
    parent->children[parent->child_count++] = child;
}

static ASTNode* parse_function(Parser* parser);
static ASTNode* parse_pipeline_element(Parser* parser);
static ASTNode* parse_parallel(Parser* parser);
static ASTNode* parse_expression(Parser* parser);

static ASTNode* parse_function(Parser* parser) {
    if (!check(parser, TOKEN_IDENTIFIER)) {
        fprintf(stderr, "Expected function name at line %d\n", 
                current(parser)->line);
        return NULL;
    }
    
    ASTNode* node = node_create(NODE_FUNCTION);
    node->name = strdup(current(parser)->value);
    advance(parser);
    
    return node;
}

static bool has_connection_token(Parser* parser) {
    return check(parser, TOKEN_ARROW) || 
           check(parser, TOKEN_ASYNC_ARROW) ||
           check(parser, TOKEN_SYNC_ARROW) ||
           check(parser, TOKEN_BUFFER_START);
}

static ConnectionType parse_connection_type(Parser* parser, int* buffer_size) {
    *buffer_size = 0;
    
    // Check for buffered connection [n]->
    if (match(parser, TOKEN_BUFFER_START)) {
        if (check(parser, TOKEN_NUMBER)) {
            *buffer_size = atoi(current(parser)->value);
            advance(parser);
        } else {
            *buffer_size = 10; // Default buffer size
        }
        
        if (!match(parser, TOKEN_BUFFER_END)) {
            fprintf(stderr, "Expected ']' after buffer size\n");
        }
        
        // After buffer, must have an arrow
        if (match(parser, TOKEN_ARROW)) {
            return CONN_BUFFERED;
        } else if (match(parser, TOKEN_ASYNC_ARROW)) {
            return CONN_ASYNC;
        } else if (match(parser, TOKEN_SYNC_ARROW)) {
            return CONN_SYNC;
        }
    }
    
    // Regular arrows
    if (match(parser, TOKEN_ASYNC_ARROW)) {
        return CONN_ASYNC;
    } else if (match(parser, TOKEN_SYNC_ARROW)) {
        return CONN_SYNC;
    } else if (match(parser, TOKEN_ARROW)) {
        return CONN_SYNC;
    }
    
    return CONN_SYNC;
}

static ASTNode* parse_parallel(Parser* parser) {
    ASTNode* left = parse_function(parser);
    if (!left) return NULL;
    
    // Check for parallel branches
    if (check(parser, TOKEN_PARALLEL)) {
        ASTNode* parallel = node_create(NODE_PARALLEL);
        node_add_child(parallel, left);
        
        while (match(parser, TOKEN_PARALLEL)) {
            ASTNode* branch = parse_function(parser);
            if (!branch) {
                free_ast(parallel);
                return NULL;
            }
            node_add_child(parallel, branch);
        }
        
        return parallel;
    }
    
    // Check for choice operator
    if (check(parser, TOKEN_CHOICE)) {
        ASTNode* choice = node_create(NODE_CHOICE);
        node_add_child(choice, left);
        
        while (match(parser, TOKEN_CHOICE)) {
            ASTNode* branch = parse_function(parser);
            if (!branch) {
                free_ast(choice);
                return NULL;
            }
            node_add_child(choice, branch);
        }
        
        return choice;
    }
    
    return left;
}

static ASTNode* parse_pipeline_element(Parser* parser) {
    ASTNode* element = NULL;
    
    // Handle loop expressions
    if (match(parser, TOKEN_LOOP_START)) {
        ASTNode* loop = node_create(NODE_LOOP);
        
        // Parse the loop body
        ASTNode* body = parse_expression(parser);
        if (!body) {
            free_ast(loop);
            return NULL;
        }
        node_add_child(loop, body);
        
        if (!match(parser, TOKEN_LOOP_END)) {
            fprintf(stderr, "Expected '}' at line %d\n", current(parser)->line);
            free_ast(loop);
            return NULL;
        }
        element = loop;
    }
    // Handle parenthesized expressions
    else if (match(parser, TOKEN_LPAREN)) {
        element = parse_expression(parser);
        if (!match(parser, TOKEN_RPAREN)) {
            fprintf(stderr, "Expected ')' at line %d\n", current(parser)->line);
            if (element) free_ast(element);
            return NULL;
        }
    } else {
        element = parse_parallel(parser);
    }
    
    return element;
}

static ASTNode* parse_expression(Parser* parser) {
    ASTNode* left = parse_pipeline_element(parser);
    if (!left) return NULL;
    
    // Check for merge operator
    if (match(parser, TOKEN_MERGE)) {
        ASTNode* merge = node_create(NODE_MERGE);
        node_add_child(merge, left);
        
        // Parse what comes after merge
        ASTNode* right = parse_expression(parser);
        if (!right) {
            free_ast(merge);
            return NULL;
        }
        node_add_child(merge, right);
        return merge;
    }
    
    // Check for pipeline continuation
    if (has_connection_token(parser)) {
        int buffer_size = 0;
        ConnectionType conn = parse_connection_type(parser, &buffer_size);
        
        ASTNode* pipeline = node_create(NODE_PIPELINE);
        pipeline->conn_type = conn;
        pipeline->buffer_size = buffer_size;
        node_add_child(pipeline, left);
        
        // Parse the rest of the pipeline
        ASTNode* right = parse_expression(parser);
        if (!right) {
            free_ast(pipeline);
            return NULL;
        }
        node_add_child(pipeline, right);
        return pipeline;
    }
    
    return left;
}

ASTNode* parse(Token* tokens) {
    Parser* parser = parser_create(tokens);
    ASTNode* ast = parse_expression(parser);
    
    if (!check(parser, TOKEN_EOF)) {
        fprintf(stderr, "Unexpected token at line %d: %s\n", 
                current(parser)->line, 
                current(parser)->value ? current(parser)->value : "");
        if (ast) free_ast(ast);
        ast = NULL;
    }
    
    parser_destroy(parser);
    return ast;
}

void free_ast(ASTNode* node) {
    if (!node) return;
    
    if (node->name) free(node->name);
    
    for (int i = 0; i < node->child_count; i++) {
        free_ast(node->children[i]);
    }
    
    free(node->children);
    free(node);
}

void print_ast(ASTNode* node, int depth) {
    if (!node) return;
    
    for (int i = 0; i < depth; i++) printf("  ");
    
    switch (node->type) {
        case NODE_FUNCTION:
            printf("Function: %s\n", node->name);
            break;
        case NODE_PIPELINE:
            printf("Pipeline (");
            if (node->conn_type == CONN_ASYNC) printf("async");
            else if (node->conn_type == CONN_BUFFERED) 
                printf("buffer=%d", node->buffer_size);
            else printf("sync");
            printf(")\n");
            break;
        case NODE_PARALLEL:
            printf("Parallel\n");
            break;
        case NODE_MERGE:
            printf("Merge\n");
            break;
        case NODE_CHOICE:
            printf("Choice\n");
            break;
        case NODE_BUFFER:
            printf("Buffer (size=%d)\n", node->buffer_size);
            break;
        case NODE_LOOP:
            printf("Loop\n");
            break;
    }
    
    for (int i = 0; i < node->child_count; i++) {
        print_ast(node->children[i], depth + 1);
    }
}