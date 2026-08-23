#include <iostream>

#include "primus/core.hpp"

int main() {
    std::cout << primus::hello() << std::endl;

    double old_confidence = 0.5;
    double reward = 1.0;
    double learning_rate = 0.15;

    double new_confidence = primus::update_confidence(
        old_confidence,
        reward,
        learning_rate
    );

    std::cout << "Old confidence: " << old_confidence << std::endl;
    std::cout << "Reward: " << reward << std::endl;
    std::cout << "New confidence: " << new_confidence << std::endl;

    return 0;
}
