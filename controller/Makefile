### Simple Makefile to compile our Controller ###

TARGET := controller
CC = gcc
BUILD_DIR := build
SRC_DIR := src
INC_DIR := include

SRCS := $(shell find $(SRC_DIR) -name *.c)
OBJS := $(SRCS:%=$(BUILD_DIR)/%.o)
DEPS := $(OBJS:.o=.d)

INC_DIRS := $(shell find $(SRC_DIR) -type d)
INC_FLAGS := $(addprefix -I,$(INC_DIRS))

CFLAGS := $(INC_FLAGS) -MMD -MP -I$(INC_DIR) -lpthread -Wall -Wextra -lm

all: $(BUILD_DIR)/$(TARGET)

$(BUILD_DIR)/$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $@ $(CFLAGS)

$(BUILD_DIR)/%.c.o: %.c
	$(MKDIR_P) $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: all clean

clean:
	$(RM) -r $(BUILD_DIR)

-include $(DEPS)

MKDIR_P := mkdir -p
