#!/usr/bin/env python3
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer_parser import TinyLangCompiler

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <filename.tiny>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    with open(filename, 'r') as f:
        source_code = f.read()
    
    compiler = TinyLangCompiler()
    
    print("Source Code:")
    print("="*60)
    print(source_code)
    print("\nAST:")
    print("="*60)
    
    ast = compiler.parse(source_code)
    print(compiler.pretty_print_ast(ast))

if __name__ == "__main__":
    main()