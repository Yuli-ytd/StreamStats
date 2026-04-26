#include <pybind11/pybind11.h>

int add(){
    int a = 3;
    int b = 5;
    return a+b;
}

PYBIND11_MODULE(streamstats, m){
    m.doc() = "Streaming Statistic Function Modules";
    m.def("add", &add, "Basic addition function for testing Makefile works");
}