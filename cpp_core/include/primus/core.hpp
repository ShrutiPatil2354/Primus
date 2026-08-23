#pragma once

#include <string>

namespace primus {

std::string hello();

double update_confidence(
    double old_confidence,
    double reward,
    double learning_rate
);

}
