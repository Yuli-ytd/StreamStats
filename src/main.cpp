#include <pybind11/pybind11.h>
#include <scalar_stream.hpp>

PYBIND11_MODULE(streamstats, m){
    m.doc() = "Streaming Statistic Function Modules";
    pybind11::class_<ScalarStream<double>>(m, "StreamStats")
        .def(pybind11::init<std::size_t>())
        .def("push", &ScalarStream<double>::push)
        .def("size", &ScalarStream<double>::size)
        .def("window_size", &ScalarStream<double>::window_size)
        .def("mean", &ScalarStream<double>::mean)
        .def("variance",
            [](const ScalarStream<double>& self, int ddof){
                if(ddof == 0){
                    return self.population_variance();
                }
                if(ddof == 1){
                    return self.sample_variance();
                }
                throw pybind11::value_error("only ddof=0 or ddof=1 are supported.");
            },
            pybind11::arg("ddof") = 0
        )
        .def("reset", &ScalarStream<double>::reset);
}