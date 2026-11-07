# Bangla Programming Language - Documentation

## Overview

**Bangla Programming Language** is a complete programming language interpreter written in Python that allows you to write code using Bangla (Bengali) keywords and syntax. It's a tree-walking interpreter that supports variables, functions, loops, conditionals, arrays, and more.

## Features

✅ **Variables** - Declare variables with `dhori`  
✅ **Data Types** - Numbers, Strings, Booleans, Lists (Arrays), Null  
✅ **Operators** - Arithmetic (+, -, *, /, %), Comparison (<, >, <=, >=, ==, !=), Logical (ebong/ba/noy)  
✅ **Control Flow** - if/else, else-if, while loops, for loops  
✅ **Functions** - User-defined functions with parameters and return values  
✅ **Arrays/Lists** - Create, access, and manipulate lists  
✅ **Built-in Functions** - Length, append, sort, reverse, sum, max, min, and more  
✅ **Break & Continue** - Loop control statements  
✅ **Comments** - Single-line comments with `#`  
✅ **String Interpolation** - String concatenation with `+`  
✅ **Bangla Unicode Support** - Full support for Bangla characters  

---

## Architecture

The interpreter consists of 4 main components:

### 1. **Lexer** (`lexer.py`)
- Tokenizes raw Bangla source code into tokens
- Handles Bangla keywords, identifiers, numbers, strings
- Recognizes operators and special characters
- Produces a token stream for the parser

### 2. **Parser** (`parser.py`)
- Implements recursive descent parsing
- Builds an Abstract Syntax Tree (AST) from tokens
- Uses operator precedence climbing for expressions
- Generates AST nodes representing the program structure

### 3. **AST Nodes** (`ast_nodes.py`)
- Defines all node types for the syntax tree
- Expression nodes: Number, String, Boolean, List, Identifier, BinaryOp, UnaryOp, etc.
- Statement nodes: VarDecl, Assignment, If, While, For, FunctionDef, etc.

### 4. **Interpreter** (`interpreter.py`)
- Tree-walking interpreter that executes the AST
- Maintains environments for variable scopes
- Implements built-in functions
- Handles control flow (break, continue, return)
- Provides error messages in Bangla

---

## Quick Start

### Installation

No external dependencies required! Just Python 3.6+

```bash
# Clone or download the Bangla language files
cd bangla-lang
```

### Running Programs

```bash
python3 main.py <program.bng>
```

Or directly from Python:

```python
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

code = '''
dhori x = 10
dekhao x
'''

lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
interpreter.interpret(ast)
```

---

## Language Reference

### Keywords

| Bangla | English | Purpose |
|--------|---------|---------|
| `dhori` | declare | Variable declaration |
| `jodi` | if | Conditional statement |
| `nahole` | else | Else/else-if block |
| `jotokkhon` | while | While loop |
| `jonno` | for | For loop (C-style) |
| `kaj` | function | Function definition |
| `ferot` | return | Return from function |
| `dekhao` | show/print | Print output |
| `nao` | take | Get user input |
| `talika` | list/array | Create array |
| `thamo` | break | Break from loop |
| `cholo` | continue | Continue to next iteration |
| `shotti` | true | Boolean true |
| `mittha` | false | Boolean false |
| `khali` | null | Null/none value |
| `ebong` | and | Logical AND |
| `ba` | or | Logical OR |
| `noy` | not | Logical NOT |

### Data Types

```bangla
# Numbers (int and float)
dhori num = 42
dhori pi = 3.14

# Strings
dhori naam = "Tasfique"
dhori message = "Hello World"

# Booleans
dhori flag = shotti
dhori empty = mittha

# Lists/Arrays
dhori numbers = talika(1, 2, 3, 4, 5)
dhori mixed = talika("hello", 42, shotti)

# Null
dhori nothing = khali
```

### Variables and Assignment

```bangla
# Declare and initialize
dhori x = 10

# Re-assign existing variable
x = 20

# Multiple variables
dhori a = 5
dhori b = 10
dhori sum = a + b
```

### Operators

#### Arithmetic
```bangla
dekhao 5 + 3      # Addition
dekhao 5 - 3      # Subtraction
dekhao 5 * 3      # Multiplication
dekhao 10 / 3     # Division
dekhao 10 % 3     # Modulo
dekhao -5         # Unary minus
```

#### Comparison
```bangla
dekhao 5 > 3      # Greater than
dekhao 5 < 3      # Less than
dekhao 5 >= 5     # Greater than or equal
dekhao 5 <= 5     # Less than or equal
dekhao 5 == 5     # Equal
dekhao 5 != 3     # Not equal
```

#### Logical
```bangla
dekhao shotti ebong shotti    # AND
dekhao shotti ba mittha       # OR
dekhao noy shotti             # NOT
```

#### String Concatenation
```bangla
dhori greeting = "Hello " + "World"
dhori message = "Age: " + 25    # Numbers converted to string
```

### Control Flow

#### If Statement
```bangla
jodi (x > 10) {
    dekhao "boro"
} nahole {
    dekhao "choto"
}
```

#### If-Else-If Chain
```bangla
jodi (x > 10) {
    dekhao "boro"
} nahole jodi (x == 10) {
    dekhao "samman"
} nahole {
    dekhao "choto"
}
```

#### While Loop
```bangla
dhori i = 0
jotokkhon (i < 5) {
    dekhao i
    i = i + 1
}
```

#### For Loop
```bangla
jonno (dhori i = 0; i < 5; i = i + 1) {
    dekhao i
}
```

#### Loop Control
```bangla
# Break out of loop
jonno (dhori i = 0; i < 10; i = i + 1) {
    jodi (i == 5) {
        thamo
    }
    dekhao i
}

# Skip to next iteration
jonno (dhori i = 0; i < 5; i = i + 1) {
    jodi (i == 2) {
        cholo
    }
    dekhao i
}
```

### Functions

#### Function Definition
```bangla
kaj add(a, b) {
    ferot a + b
}

kaj greet(naam) {
    dekhao "Assalamu Alaikum " + naam
}

kaj no_return() {
    dekhao "This function doesn't return"
    # Implicit return of null
}
```

#### Function Calls
```bangla
dhori result = add(5, 3)
greet("Tasfique")
no_return()

# Functions can call other functions
kaj multiply(a, b) {
    ferot a * b
}

kaj quadruple(x) {
    ferot multiply(multiply(x, 2), 2)
}
```

### Arrays/Lists

#### Creating Arrays
```bangla
dhori numbers = talika(1, 2, 3, 4, 5)
dhori strings = talika("hello", "world")
dhori mixed = talika(1, "two", shotti, khali)
```

#### Accessing Elements
```bangla
dhori first = numbers[0]
dhori third = numbers[2]
```

#### Modifying Elements
```bangla
numbers[0] = 10
numbers[2] = 99
```

#### Built-in List Functions

```bangla
dhori nums = talika(3, 1, 4, 1, 5, 9, 2, 6)

# Length
dekhao dhoirgo(nums)           # 8

# Append (mutates list)
juktokoro(nums, 100)           # Adds 100 to end

# Sort (returns new list)
dhori sorted = shajao(nums)    # Returns sorted copy

# Reverse (returns new list)
dhori reversed = ulto(nums)    # Returns reversed copy
dhori rev_str = ulto("Bangla") # Also works on strings

# Sum
dekhao jog_koro(nums)          # Sum of all elements

# Max
dekhao shorbo_boro(nums)       # Maximum value

# Min
dekhao shorbo_choto(nums)      # Minimum value
```

### User Input

```bangla
# Get input as string
dhori naam = nao("Apnar naam ki? ")
dekhao "Hello " + naam

# Convert to number
dhori num_str = nao("Ekta sankhya likun: ")
# Note: Input is always a string, convert manually if needed
```

### Comments

```bangla
# This is a single-line comment
dhori x = 10  # Comment at end of line

# Ei to ek bangla comment
dhori naam = "Bangla"  # আরও একটি মন্তব্য
```

---

## Complete Examples

### Example 1: Sum of Numbers
```bangla
kaj sum_range(n) {
    dhori total = 0
    jonno (dhori i = 1; i <= n; i = i + 1) {
        total = total + i
    }
    ferot total
}

dhori result = sum_range(10)
dekhao "Sum 1 to 10: " + result
```

**Output:**
```
Sum 1 to 10: 55
```

### Example 2: Fibonacci Sequence
```bangla
kaj fibonacci(n) {
    jodi (n <= 1) {
        ferot n
    }
    ferot fibonacci(n - 1) + fibonacci(n - 2)
}

jonno (dhori i = 0; i < 8; i = i + 1) {
    dekhao fibonacci(i)
}
```

**Output:**
```
0
1
1
2
3
5
8
13
```

### Example 3: Array Operations
```bangla
dhori numbers = talika(5, 2, 8, 1, 9)

dekhao "Original: " + numbers
dekhao "Sorted: " + shajao(numbers)
dekhao "Reversed: " + ulto(numbers)
dekhao "Sum: " + jog_koro(numbers)
dekhao "Max: " + shorbo_boro(numbers)
dekhao "Min: " + shorbo_choto(numbers)

juktokoro(numbers, 100)
dekhao "After append: " + numbers
```

**Output:**
```
Original: [5, 2, 8, 1, 9]
Sorted: [1, 2, 5, 8, 9]
Reversed: [9, 1, 8, 2, 5]
Sum: 25
Max: 9
Min: 1
After append: [5, 2, 8, 1, 9, 100]
```

### Example 4: String Manipulation
```bangla
dhori word = "Bangla"

dekhao "Original: " + word
dekhao "Reversed: " + ulto(word)
dekhao "Length: " + dhoirgo(word)

# First character
dekhao word[0]

# Last character
dekhao word[dhoirgo(word) - 1]
```

**Output:**
```
Original: Bangla
Reversed: algnaB
Length: 6
B
a
```

---

## Error Handling

The interpreter provides helpful error messages in Bangla:

### Lexer Errors
```
Lexer Error at line 1, col 5: Unexpected character '@'
```

### Parser Errors
```
Parser Error (line 3, col 10): Expected '=' after variable name 'x'
```

### Runtime Errors
```
ত্রুটি: 'undefined_var' নামে কোনো variable পাওয়া যায়নি
ত্রুটি: শূন্য দিয়ে ভাগ করা যায় না
ত্রুটি: Index এর বাইরে (out of range)
```

---

## Implementation Details

### Lexer
- Tokenizes Bangla source code using state machine
- Handles Bangla Unicode characters (U+0980 to U+09FF)
- Supports single and multi-character operators
- Proper line and column tracking for error reporting

### Parser
- Recursive descent parser with operator precedence climbing
- Builds complete AST for entire program
- Detailed error messages with line/column information

### Interpreter
- Tree-walking interpreter pattern
- Maintains environment for variable/function scopes
- Uses exceptions for control flow (break, continue, return)
- Short-circuit evaluation for logical operators
- Type coercion for string concatenation

---

## Testing

Run the comprehensive test suite:

```bash
python3 test_bangla.py
```

This runs 30+ tests covering:
- Variable declarations
- Arithmetic and string operations
- Control flow (if/else, loops)
- Function definitions and calls
- Arrays and built-in functions
- Error handling

---

## File Structure

```
bangla-language/
├── lexer.py              # Tokenizer
├── parser.py             # Parser (tokens -> AST)
├── ast_nodes.py          # AST node definitions
├── interpreter.py        # Tree-walking interpreter
├── main.py               # CLI entry point
├── test_bangla.py        # Comprehensive test suite
├── README.md             # This file
└── examples/
    ├── hello.bng
    ├── fibonacci.bng
    ├── array_demo.bng
    └── functions.bng
```

---

## Future Enhancements

Possible features to add:
- Dictionaries/hash maps
- String formatting methods
- File I/O operations
- Module/import system
- Classes and objects
- Exception handling (try/catch)
- Lambda functions
- Decorators
- Type annotations

---

## Author

Created as a demonstration of building a complete programming language interpreter from scratch.

**Language**: Python 3.6+  
**Pattern**: Tree-Walking Interpreter  
**Status**: ✅ Complete and Fully Tested

---

## License

Open source - feel free to use, modify, and distribute.

---

## Quick Reference

```bangla
# Variables
dhori x = 10

# Print
dekhao x

# Arithmetic
dhori sum = 5 + 3
dhori diff = 5 - 3
dhori product = 5 * 3
dhori quotient = 5 / 3
dhori remainder = 5 % 3

# Comparison
jodi (x > 5) { ... }
jodi (x < 5) { ... }
jodi (x >= 5) { ... }
jodi (x <= 5) { ... }
jodi (x == 5) { ... }
jodi (x != 5) { ... }

# Logic
jodi (a ebong b) { ... }
jodi (a ba b) { ... }
jodi (noy a) { ... }

# Control Flow
jodi (...) { ... } nahole { ... }
jotokkhon (...) { ... }
jonno (init; cond; update) { ... }

# Functions
kaj add(a, b) { ferot a + b }
dekhao add(2, 3)

# Arrays
dhori arr = talika(1, 2, 3)
dekhao arr[0]
arr[0] = 100

# Built-ins
dhoirgo(arr)        # length
juktokoro(arr, x)   # append
shajao(arr)         # sort
ulto(arr)           # reverse
jog_koro(arr)       # sum
shorbo_boro(arr)    # max
shorbo_choto(arr)   # min

# Loop Control
thamo      # break
cholo      # continue
ferot x    # return
```

---

## Troubleshooting

**Problem**: "command not found: python3"  
**Solution**: Install Python 3.6 or higher from python.org

**Problem**: "No such file or directory"  
**Solution**: Make sure you're in the correct directory with `cd` command

**Problem**: Error message in Bangla not displaying correctly  
**Solution**: Ensure your terminal supports UTF-8 encoding

**Problem**: IndexError or out of range  
**Solution**: Check array bounds; Bangla uses 0-based indexing like Python

---

Enjoy coding in Bangla! 🎉
