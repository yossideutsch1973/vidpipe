#include "vidpipe.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>

static Runtime* g_runtime = NULL;

void signal_handler(int sig) {
    (void)sig; // Suppress unused parameter warning
    if (g_runtime) {
        printf("\nStopping pipeline...\n");
        runtime_stop(g_runtime);
    }
    exit(0);
}

char* read_file(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Cannot open file: %s\n", filename);
        return NULL;
    }
    
    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    if (size <= 0) {
        fprintf(stderr, "Invalid file size: %ld\n", size);
        fclose(file);
        return NULL;
    }
    
    char* buffer = malloc(size + 1);
    if (!buffer) {
        fprintf(stderr, "Memory allocation failed\n");
        fclose(file);
        return NULL;
    }
    
    size_t bytes_read = fread(buffer, 1, size, file);
    if (bytes_read != (size_t)size) {
        fprintf(stderr, "Failed to read file: expected %ld bytes, got %zu\n", size, bytes_read);
        free(buffer);
        fclose(file);
        return NULL;
    }
    
    buffer[size] = '\0';
    fclose(file);
    return buffer;
}

void run_pipeline(const char* pipeline_str) {
    printf("Pipeline: %s\n", pipeline_str);
    
    // Tokenize
    Token* tokens = lex(pipeline_str);
    if (!tokens) {
        fprintf(stderr, "Failed to tokenize pipeline\n");
        return;
    }
    
    // Parse
    ASTNode* ast = parse(tokens);
    free_tokens(tokens);
    
    if (!ast) {
        fprintf(stderr, "Failed to parse pipeline\n");
        return;
    }
    
    printf("AST:\n");
    print_ast(ast, 0);
    printf("\n");
    
    // Create function registry and register built-ins
    FunctionRegistry* registry = registry_create();
    register_builtin_functions(registry);
    
    // Create runtime
    g_runtime = runtime_create(registry);
    
    // Execute pipeline
    printf("Starting pipeline execution...\n");
    if (runtime_execute(g_runtime, ast)) {
        printf("Pipeline running. Press Ctrl+C to stop.\n");
        
        // Wait for interrupt
        while (g_runtime->running) {
            sleep(1);
        }
    } else {
        fprintf(stderr, "Failed to execute pipeline\n");
    }
    
    // Cleanup
    runtime_destroy(g_runtime);
    registry_destroy(registry);
    free_ast(ast);
}

void run_interactive() {
    printf("VidPipe Interactive Mode\n");
    printf("Enter pipeline (or 'quit' to exit):\n");
    
    char buffer[1024];
    while (1) {
        printf("> ");
        fflush(stdout);
        
        if (!fgets(buffer, sizeof(buffer), stdin)) {
            break;
        }
        
        // Remove newline
        buffer[strcspn(buffer, "\n")] = '\0';
        
        if (strcmp(buffer, "quit") == 0 || strcmp(buffer, "exit") == 0) {
            break;
        }
        
        if (strlen(buffer) > 0) {
            run_pipeline(buffer);
        }
    }
}

void print_usage(const char* program) {
    printf("VidPipe - Pipeline Language for Realtime Video Processing\n\n");
    printf("Usage:\n");
    printf("  %s <pipeline.vp>           Run pipeline from file\n", program);
    printf("  %s -c \"pipeline\"           Run pipeline from command line\n", program);
    printf("  %s -i                      Interactive mode\n", program);
    printf("  %s --help                  Show this help\n", program);
    printf("\nExamples:\n");
    printf("  %s -c \"capture -> grayscale -> edges -> display\"\n", program);
    printf("  %s -c \"capture [10]-> blur ~> edges -> display\"\n", program);
    printf("  %s -c \"capture -> grayscale &> edges &> threshold\"\n", program);
    printf("\nBuilt-in Functions:\n");
    printf("  Sources:    capture, capture-frame\n");
    printf("  Filters:    grayscale, gray, edges, blur, threshold, invert, resize\n");
    printf("  Sinks:      display, show, save\n");
}

int main(int argc, char* argv[]) {
    // Set up signal handler
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }
    
    if (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0) {
        print_usage(argv[0]);
        return 0;
    }
    
    if (strcmp(argv[1], "-i") == 0) {
        run_interactive();
        return 0;
    }
    
    if (strcmp(argv[1], "-c") == 0) {
        if (argc < 3) {
            fprintf(stderr, "Error: -c requires a pipeline string\n");
            return 1;
        }
        run_pipeline(argv[2]);
        return 0;
    }
    
    // Try to run as file
    char* pipeline = read_file(argv[1]);
    if (pipeline) {
        run_pipeline(pipeline);
        free(pipeline);
    }
    
    return 0;
}