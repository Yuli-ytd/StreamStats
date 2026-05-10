#include <iostream>
#include <cassert>
#include <cmath>
#include "scalar_stream.hpp"

bool approx_equal(double a, double b, double eps = 1e-12){
    return std::fabs(a - b) < eps;
}

int main(){
    std::cout << "\nRunning ScalarStream tests..." << std::endl;

    ScalarStream<double> stream(3);

    //test 1: check for empty buffer
    assert(stream.size() == 0);
    assert(std::isnan(stream.mean()));
    assert(std::isnan(stream.sample_variance()));
    assert(std::isnan(stream.population_variance()));

    //test 2: initial push 2 elements
    for(int i = 0; i < 2; i++){
        stream.push(i + 1.0);
        assert(stream[i] == i + 1.0);
    }
    assert(stream.size() == 2);
    assert(stream.window_size() == 3);
    assert(approx_equal(stream.mean(), 1.5));
    assert(approx_equal(stream.sample_variance(), 0.5));
    assert(approx_equal(stream.population_variance(), 0.25));

    //test 3: push 2 more elements, buffer fulled
    stream.push(3.0);
    stream.push(10.0);
    assert(approx_equal(stream[0], 2.0)); //1.0 had been removed
    assert(approx_equal(stream.mean(), 5.0));
    assert(approx_equal(stream.sample_variance(), 19.0));
    assert(approx_equal(stream.population_variance(), (38.0 / 3)));

    //test 4: check reset function
    stream.reset();

    assert(stream.size() == 0);
    assert(std::isnan(stream.mean()));
    assert(std::isnan(stream.sample_variance()));
    assert(std::isnan(stream.population_variance()));
    
    std::cout << "All tests passed!" << std::endl;
    return 0;

}