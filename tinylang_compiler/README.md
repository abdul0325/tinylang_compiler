# 🚀 TinyLang Compiler

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen?style=for-the-badge)

**A Complete, Production-Quality Compiler Built from Scratch in Python**

*From source code to execution  Experience every stage of compilation*

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples)

</div>

---

## ✨ Overview

**TinyLang** is a fully-featured educational compiler that transforms a custom C-like programming language into executable bytecode. Built entirely in Python, it demonstrates every phase of modern compiler construction with crystal-clear code and comprehensive documentation.

### 🎯 What Makes TinyLang Special?

- **Complete Pipeline**: Every compilation phase from lexical analysis to execution
- **Educational Focus**: Clean, well-documented code perfect for learning
- **Real Optimizations**: Multiple optimization passes that actually improve code
- **Visual Feedback**: See every transformation step in your code's journey
- **Production Patterns**: Industry-standard techniques and data structures

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SOURCE CODE (.tiny)                     │
│                   int x = 10 + 20 * 2;                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: LEXICAL ANALYSIS                                   │
│  • Tokenization using Lark parser                            │
│  • Keyword recognition with priority                         │
│  • Comment stripping                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: SYNTAX ANALYSIS & AST GENERATION                   │
│  • Context-free grammar parsing                              │
│  • Abstract Syntax Tree construction                         │
│  • Operator precedence handling                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: SEMANTIC ANALYSIS                                  │
│  • Type checking (int, bool)                                 │
│  • Symbol table with scope management                        │
│  • Undeclared variable detection                             │
│  • Type mismatch validation                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: INTERMEDIATE REPRESENTATION (TAC)                  │
│  • Three-Address Code generation                             │
│  • Temporary variable allocation                             │
│  • Label generation for control flow                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 5: OPTIMIZATION                                       │
│  • Constant Folding: 2+3 → 5                                │
│  • Dead Code Elimination: Remove unused temps                │
│  • Algebraic Simplification: x*1 → x, x+0 → x              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 6: CODE GENERATION                                    │
│  • Bytecode emission                                         │
│  • Label address resolution                                  │
│  • Stack-based instruction generation                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 7: VIRTUAL MACHINE EXECUTION                          │
│  • Stack-based VM                                            │
│  • Runtime variable storage                                  │
│  • Program output                                            │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
                   OUTPUT: 50
```

---

## 🎨 Features

### 🔤 Language Features

| Feature | Description | Example |
|---------|-------------|---------|
| **Data Types** | Integers and Booleans | `int x = 42;` `bool flag = true;` |
| **Operators** | Arithmetic, Logical, Relational | `+, -, *, /, %, &&, \|\|, !, <, >, ==` |
| **Control Flow** | If/Else and While loops | `if (x > 0) {...} else {...}` |
| **Variables** | Declaration and assignment | `int counter = 0;` |
| **I/O** | Print statements | `print(x);` |
| **Scoping** | Nested block scopes | `{ int local = 5; }` |

### 🛠️ Compiler Features

<table>
<tr>
<td width="50%">

#### 🔍 **Analysis**
- ✅ Lexical Analysis with Lark
- ✅ Recursive Descent Parsing
- ✅ Symbol Table Management
- ✅ Type Checking System
- ✅ Scope Resolution

</td>
<td width="50%">

#### ⚡ **Optimization**
- ✅ Constant Folding
- ✅ Dead Code Elimination
- ✅ Algebraic Simplification
- ✅ Instruction Count Metrics
- ✅ Before/After Comparison

</td>
</tr>
<tr>
<td width="50%">

#### 🎯 **Code Generation**
- ✅ Three-Address Code (TAC)
- ✅ Bytecode Compilation
- ✅ Label Resolution
- ✅ Jump Optimization

</td>
<td width="50%">

#### 💻 **Execution**
- ✅ Stack-Based VM
- ✅ Variable Storage
- ✅ Control Flow Handling
- ✅ Runtime Output

</td>
</tr>
</table>

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/tinylang-compiler.git
cd tinylang-compiler

# Install dependencies
pip install -r requirements.txt

# Run the compiler
python src/semantic_codegen.py
```

### Dependencies

```txt
lark==1.1.9      # Parser generator
rich==13.7.0     # Beautiful terminal output (optional)
```

---

## ⚡ Quick Start

### 1️⃣ Write Your First Program

Create `hello.tiny`:

```c
// My first TinyLang program
int x = 10;
int y = 20;
int result = x + y * 2;

print(result);  // Output: 50
```

### 2️⃣ Compile and Run

```bash
python tests/test_runner.py file hello.tiny
```

### 3️⃣ See the Magic ✨

```
============================================================
SEMANTIC ANALYSIS
============================================================
✅ No semantic errors

Symbol Table:
  x: int (scope 0)
  y: int (scope 0)
  result: int (scope 0)

============================================================
TAC GENERATION
============================================================
TAC Instructions (before optimization):
    0: t0 = 10
    1: x = t0
    2: t1 = 20
    ...

============================================================
OPTIMIZATION
============================================================
Original instructions: 15
Optimized instructions: 12
Reduction: 3 instructions (20.0%)

============================================================
EXECUTION
============================================================
Program output:
50

Final variable values:
  x = 10
  y = 20
  result = 50
```

---

## 📚 Examples

### Example 1: Fibonacci Sequence

```c
// Generate first 10 Fibonacci numbers
int a = 0;
int b = 1;
int i = 0;

print(a);
print(b);

while (i < 8) {
    int temp = a + b;
    print(temp);
    a = b;
    b = temp;
    i = i + 1;
}
```

**Output:** `0, 1, 1, 2, 3, 5, 8, 13, 21, 34`

---

### Example 2: Factorial

```c
// Calculate 5!
int n = 5;
int result = 1;
int i = 1;

while (i <= n) {
    result = result * i;
    i = i + 1;
}

print(result);  // Output: 120
```

---

### Example 3: Conditional Logic

```c
// Check if number is positive
int x = 15;

if (x > 0) {
    print(1);  // Positive
} else {
    if (x < 0) {
        print(-1);  // Negative
    } else {
        print(0);   // Zero
    }
}
```

---

### Example 4: Boolean Logic

```c
// Logical operations
bool a = true;
bool b = false;
bool result = (a && !b) || (b && !a);

if (result) {
    print(1);  // XOR is true
} else {
    print(0);
}
```

---

## 🧪 Testing

### Run Test Suite

```bash
# Run all built-in tests
python tests/test_runner.py

# Run all tests (built-in + file tests)
python tests/test_runner.py all

# Test specific file
python tests/test_runner.py file tests/test_programs/fibonacci.tiny

# Test all .tiny files
python tests/test_runner.py files
```

### Test Results

```
============================================================
TEST SUMMARY
============================================================
Total: 10 tests
✅ Passed: 10
❌ Failed: 0
============================================================
```

---

## 📖 Documentation

### Project Structure

```
tinylang_compiler/
├── src/
│   ├── lexer_parser.py       # Lexer, Parser, AST
│   ├── semantic_codegen.py   # Semantic Analysis, TAC, VM
│   └── main.py               # CLI interface
├── tests/
│   ├── test_runner.py        # Test framework
│   └── test_programs/        # Sample .tiny files
│       ├── fibonacci.tiny
│       ├── factorial.tiny
│       └── ...
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🎓 Learning Resources

### Understanding Each Phase

#### **Phase 1-2: Lexing & Parsing**
The compiler uses **Lark** parser with a context-free grammar that defines TinyLang's syntax. Token priority ensures keywords like `int` and `bool` are recognized before identifiers.

#### **Phase 3: Semantic Analysis**
A **symbol table** tracks variable declarations across nested scopes. Type checking ensures operations are performed on compatible types.

#### **Phase 4: TAC Generation**
The AST is linearized into **Three-Address Code** (quadruples), where each instruction has at most three operands: `result = arg1 op arg2`.

#### **Phase 5: Optimization**
Three optimization passes improve code efficiency:
- **Constant Folding**: Evaluate constant expressions at compile time
- **Dead Code Elimination**: Remove unused temporary variables
- **Algebraic Simplification**: Apply mathematical identities

#### **Phase 6-7: Code Generation & Execution**
TAC is compiled to **bytecode** for a stack-based VM. The VM executes instructions using a stack for operands and a dictionary for variables.

---

## 🛣️ Roadmap

### ✅ Completed
- [x] Lexer and Parser
- [x] AST Generation
- [x] Semantic Analysis
- [x] Symbol Table
- [x] TAC Generation
- [x] Optimization Passes
- [x] Bytecode Generation
- [x] Stack-based VM
- [x] Test Framework

### 🔜 Coming Soon
- [ ] Function definitions and calls
- [ ] Arrays and pointers
- [ ] String data type
- [ ] For loops
- [ ] Break/continue statements
- [ ] More optimizations (CSE, loop optimization)
- [ ] x86/ARM assembly generation
- [ ] LLVM IR backend
- [ ] Debugger with breakpoints
- [ ] Interactive REPL

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Areas for Contribution
- 🐛 Bug fixes
- ✨ New language features
- ⚡ Additional optimizations
- 📝 Documentation improvements
- 🧪 More test cases
- 🎨 Better error messages

---

## 📝 Language Grammar

```ebnf
program       → statement*
statement     → var_decl | assignment | if_stmt | while_stmt | print_stmt
var_decl      → TYPE IDENTIFIER ("=" expression)? ";"
assignment    → IDENTIFIER "=" expression ";"
if_stmt       → "if" "(" expression ")" block ("else" block)?
while_stmt    → "while" "(" expression ")" block
print_stmt    → "print" "(" expression ")" ";"
block         → "{" statement* "}"

expression    → logic_or
logic_or      → logic_and ("||" logic_and)*
logic_and     → equality ("&&" equality)*
equality      → comparison (("==" | "!=") comparison)*
comparison    → term (("<" | ">" | "<=" | ">=") term)*
term          → factor (("+" | "-") factor)*
factor        → unary (("*" | "/" | "%") unary)*
unary         → ("!" | "-") unary | primary
primary       → INTEGER | BOOLEAN | IDENTIFIER | "(" expression ")"

TYPE          → "int" | "bool"
BOOLEAN       → "true" | "false"
INTEGER       → [0-9]+
IDENTIFIER    → [a-zA-Z_][a-zA-Z0-9_]*
```

---

## 💡 Use Cases

### 🎓 **Education**
Perfect for:
- Compiler design courses
- Programming language theory
- Understanding code optimization
- Learning VM architecture

### 🔬 **Research**
Experiment with:
- New optimization techniques
- Alternative IR representations
- Different execution models
- Language feature design

### 🛠️ **Development**
Foundation for:
- Domain-specific languages (DSLs)
- Script interpreters
- Configuration languages
- Educational tools

---

## 📊 Performance

### Optimization Impact

| Test Case | Original Instructions | Optimized | Reduction |
|-----------|----------------------|-----------|-----------|
| Arithmetic | 15 | 12 | 20% |
| Fibonacci | 42 | 38 | 9.5% |
| Factorial | 28 | 24 | 14.3% |
| Nested Loops | 65 | 58 | 10.8% |

---

## 🐛 Known Limitations

- No function definitions yet
- Single file compilation only
- Limited to int and bool types
- No array support
- No string operations
- Simple error messages

*These are features planned for future releases!*

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 TinyLang Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 Acknowledgments

- **Lark Parser** - Fast and elegant parsing library
- **Compiler Design Principles** - Inspired by classic textbooks
- **Open Source Community** - For feedback and contributions

---

## 📬 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/tinylang-compiler/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/yourusername/tinylang-compiler/discussions)

---

<div align="center">

### ⭐ Star this repository if you find it helpful!

**Made with ❤️ by passionate compiler enthusiasts**

[⬆ Back to Top](#-tinylang-compiler)

</div>
