#include "binlog/binlog.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>

int main() {
  BINLOG_INFO("Hello {}!", "World");

  std::ofstream logfile("hello.blog", std::ofstream::out|std::ofstream::binary);
  binlog::consume(logfile);

  if (!logfile)
  {
    std::cerr << "Failed to write hello.blog\n";
    return EXIT_FAILURE;
  }

  std::cout << "Binary log written to hello.blog\n";
  return EXIT_SUCCESS;
}
