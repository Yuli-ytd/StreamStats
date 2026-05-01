#include <vector>
#include <cstddef>
#include <cassert>
#include <stdexcept>

template <typename T>
class RingBuffer{
public:
    RingBuffer(size_t capacity)
        :m_data(capacity), m_head(0), m_capacity(capacity), m_count(0)
    {
        if(m_capacity == 0){
            throw std::invalid_argument("RingBuffer capacity must be greater than 0.");
        }
    }

    T push(T value)
    {
        T m_prev = m_data[m_head];
        m_data[m_head] = value;

        m_head++;
        if(m_head >= m_capacity) m_head = 0;
        m_prev = (m_count < m_capacity)? T() : m_prev;
        m_count = (m_count < m_capacity)? m_count+1 : m_count;
        return m_prev;
    }

    const T& operator[](size_t i) const
    {
        std::size_t start = (m_count < m_capacity)? 0 : m_head;
        return m_data[(start + i) % m_capacity];
    }

    std::size_t capacity() const { return m_capacity; }
    std::size_t size() const { return m_count; }

private:
    std::vector<T> m_data;
    std::size_t m_head;
    std::size_t m_capacity;
    std::size_t m_count;
};