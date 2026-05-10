#pragma once
#include <vector>
#include <cstddef>
#include <limits>
#include <type_traits>
#include <stdexcept>
#include "ringbuff.hpp"

template <typename T>
class ScalarStream
{
    static_assert(std::is_floating_point<T>::value,
                "ScalarStream requires floating point T");

public:
    ScalarStream(std::size_t window_size):
        m_buffer(check_window_size(window_size)),
        m_mean(0),
        m_m2(0)
    {}

    void push(T value) {
        bool was_full = (m_buffer.capacity() == m_buffer.size());
        T removed = m_buffer.push(value);

        if(!was_full){

            std::size_t n = m_buffer.size();

            T delta = value - m_mean; //mean before pushed
            m_mean += delta / static_cast<T>(n);

            T delta2 = value - m_mean; //mean after pushed
            m_m2 += delta * delta2;
        }
            
        else{

            std::size_t n = m_buffer.capacity();

            T old_mean = m_mean;
            T new_mean = old_mean + (value - removed) / static_cast<T>(n);

            m_m2 += (value - removed) * (value - new_mean + removed - old_mean);
            m_mean = new_mean;
        }
    }

    std::size_t size() const {return m_buffer.size();}

    std::size_t window_size() const {return m_buffer.capacity();}

    T mean() const {

        if(m_buffer.size() == 0) 
            return std::numeric_limits<T>::quiet_NaN();

        return m_mean;
        
    }

    T variance() const {
        
        if(m_buffer.size() < 2)
            return std::numeric_limits<T>::quiet_NaN();
        
        return m_m2 / static_cast<T>(m_buffer.size() - 1);
    }

    T sample_variance() const {
        return variance();
    }
    
    T population_variance() const {

        if(m_buffer.size() < 1)
            return std::numeric_limits<T>::quiet_NaN();
        return m_m2 / static_cast<T>(m_buffer.size());
    }

    void reset() {
        m_buffer.reset();
        m_mean = T();
        m_m2 = T();
    }

    const T& operator[](std::size_t i) const {
        return m_buffer[i];
    }

private:
    RingBuffer<T> m_buffer;
    T m_mean;
    T m_m2;

    static std::size_t check_window_size(std::size_t window_size){
        if(window_size == 0)
            throw std::invalid_argument("ScalarStream window_size must be greater than 0.");
        return window_size;
    }

};