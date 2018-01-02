# Lulesh

URL: https://github.com/LLNL/LULESH

## Compile

Make each binary name split by dash on options:

$ make clean
$ CXX="gcc -DUSE_MPI=0 -O3 -mtune=generic" make -j
$ mv lulesh gcc-o3-generic

$ make clean
$ CXX="gcc -DUSE_MPI=0 -O3 -mtune=native" make -j
$ mv lulesh gcc-o3-native

$ make clean
$ CXX="clang -DUSE_MPI=0 -O3 -mtune=generic" make -j
$ mv lulesh clang-o3-generic

$ make clean
$ CXX="clang -DUSE_MPI=0 -O3 -mtune=native" make -j
$ mv lulesh clang-o3-native

## Execute

Create a directory for this architecture:

$ mkdir Foo
$ cd Foo

Run each binary on different OpenMP threads (up to CPUs):

for i in gcc-o3-generic gcc-o3-native clang-o3-generic clang-o3-native; do
  ./run_up_to.sh ../$i
done

## Analysis

Create a CSV with the comparisons of all modes against all modes::

$ cd ..
$ ./read_logs.pl Foo > foo.csv

Import in your favourite spreadsheet software.
