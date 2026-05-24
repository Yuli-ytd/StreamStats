#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <scalar_stream.hpp>

namespace py = pybind11;

template <typename T>
void bind_scalar_stream(py::module_& m, const char* name)
{
    py::class_<ScalarStream<T>>(m, name)
        .def(py::init<std::size_t>())
        .def("push", &ScalarStream<T>::push)
        .def("size", &ScalarStream<T>::size)
        .def("window_size", &ScalarStream<T>::window_size)
        .def("mean", &ScalarStream<T>::mean)
        .def(
            "variance",
            [](const ScalarStream<T>& self, int ddof) {
                if (ddof == 0) {
                    return self.population_variance();
                }
                if (ddof == 1) {
                    return self.sample_variance();
                }
                throw py::value_error("only ddof=0 or ddof=1 are supported.");
            },
            py::arg("ddof") = 0
        )
        .def("reset", &ScalarStream<T>::reset);
}

PYBIND11_MODULE(streamstats, m)
{
    m.doc() = "Streaming Statistic Function Modules";

    bind_scalar_stream<double>(m, "_StreamStatsF64");
    bind_scalar_stream<float>(m, "_StreamStatsF32");

    m.def(
        "StreamStats",
        [](std::size_t window_size, py::object dtype) -> py::object{
            if(dtype.is_none()){
                return py::cast(ScalarStream<double>(window_size));
            }

            py::module_ np = py::module_::import("numpy");
            py::object dtype_obj = np.attr("dtype")(dtype);
            std::string dtype_name = py::str(dtype_obj);

            if(dtype_name == "float64"){
                return py::cast(ScalarStream<double>(window_size));
            }

            else if(dtype_name == "float32"){
                return py::cast(ScalarStream<float>(window_size));
            }

            throw py::value_error("dtype must be np.float32 or np.float64.");
        },
        py::arg("window_size"),
        py::arg("dtype") = py::none()
    );
}