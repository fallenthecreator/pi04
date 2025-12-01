 
#include <iostream> 
#include <vector> 
 
void bubbleSort(std::vector<int>& beads) { 
    bool swapped; 
    for (size_t i = 0; i < beads.size() - 1; ++i) { 
        swapped = false; 
        for (size_t j = 0; j < beads.size() - i - 1; ++j) { 
            if (beads[j] > beads[j + 1]) { 
                std::swap(beads[j], beads[j + 1]); 
                swapped = true; 
            } 
        } 
        if (!swapped) break; 
    } 
} 
 
int main() { 
    std::vector<int> beads = {5, 2, 9, 1, 5, 6}; 
     
    std::cout << "До сортировки: "; 
    for (int bead : beads) { 
        std::cout << bead << " "; 
    } 
    std::cout << std::endl; 
    bubbleSort(beads); 
 
    std::cout << "После сортировки: "; 
    for (int bead : beads) { 
        std::cout << bead << " "; 
    } 
    std::cout << std::endl; 
 
    return 0; 
} 
