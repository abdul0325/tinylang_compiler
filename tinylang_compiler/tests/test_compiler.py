import unittest
from lexer_parser import TinyLangCompiler
from semantic_codegen import TinyLangFullCompiler, SemanticAnalyzer

class TestCompiler(unittest.TestCase):
    
    def setUp(self):
        self.parser = TinyLangCompiler()
        self.compiler = TinyLangFullCompiler()
    
    def test_arithmetic(self):
        """Test basic arithmetic"""
        code = "int x = 5 + 3; print(x);"
        ast = self.parser.parse(code)
        self.compiler.compile_and_run(ast)
        self.assertEqual(self.compiler.vm.output, ['8'])
    
    def test_while_loop(self):
        """Test while loop"""
        code = """
        int i = 0;
        while (i < 3) {
            print(i);
            i = i + 1;
        }
        """
        ast = self.parser.parse(code)
        self.compiler.compile_and_run(ast)
        self.assertEqual(self.compiler.vm.output, ['0', '1', '2'])
    
    def test_undeclared_variable(self):
        """Test semantic error for undeclared variable"""
        code = "print(x);"
        ast = self.parser.parse(code)
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        self.assertTrue(len(analyzer.errors) > 0)
    
    def test_type_mismatch(self):
        """Test semantic error for type mismatch"""
        code = "int x = 10; bool y = x;"
        ast = self.parser.parse(code)
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        self.assertTrue(len(analyzer.errors) > 0)

if __name__ == "__main__":
    unittest.main()