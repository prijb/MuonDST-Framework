#include <iostream>
#include <fstream>
#include "TFile.h"
#include "TTree.h"

void print_events(const char* input_file, const char* output_file) {
    // Abrir el archivo ROOT
    TFile *file = TFile::Open(input_file);
    if (!file || file->IsZombie()) {
        std::cerr << "Error: no se pudo abrir el archivo " << input_file << std::endl;
        return;
    }

    // Obtener el árbol "Events"
    TTree *tree = dynamic_cast<TTree*>(file->Get("Events"));
    if (!tree) {
        std::cerr << "Error: no se pudo encontrar el árbol 'Events' en el archivo " << input_file << std::endl;
        file->Close();
        return;
    }

    // Redirigir la salida estándar a un archivo
    std::ofstream outfile(output_file);
    std::streambuf *coutbuf = std::cout.rdbuf(); // Guardar el buffer original de cout
    std::cout.rdbuf(outfile.rdbuf()); // Redirigir cout al archivo

    // Imprimir el árbol "Events"
    tree->Print();

    // Restaurar el buffer original de cout
    std::cout.rdbuf(coutbuf);

    // Cerrar el archivo ROOT
    file->Close();
}
