#include <list>
#include <iostream>

int main()
{
    std::list<int> defaultlist{1,2,3,4,5,6};
    for (int n : defaultlist)
        if(n%2 == 0)
        {
            std::cout << n << '\t';
        }
    std::cout << std::endl;
}

