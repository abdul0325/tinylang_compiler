from lexer_parser import TinyLangCompiler
from semantic_codegen import TinyLangFullCompiler
import sys

def test_file(filename):
    """Test a single .tiny file"""
    print(f"\n{'='*60}")
    print(f"Testing: {filename}")
    print('='*60)
    
    # Read the source file
    with open(filename, 'r') as f:
        source_code = f.read()
    
    print("Source Code:")
    print(source_code)
    print()
    
    # Parse
    parser = TinyLangCompiler()
    try:
        ast = parser.parse(source_code)
    except Exception as e:
        print(f"❌ Parse Error: {e}")
        return False
    
    # Compile and run
    compiler = TinyLangFullCompiler()
    try:
        compiler.compile_and_run(ast)
        return True
    except Exception as e:
        print(f"❌ Runtime Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_runner.py <file.tiny>")
        print("   or: python test_runner.py all  (to test all files)")
        sys.exit(1)
    
    if sys.argv[1] == "all":
        # Test all files in tests/test_programs/
        import glob
        files = glob.glob("tests/test_programs/*.tiny")
        
        passed = 0
        failed = 0
        
        for file in files:
            if test_file(file):
                passed += 1
            else:
                failed += 1
        
        print(f"\n{'='*60}")
        print(f"Results: {passed} passed, {failed} failed")
        print('='*60)
    else:
        test_file(sys.argv[1])

if __name__ == "__main__":
    main()