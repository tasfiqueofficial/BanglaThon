#!/usr/bin/env python3
"""
Bangla Programming Language — CLI Runner
===========================================
Kaj: ekটা .bl file (Bangla language source code) niয়ে run kore dেখায়।

Usage (installed as command):
    bangla run hello.bl
    bangla            (interactive REPL mode)
    bangla --version

Usage (running directly from source):
    python3 main.py hello.bl
"""

import sys
try:
    from .lexer import Lexer, LexerError
    from .parser import Parser, ParserError
    from .interpreter import Interpreter, BanglaRuntimeError
    from . import __version__
except ImportError:
    from lexer import Lexer, LexerError
    from parser import Parser, ParserError
    from interpreter import Interpreter, BanglaRuntimeError
    __version__ = "0.1.0"


def run_file(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: ফাইল পাওয়া যায়নি — '{filepath}'")
        sys.exit(1)

    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        Interpreter().interpret(ast)
    except LexerError as e:
        print(f"[Lexer Error] {e}")
        sys.exit(1)
    except ParserError as e:
        print(f"[Parser Error] {e}")
        sys.exit(1)
    except BanglaRuntimeError as e:
        print(f"[Runtime Error] {e}")
        sys.exit(1)


def run_repl():
    """Interactive mode — ekটা line diye ekটা line code run kora jay."""
    print(f"Bangla Programming Language v{__version__} — Interactive Mode")
    print("Exit korte 'exit' likhun\n")
    interpreter = Interpreter()
    while True:
        try:
            line = input(">> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBidai!")
            break
        if line.strip() == "exit":
            print("Bidai!")
            break
        if not line.strip():
            continue
        try:
            tokens = Lexer(line).tokenize()
            ast = Parser(tokens).parse()
            interpreter.interpret(ast)
        except LexerError as e:
            print(f"[Lexer Error] {e}")
        except ParserError as e:
            print(f"[Parser Error] {e}")
        except BanglaRuntimeError as e:
            print(f"[Runtime Error] {e}")


def main():
    """Entry point — 'bangla' command likhle eita call hoy."""
    args = sys.argv[1:]

    if not args:
        run_repl()
        return

    if args[0] in ("--version", "-v"):
        print(f"Bangla Programming Language v{__version__}")
        return

    if args[0] in ("--help", "-h"):
        print(__doc__)
        return

    if args[0] == "run":
        if len(args) < 2:
            print("Error: file path দিন। Usage: bangla run <file.bl>")
            sys.exit(1)
        run_file(args[1])
        return

    # 'bangla file.bl' ba 'file.bng' — 'run' keyword na dile o file hishebe treat kora
    if args[0].endswith(".bl") or args[0].endswith(".bng"):
        run_file(args[0])
        return

    print(f"Unknown command: {args[0]}")
    print("Usage: bangla run <file.bl>  |  bangla  |  bangla --version")
    sys.exit(1)


if __name__ == "__main__":
    main()
