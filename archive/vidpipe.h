#ifndef VIDPIPE_H
#define VIDPIPE_H

#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

// Token types for lexer
typedef enum {
    TOKEN_IDENTIFIER,
    TOKEN_ARROW,          // ->
    TOKEN_ASYNC_ARROW,    // ~>
    TOKEN_SYNC_ARROW,     // =>
    TOKEN_PARALLEL,       // &>
    TOKEN_MERGE,          // +>
    TOKEN_CHOICE,         // |
    TOKEN_BUFFER_START,   // [
    TOKEN_BUFFER_END,     // ]
    TOKEN_LOOP_START,     // {
    TOKEN_LOOP_END,       // }
    TOKEN_NUMBER,
    TOKEN_LPAREN,         // (
    TOKEN_RPAREN,         // )
    TOKEN_COMMA,          // ,
    TOKEN_EOF,
    TOKEN_ERROR
} TokenType;

typedef struct {
    TokenType type;
    char* value;
    int line;
    int column;
} Token;

// AST node types
typedef enum {
    NODE_FUNCTION,
    NODE_PIPELINE,
    NODE_PARALLEL,
    NODE_MERGE,
    NODE_CHOICE,
    NODE_BUFFER,
    NODE_LOOP
} NodeType;

typedef enum {
    CONN_SYNC,
    CONN_ASYNC,
    CONN_BUFFERED
} ConnectionType;

typedef struct ASTNode {
    NodeType type;
    char* name;
    ConnectionType conn_type;
    int buffer_size;
    struct ASTNode** children;
    int child_count;
    int child_capacity;
} ASTNode;

// Frame structure for video processing
typedef struct {
    uint8_t* data;
    int width;
    int height;
    int channels;
    uint64_t timestamp;
    void* metadata;
} Frame;

// Queue for inter-function communication
typedef struct QueueNode {
    Frame* frame;
    struct QueueNode* next;
} QueueNode;

typedef struct {
    QueueNode* head;
    QueueNode* tail;
    int size;
    int max_size;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} FrameQueue;

// Function registry
typedef Frame* (*ProcessFunc)(Frame* input, void* params);

typedef struct {
    char* name;
    ProcessFunc func;
    void* params;
    bool is_source;
    bool is_sink;
} FunctionDef;

typedef struct {
    FunctionDef* functions;
    int count;
    int capacity;
} FunctionRegistry;

// Runtime execution context
typedef struct {
    ASTNode* node;
    FrameQueue* input_queue;
    FrameQueue** output_queues;
    int output_count;
    pthread_t thread;
    bool running;
    FunctionDef* function;
} ExecutionNode;

typedef struct {
    ExecutionNode** nodes;
    int node_count;
    FunctionRegistry* registry;
    bool running;
} Runtime;

// Lexer functions
Token* lex(const char* input);
void free_tokens(Token* tokens);

// Parser functions
ASTNode* parse(Token* tokens);
void free_ast(ASTNode* node);
void print_ast(ASTNode* node, int depth);

// Queue functions
FrameQueue* queue_create(int max_size);
void queue_destroy(FrameQueue* queue);
bool queue_push(FrameQueue* queue, Frame* frame);
Frame* queue_pop(FrameQueue* queue);
bool queue_is_empty(FrameQueue* queue);

// Frame functions
Frame* frame_create(int width, int height, int channels);
void frame_destroy(Frame* frame);
Frame* frame_copy(Frame* src);

// Runtime functions
Runtime* runtime_create(FunctionRegistry* registry);
void runtime_destroy(Runtime* runtime);
bool runtime_execute(Runtime* runtime, ASTNode* ast);
void runtime_stop(Runtime* runtime);

// Function registry
FunctionRegistry* registry_create();
void registry_destroy(FunctionRegistry* registry);
void registry_add(FunctionRegistry* registry, const char* name, ProcessFunc func, void* params, bool is_source, bool is_sink);
FunctionDef* registry_get(FunctionRegistry* registry, const char* name);

// Performance profiling
typedef struct {
    double frame_time;
    double processing_time;
    int frame_count;
    double fps;
    char* bottleneck_function;
} PerformanceStats;

// Advanced CV structures
typedef struct {
    int x, y, width, height;
    float confidence;
} DetectionBox;

typedef struct {
    DetectionBox* boxes;
    int count;
    int capacity;
} DetectionResult;

// Motion tracking
typedef struct {
    float x, y;
    float vx, vy;
    int age;
    int id;
} TrackedPoint;

typedef struct {
    TrackedPoint* points;
    int count;
    int capacity;
    int next_id;
} MotionTracker;

// Built-in functions
void register_builtin_functions(FunctionRegistry* registry);

// Performance monitoring
void performance_start_timing();
double performance_end_timing();
void performance_update_stats(PerformanceStats* stats, const char* function_name, double time);

#endif // VIDPIPE_H