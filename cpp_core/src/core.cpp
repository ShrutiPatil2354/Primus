#include "primus/core.hpp"

#include <algorithm>

namespace primus {

std::string hello() {
    return "PRIMUS C++ core active";
}

double update_confidence(
    double old_confidence,
    double reward,
    double learning_rate
) {
    double updated =
        old_confidence + learning_rate * (reward - old_confidence);

    return std::clamp(updated, 0.0, 1.0);
}

}
