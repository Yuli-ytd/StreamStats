CXX = g++
CXXFLAGS = -std=c++11 -O3 -fPIC

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

streamstats.so: src/main.cpp
	$(CXX) $(CXXFLAGS) $(INC) -shared $< -o $@

.PHONY = test clean

test: streamstats.so
	PYTHONPATH=. pytest test/ -v

clean:
	rm -rf *.so __pycache__ .pytest_cache