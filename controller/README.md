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
## Protocol

* IP `127.0.0.1` (local host)
* Controller Port `6969`
* Backend Port `6970`

The protocol should (for now) run over UDP. UDP has a checksum build in. So if a
packet arrives, it is intact. On top of that we have to ensure that:
* when we have no packet / communication for a certain time we will timeout and
  go into a failsafe state
* that packets arrive in order, so old packets get discarded
* check how much delay we have on the line and handle that accordingly
