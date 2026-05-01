#include <iostream>
#include <cassert>
#include "ringbuff.hpp"

int main() {
    std::cout << "Running RingBuffer tests..." << std::endl;
    
    int cap = 5;
    RingBuffer<double> buff(cap);

    //test 1: initial push
    for(int i = 0; i < 3; i++){
        double ori = buff.push(i + 1.0);
        assert(ori == 0.0);
    }
    assert(buff.size() == 3);

    //test 2: random access
    for(int i = 0; i < 3; i++){
        assert(buff[i] == i + 1.0);
    }

    //test 3: capacity overflow
    buff.push(4.0);
    buff.push(5.0); //buffer full
    assert(buff.size() == 5);
    //continue push elements
    for (int i = 0; i < 3; ++i) {
        double ori = buff.push(i + 10.0);
        assert(ori == (i + 1.0)); // 1.0, 2.0, 3.0 should be poped out by sequencial
    }
    
    std::cout << "All tests passed!" << std::endl;
    return 0;
}