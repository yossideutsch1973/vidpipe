#include "vidpipe.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>

// Frame management
Frame* frame_create(int width, int height, int channels) {
    Frame* frame = malloc(sizeof(Frame));
    frame->width = width;
    frame->height = height;
    frame->channels = channels;
    frame->data = malloc(width * height * channels);
    frame->timestamp = 0;
    frame->metadata = NULL;
    return frame;
}

void frame_destroy(Frame* frame) {
    if (!frame) return;
    if (frame->data) free(frame->data);
    if (frame->metadata) free(frame->metadata);
    free(frame);
}

Frame* frame_copy(Frame* src) {
    if (!src) return NULL;
    
    Frame* dst = frame_create(src->width, src->height, src->channels);
    memcpy(dst->data, src->data, src->width * src->height * src->channels);
    dst->timestamp = src->timestamp;
    return dst;
}

// Queue management
FrameQueue* queue_create(int max_size) {
    FrameQueue* queue = malloc(sizeof(FrameQueue));
    queue->head = NULL;
    queue->tail = NULL;
    queue->size = 0;
    queue->max_size = max_size > 0 ? max_size : 1;
    pthread_mutex_init(&queue->mutex, NULL);
    pthread_cond_init(&queue->not_empty, NULL);
    pthread_cond_init(&queue->not_full, NULL);
    return queue;
}

void queue_destroy(FrameQueue* queue) {
    if (!queue) return;
    
    pthread_mutex_lock(&queue->mutex);
    
    QueueNode* current = queue->head;
    while (current) {
        QueueNode* next = current->next;
        frame_destroy(current->frame);
        free(current);
        current = next;
    }
    
    pthread_mutex_unlock(&queue->mutex);
    pthread_mutex_destroy(&queue->mutex);
    pthread_cond_destroy(&queue->not_empty);
    pthread_cond_destroy(&queue->not_full);
    free(queue);
}

bool queue_push(FrameQueue* queue, Frame* frame) {
    if (!queue || !frame) return false;
    
    pthread_mutex_lock(&queue->mutex);
    
    // Wait if queue is full
    while (queue->size >= queue->max_size) {
        pthread_cond_wait(&queue->not_full, &queue->mutex);
    }
    
    QueueNode* node = malloc(sizeof(QueueNode));
    node->frame = frame;
    node->next = NULL;
    
    if (queue->tail) {
        queue->tail->next = node;
    } else {
        queue->head = node;
    }
    queue->tail = node;
    queue->size++;
    
    pthread_cond_signal(&queue->not_empty);
    pthread_mutex_unlock(&queue->mutex);
    
    return true;
}

Frame* queue_pop(FrameQueue* queue) {
    if (!queue) return NULL;
    
    pthread_mutex_lock(&queue->mutex);
    
    // Check if queue is empty, return NULL immediately if so
    if (queue->size == 0) {
        pthread_mutex_unlock(&queue->mutex);
        return NULL;
    }
    
    QueueNode* node = queue->head;
    Frame* frame = node->frame;
    queue->head = node->next;
    
    if (!queue->head) {
        queue->tail = NULL;
    }
    
    queue->size--;
    free(node);
    
    pthread_cond_signal(&queue->not_full);
    pthread_mutex_unlock(&queue->mutex);
    
    return frame;
}

bool queue_is_empty(FrameQueue* queue) {
    if (!queue) return true;
    
    pthread_mutex_lock(&queue->mutex);
    bool empty = (queue->size == 0);
    pthread_mutex_unlock(&queue->mutex);
    
    return empty;
}

// Function registry
FunctionRegistry* registry_create() {
    FunctionRegistry* registry = malloc(sizeof(FunctionRegistry));
    registry->capacity = 32;
    registry->count = 0;
    registry->functions = malloc(sizeof(FunctionDef) * registry->capacity);
    return registry;
}

void registry_destroy(FunctionRegistry* registry) {
    if (!registry) return;
    
    for (int i = 0; i < registry->count; i++) {
        free(registry->functions[i].name);
        if (registry->functions[i].params) {
            free(registry->functions[i].params);
        }
    }
    
    free(registry->functions);
    free(registry);
}

void registry_add(FunctionRegistry* registry, const char* name, 
                 ProcessFunc func, void* params, bool is_source, bool is_sink) {
    if (!registry || !name || !func) return;
    
    if (registry->count >= registry->capacity) {
        registry->capacity *= 2;
        registry->functions = realloc(registry->functions, 
                                     sizeof(FunctionDef) * registry->capacity);
    }
    
    FunctionDef* def = &registry->functions[registry->count++];
    def->name = strdup(name);
    def->func = func;
    def->params = params;
    def->is_source = is_source;
    def->is_sink = is_sink;
}

FunctionDef* registry_get(FunctionRegistry* registry, const char* name) {
    if (!registry || !name) return NULL;
    
    for (int i = 0; i < registry->count; i++) {
        if (strcmp(registry->functions[i].name, name) == 0) {
            return &registry->functions[i];
        }
    }
    
    return NULL;
}

// Worker thread function
static void* worker_thread(void* arg) {
    ExecutionNode* node = (ExecutionNode*)arg;
    
    while (node->running) {
        Frame* input = NULL;
        
        // Source nodes generate frames
        if (node->function->is_source) {
            input = node->function->func(NULL, node->function->params);
            if (!input) {
                usleep(1000); // Brief pause if no frame available
                continue;
            }
        } else {
            // Processing nodes consume from input queue
            input = queue_pop(node->input_queue);
            if (!input) {
                // No frame available, brief sleep to avoid busy waiting
                usleep(1000);
                continue;
            }
        }
        
        // Process the frame
        Frame* output = NULL;
        if (!node->function->is_sink) {
            output = node->function->func(input, node->function->params);
        } else {
            // Sink nodes don't produce output
            node->function->func(input, node->function->params);
        }
        
        // Distribute output to all output queues
        if (output && node->output_count > 0) {
            for (int i = 0; i < node->output_count; i++) {
                Frame* copy = (i == node->output_count - 1) ? output : frame_copy(output);
                queue_push(node->output_queues[i], copy);
            }
        } else if (output) {
            frame_destroy(output);
        }
        
        // Clean up input frame if not passed through
        if (input && input != output) {
            frame_destroy(input);
        }
        
        // Frame rate limiting to prevent CPU starvation
        if (node->function->is_source) {
            // Sources should limit their generation rate to 30 FPS
            usleep(33333);
        } else if (node->function->is_sink) {
            // Sinks need rate limiting to prevent overwhelming displays  
            usleep(33333);
        } else {
            // Processing nodes yield CPU but can run faster
            usleep(1000);
        }
    }
    
    return NULL;
}

// Runtime management
Runtime* runtime_create(FunctionRegistry* registry) {
    Runtime* runtime = malloc(sizeof(Runtime));
    runtime->nodes = NULL;
    runtime->node_count = 0;
    runtime->registry = registry;
    runtime->running = false;
    return runtime;
}

void runtime_destroy(Runtime* runtime) {
    if (!runtime) return;
    
    runtime_stop(runtime);
    
    if (runtime->nodes) {
        for (int i = 0; i < runtime->node_count; i++) {
            ExecutionNode* node = runtime->nodes[i];
            if (node->input_queue) queue_destroy(node->input_queue);
            if (node->output_queues) free(node->output_queues);
            free(node);
        }
        free(runtime->nodes);
    }
    
    free(runtime);
}

static ExecutionNode* create_execution_node(Runtime* runtime, ASTNode* ast_node) {
    ExecutionNode* exec_node = malloc(sizeof(ExecutionNode));
    exec_node->node = ast_node;
    exec_node->input_queue = NULL;
    exec_node->output_queues = NULL;
    exec_node->output_count = 0;
    exec_node->running = false;
    exec_node->function = NULL;
    
    if (ast_node->type == NODE_FUNCTION) {
        exec_node->function = registry_get(runtime->registry, ast_node->name);
        if (!exec_node->function) {
            fprintf(stderr, "Unknown function: %s\n", ast_node->name);
            free(exec_node);
            return NULL;
        }
        
        if (!exec_node->function->is_source) {
            int buffer_size = ast_node->buffer_size > 0 ? ast_node->buffer_size : 1;
            exec_node->input_queue = queue_create(buffer_size);
        }
    }
    
    return exec_node;
}

static bool build_execution_graph(Runtime* runtime, ASTNode* ast, 
                                 ExecutionNode** nodes, int* node_count) {
    // Simple implementation for now - just handle linear pipelines
    // TODO: Implement full graph building for parallel and merge nodes
    
    if (!ast) return false;
    
    switch (ast->type) {
        case NODE_FUNCTION: {
            ExecutionNode* node = create_execution_node(runtime, ast);
            if (!node) return false;
            
            nodes[(*node_count)++] = node;
            break;
        }
        
        case NODE_PIPELINE: {
            // Build left side
            if (!build_execution_graph(runtime, ast->children[0], nodes, node_count)) {
                return false;
            }
            
            // Build right side
            int right_start = *node_count;
            if (!build_execution_graph(runtime, ast->children[1], nodes, node_count)) {
                return false;
            }
            
            // Connect left output to right input
            if (right_start < *node_count) {
                ExecutionNode* left_end = nodes[right_start - 1];
                ExecutionNode* right_begin = nodes[right_start];
                
                if (!right_begin->function->is_source) {
                    left_end->output_count = 1;
                    left_end->output_queues = malloc(sizeof(FrameQueue*));
                    left_end->output_queues[0] = right_begin->input_queue;
                }
            }
            break;
        }
        
        case NODE_PARALLEL: {
            // For now, just execute the first branch
            // TODO: Implement proper parallel execution
            if (!build_execution_graph(runtime, ast->children[0], nodes, node_count)) {
                return false;
            }
            break;
        }
        
        case NODE_LOOP: {
            // For loops, build the inner pipeline and mark for continuous execution
            if (ast->child_count > 0) {
                if (!build_execution_graph(runtime, ast->children[0], nodes, node_count)) {
                    return false;
                }
                
                // Mark the nodes in this loop for continuous execution
                // This is handled by the worker threads which will keep looping
            }
            break;
        }
        
        default:
            fprintf(stderr, "Unsupported node type in execution graph\n");
            return false;
    }
    
    return true;
}

bool runtime_execute(Runtime* runtime, ASTNode* ast) {
    if (!runtime || !ast || runtime->running) return false;
    
    // Allocate space for execution nodes
    ExecutionNode** nodes = malloc(sizeof(ExecutionNode*) * 100); // Max 100 nodes
    int node_count = 0;
    
    // Build execution graph
    if (!build_execution_graph(runtime, ast, nodes, &node_count)) {
        free(nodes);
        return false;
    }
    
    runtime->nodes = nodes;
    runtime->node_count = node_count;
    runtime->running = true;
    
    // Start worker threads
    for (int i = 0; i < node_count; i++) {
        runtime->nodes[i]->running = true;
        pthread_create(&runtime->nodes[i]->thread, NULL, 
                      worker_thread, runtime->nodes[i]);
    }
    
    return true;
}

void runtime_stop(Runtime* runtime) {
    if (!runtime || !runtime->running) return;
    
    runtime->running = false;
    
    // Stop all worker threads
    for (int i = 0; i < runtime->node_count; i++) {
        runtime->nodes[i]->running = false;
    }
    
    // Wait for threads to finish
    for (int i = 0; i < runtime->node_count; i++) {
        pthread_join(runtime->nodes[i]->thread, NULL);
    }
}