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
INTERNAL_INC := -Iinclude

all: streamstats.so test_ringbuff test_scalar_stream

streamstats.so: src/main.cpp include/scalar_stream.hpp include/ringbuff.hpp
	$(CXX) $(CXXFLAGS) $(INTERNAL_INC) -fPIC $(INC) -shared $< -o $@

test_ringbuff: test/test_ringbuff.cpp include/ringbuff.hpp
	$(CXX) $(CXXFLAGS) $(INTERNAL_INC) $< -o $@

test_scalar_stream: test/test_scalar_stream.cpp include/scalar_stream.hpp include/ringbuff.hpp
	$(CXX) $(CXXFLAGS) $(INTERNAL_INC) $< -o $@ 

.PHONY: all test benchmark clean

test: streamstats.so test_ringbuff test_scalar_stream
	@echo "\n...Running C++ unit tests..."
	./test_ringbuff
	./test_scalar_stream
	@echo "\n...Running Python integration tests..."
	PYTHONPATH=. pytest test/ -v

benchmark: streamstats.so
	@echo "\n...Benchmark runtime tests..."
	PYTHONPATH=. python3 benchmark/benchmark_runtime.py

clean:
	rm -rf *.so test_* __pycache__ .pytest_cache */__pycache__