CC = gcc
CXX = g++
CFLAGS = -Wall -Wextra -O2 -pthread -g
CXXFLAGS = -Wall -Wextra -O2 -pthread -g -std=c++11
LDFLAGS = -pthread -lm
TARGET = vidpipe
SOURCES = main.c lexer.c parser.c runtime.c functions.c
CXX_SOURCES = camera.cpp
OBJECTS = $(SOURCES:.c=.o) $(CXX_SOURCES:.cpp=.o)
HEADERS = vidpipe.h

# OpenCV support
OPENCV_CFLAGS = $(shell pkg-config --cflags opencv4 2>/dev/null)
OPENCV_LIBS = $(shell pkg-config --libs opencv4 2>/dev/null)

ifneq ($(OPENCV_CFLAGS),)
    CXXFLAGS += -DUSE_OPENCV $(OPENCV_CFLAGS)
    LDFLAGS += $(OPENCV_LIBS)
    $(info OpenCV found - enabling camera support)
else
    $(info OpenCV not found - using fallback camera simulation)
endif

# SDL2 support for GUI windows
SDL2_CFLAGS = $(shell pkg-config --cflags sdl2 2>/dev/null)
SDL2_LIBS = $(shell pkg-config --libs sdl2 2>/dev/null)

ifneq ($(SDL2_CFLAGS),)
    CXXFLAGS += -DUSE_SDL2 $(SDL2_CFLAGS)
    CFLAGS += -DUSE_SDL2 $(SDL2_CFLAGS)
    LDFLAGS += $(SDL2_LIBS)
    $(info SDL2 found - enabling GUI window support)
else
    $(info SDL2 not found - GUI windows not available)
endif

# macOS frameworks
ifeq ($(shell uname), Darwin)
    LDFLAGS += -framework ApplicationServices -framework CoreGraphics
endif

# Default target
all: $(TARGET)

# Build the main executable
$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

# Compile C source files
$(filter-out camera.o, $(OBJECTS)): %.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

# Compile camera.cpp as C++ (for OpenCV)
camera.o: camera.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Run tests
test: $(TARGET)
	./$(TARGET) --help
	./$(TARGET) -c "capture -> grayscale -> display"

# Run examples
run-simple: $(TARGET)
	./$(TARGET) examples/simple.vp

run-parallel: $(TARGET)
	./$(TARGET) examples/parallel.vp

run-buffered: $(TARGET)
	./$(TARGET) examples/buffered.vp

run-camera: $(TARGET)
	./$(TARGET) examples/camera_demo.vp

run-webcam: $(TARGET)
	./$(TARGET) -c "webcam -> window"

run-live: $(TARGET)
	./$(TARGET) examples/camera_live.vp

run-loops: $(TARGET)
	./$(TARGET) examples/loops.vp

# Interactive mode
interactive: $(TARGET)
	./$(TARGET) -i

# Clean build files
clean:
	rm -f $(OBJECTS) $(TARGET)
	rm -f frame_*.ppm

# Install (optional)
install: $(TARGET)
	cp $(TARGET) /usr/local/bin/

# Debug build
debug: CFLAGS += -DDEBUG -g
debug: clean $(TARGET)

# Static analysis
analyze:
	clang --analyze $(SOURCES)

.PHONY: all clean test install debug analyze interactive run-simple run-parallel run-buffered run-camera run-webcam run-live run-loops