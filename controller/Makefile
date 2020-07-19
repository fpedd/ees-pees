### Makefile to compile our Controller ###

# Compiler
CC := g++

# Main Target
TARGET := controller

# Target to run unit tests
TARGET_TST := controller_test

# Project directories
BUILD_DIR := build
SRC_DIR := src
INC_DIR := include
TST_DIR := test

# Path to your Googletest
GTEST_INC := /usr/src/gtest/include/gtest
GTEST_BIN := gtest

# Get all source files we need to compile
SRCS := $(shell find $(SRC_DIR) -name '*.c')
OBJS := $(SRCS:%=$(BUILD_DIR)/%.o)

# Get all source files needed for testing
SRCS_TST := $(filter-out %main.c, $(SRCS))
SRCS_TST += $(shell find $(TST_DIR) -name '*.cpp')
OBJS_TST := $(SRCS_TST:%=$(BUILD_DIR)/%.o)

# Linker and compiler flags
LDFLAGS := -lpthread -lm -Wall -Wextra
CFLAGS := -MMD -MP -I$(INC_DIR) -Wall -Wextra

# Main target
all: $(BUILD_DIR)/$(TARGET)

$(BUILD_DIR)/$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $@ $(LDFLAGS)

# Test target
test: $(BUILD_DIR)/$(TARGET_TST)
	./$(BUILD_DIR)/$(TARGET_TST)

$(BUILD_DIR)/$(TARGET_TST): $(OBJS_TST)
	$(CC) $(OBJS_TST) -o $@ -l$(GTEST_BIN) $(LDFLAGS)

# Target to compile C sources
$(BUILD_DIR)/%.c.o: %.c
	$(MKDIR_P) $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

# Target to compile C++ sources
$(BUILD_DIR)/%.cpp.o: %.cpp
	$(MKDIR_P) $(dir $@)
	$(CC) $(CFLAGS) -I$(GTEST_INC) -c $< -o $@

.PHONY: all clean test

clean:
	rm -rf $(BUILD_DIR)

MKDIR_P := mkdir -p
