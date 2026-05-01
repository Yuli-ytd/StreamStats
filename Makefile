CXX = g++
CXXFLAGS = -std=c++11 -O3

PYTHON_INC := $(shell python3-config --includes)

PYBIND11_PATH := extern/pybind11/include
ifneq ($(wildcard $(PYBIND11_PATH)/.),)
	PYBIND11_INC := -I$(PYBIND11_PATH)
else
	PYBIND11_INC := $(shell python3 -m pybind11 --includes 2>/dev/null)
endif

ifeq ($(strip $(PYBIND11_INC)),)
    $(error "Pybind11 not found. Please run 'git submodule update --init' or 'pip install pybind11'")
endif

INC := $(PYTHON_INC) $(PYBIND11_INC)

all: streamstats.so test_ringbuff

streamstats.so: src/main.cpp
	$(CXX) $(CXXFLAGS) -fPIC $(INC) -shared $< -o $@

test_ringbuff: test/test_ringbuff.cpp include/ringbuff.hpp
	$(CXX) $(CXXFLAGS) $(INTERNAL_INC) $< -o $@

.PHONY = all test clean

test: streamstats.so test_ringbuff
	@echo "\n...Running C++ unit tests..."
	./test_ringbuff
	@echo "\n...Running Python integration tests..."
	PYTHONPATH=. pytest test/ -v

clean:
	rm -rf *.so test_ringbuff __pycache__ .pytest_cache */__pycache__