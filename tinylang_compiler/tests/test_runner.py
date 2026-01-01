"""
TinyLang Compiler Test Runner
Comprehensive testing suite for the TinyLang compiler
"""

import sys
import os
import glob
from io import StringIO

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer_parser import TinyLangCompiler
from semantic_codegen import TinyLangFullCompiler

class TestResult:
    """Store test results"""
    def __init__(self, name, passed, output=None, error=None, expected=None):
        self.name = name
        self.passed = passed
        self.output = output
        self.error = error
        self.expected = expected

class TinyLangTester:
    """Test runner for TinyLang programs"""
    
    def __init__(self):
        self.parser = TinyLangCompiler()
        self.results = []
    
    def test_code(self, name, code, expected_output=None, should_fail=False):
        """Test a code snippet"""
        print(f"\n{'='*60}")
        print(f"Test: {name}")
        print('='*60)
        print("Code:")
        print(code)
        print()
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Parse
            ast = self.parser.parse(code)
            
            # Compile and run
            compiler = TinyLangFullCompiler()
            compiler.compile_and_run(ast)
            
            # Get output
            output = compiler.vm.output
            
            # Restore stdout
            sys.stdout = old_stdout
            
            # Check results
            if should_fail:
                print(f"❌ FAILED: Expected semantic error but code executed")
                self.results.append(TestResult(name, False, output, "Should have failed"))
                return False
            
            if expected_output is not None:
                if output == expected_output:
                    print(f"✅ PASSED")
                    print(f"Output: {output}")
                    self.results.append(TestResult(name, True, output))
                    return True
                else:
                    print(f"❌ FAILED")
                    print(f"Expected: {expected_output}")
                    print(f"Got: {output}")
                    self.results.append(TestResult(name, False, output, "Wrong output", expected_output))
                    return False
            else:
                print(f"✅ PASSED")
                print(f"Output: {output}")
                self.results.append(TestResult(name, True, output))
                return True
                
        except Exception as e:
            sys.stdout = old_stdout
            if should_fail:
                print(f"✅ PASSED (Expected failure)")
                print(f"Error: {e}")
                self.results.append(TestResult(name, True, None, str(e)))
                return True
            else:
                print(f"❌ FAILED with exception")
                print(f"Error: {e}")
                self.results.append(TestResult(name, False, None, str(e)))
                return False
    
    def test_file(self, filename, expected_output=None):
        """Test a .tiny file"""
        with open(filename, 'r') as f:
            code = f.read()
        
        name = os.path.basename(filename)
        return self.test_code(name, code, expected_output)
    
    def print_summary(self):
        """Print test summary"""
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print('='*60)
        print(f"Total: {len(self.results)} tests")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print("\nFailed tests:")
            for r in self.results:
                if not r.passed:
                    print(f"  - {r.name}: {r.error}")
        
        print('='*60)

def run_basic_tests():
    """Run basic test suite"""
    tester = TinyLangTester()
    
    # Test 1: Simple arithmetic
    tester.test_code(
        "Simple Arithmetic",
        """
        int x = 10;
        int y = 20;
        int z = x + y;
        print(z);
        """,
        expected_output=['30']
    )
    
    # Test 2: Multiplication precedence
    tester.test_code(
        "Operator Precedence",
        """
        int result = 2 + 3 * 4;
        print(result);
        """,
        expected_output=['14']
    )
    
    # Test 3: While loop
    tester.test_code(
        "While Loop",
        """
        int i = 0;
        while (i < 3) {
            print(i);
            i = i + 1;
        }
        """,
        expected_output=['0', '1', '2']
    )
    
    # Test 4: If/Else
    tester.test_code(
        "If/Else Statement",
        """
        int x = 10;
        if (x > 5) {
            print(1);
        } else {
            print(0);
        }
        """,
        expected_output=['1']
    )
    
    # Test 5: Boolean operations
    tester.test_code(
        "Boolean Logic",
        """
        bool a = true;
        bool b = false;
        if (a && !b) {
            print(1);
        } else {
            print(0);
        }
        """,
        expected_output=['1']
    )
    
    # Test 6: Nested scopes
    tester.test_code(
        "Nested Scopes",
        """
        int x = 10;
        if (x > 5) {
            int y = 20;
            print(x + y);
        }
        print(x);
        """,
        expected_output=['30', '10']
    )
    
    # Test 7: Complex expression
    tester.test_code(
        "Complex Expression",
        """
        int a = 5;
        int b = 10;
        int c = (a + b) * 2 - 5;
        print(c);
        """,
        expected_output=['25']
    )
    
    # Test 8: Factorial
    tester.test_code(
        "Factorial",
        """
        int n = 5;
        int result = 1;
        int i = 1;
        
        while (i <= n) {
            result = result * i;
            i = i + 1;
        }
        
        print(result);
        """,
        expected_output=['120']
    )
    
    # Test 9: Undeclared variable (should fail)
    tester.test_code(
        "Undeclared Variable (Error)",
        """
        int x = 10;
        print(y);
        """,
        should_fail=True
    )
    
    # Test 10: Type mismatch (should fail)
    tester.test_code(
        "Type Mismatch (Error)",
        """
        int x = 10;
        bool y = x;
        """,
        should_fail=True
    )
    
    return tester

def run_file_tests():
    """Run tests from test_programs directory"""
    tester = TinyLangTester()
    
    test_dir = "tests/test_programs"
    if os.path.exists(test_dir):
        files = glob.glob(f"{test_dir}/*.tiny")
        
        if files:
            print(f"\nFound {len(files)} test files in {test_dir}")
            for file in files:
                tester.test_file(file)
        else:
            print(f"\nNo .tiny files found in {test_dir}")
    else:
        print(f"\nDirectory {test_dir} does not exist")
    
    return tester

def main():
    """Main test runner"""
    print("TinyLang Compiler Test Suite")
    print("="*60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "file":
            if len(sys.argv) > 2:
                # Test specific file
                tester = TinyLangTester()
                tester.test_file(sys.argv[2])
                tester.print_summary()
            else:
                print("Usage: python test_runner.py file <filename.tiny>")
        elif sys.argv[1] == "files":
            # Test all files in test_programs
            tester = run_file_tests()
            tester.print_summary()
        elif sys.argv[1] == "all":
            # Run all tests
            print("\n>>> Running Basic Tests <<<")
            tester1 = run_basic_tests()
            
            print("\n>>> Running File Tests <<<")
            tester2 = run_file_tests()
            
            # Combined summary
            all_results = tester1.results + tester2.results
            passed = sum(1 for r in all_results if r.passed)
            failed = len(all_results) - passed
            
            print(f"\n{'='*60}")
            print("OVERALL SUMMARY")
            print('='*60)
            print(f"Total: {len(all_results)} tests")
            print(f"✅ Passed: {passed}")
            print(f"❌ Failed: {failed}")
            print('='*60)
        else:
            print("Unknown command")
            print("Usage:")
            print("  python test_runner.py           - Run basic tests")
            print("  python test_runner.py all       - Run all tests")
            print("  python test_runner.py file <f>  - Test specific file")
            print("  python test_runner.py files     - Test all .tiny files")
    else:
        # Default: run basic tests
        tester = run_basic_tests()
        tester.print_summary()

if __name__ == "__main__":
    main()