#include <pybind11/pybind11.h>

#include "primus/core.hpp"

namespace py = pybind11;

PYBIND11_MODULE(primus_core, m) {
    m.doc() = "PRIMUS C++ core";

    m.def(
        "hello",
        &primus::hello,
        "Returns PRIMUS C++ core status message"
    );

    m.def(
        "update_confidence",
        &primus::update_confidence,
        "Updates skill confidence using C++",
        py::arg("old_confidence"),
        py::arg("reward"),
        py::arg("learning_rate") = 0.15
    );
}
