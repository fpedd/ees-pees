# EES-PEES Robot Project Controller

## Architecture
The code is split up into two directories:
* `include/`, headers that define the interface of every source file
* `src/`, the source files, including the main entry point `main.c`

We also have a `Makefile` to compile the code in the root directory.

## Usage
Use the `Makefile` in the root directory to compile the code. If there are no erros,
a new `build` directory will be created. The build directory is not part of
the version control system and should not be added or commited via git
(we have `/build` added to our) `.gitignore`. You can then execute the binary in the
`/build` directory.

```
make
./build/controller
```

To get a clean start (delete all build files):

```
make clean
```
