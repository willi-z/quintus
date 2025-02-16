# Quintus

[![Rust package](https://github.com/willi-z/quintus/actions/workflows/test.yaml/badge.svg)](https://github.com/willi-z/quintus/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/willi-z/quintus/branch/master/graph/badge.svg?token=TM9VDQMA4L)](https://codecov.io/gh/willi-z/quintus)

---

Help you find the optimal configuration from a set of materials.

Experiments are important, but testing every possible combination is not feasible. This is where QUINTUS comes to the rescue. QUINTUS scans material databases, combines materials, and predicts their combined properties.

This allows experimentalists to focus on the most promising ones.


## Usage

The there are two ways to insert and edit data:
1. import the data an EXCEL-file with a additional data in a JSON-config file (see examples)
2. open a graphical user interface in your browser (work in progress)
![](/docs/QUINTUS.png)

The avaible data can be combined with serveral models and used for further evaluation and optimizations.
![](/docs/plot.png)

## Development

see only warning when executing main.rs:
```
RUST_LOG=warn cargo run --bin main
```

Testing
```
RUST_LOG=debug cargo test
```

Coverage
```
cargo install cargo-llvm-cov
cargo llvm-cov
```
https://api.codecov.io/validate
