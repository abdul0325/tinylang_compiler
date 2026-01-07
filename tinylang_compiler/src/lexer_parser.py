from lark import Lark, Transformer, Token, Tree, v_args
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional
from enum import Enum

# AST Node Definitions
@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    pass

@dataclass
class Program(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)

@dataclass
class VarDecl(ASTNode):
    var_type: str  # 'int' or 'bool'
    name: str
    value: Optional[ASTNode] = None

@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode

@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    then_block: List[ASTNode] = field(default_factory=list)
    else_block: Optional[List[ASTNode]] = None

@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode
    body: List[ASTNode] = field(default_factory=list)

@dataclass
class PrintStmt(ASTNode):
    expression: ASTNode

@dataclass
class BinaryOp(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode

@dataclass
class Literal(ASTNode):
    value: Any
    lit_type: str  # 'int' or 'bool'

@dataclass
class Variable(ASTNode):
    name: str

# Grammar Definition

TINYLANG_GRAMMAR = r"""
    ?start: program

    program: statement*

    ?statement: var_decl
              | assignment
              | if_stmt
              | while_stmt
              | print_stmt

    var_decl: TYPE IDENTIFIER ("=" expression)? ";"
    assignment: IDENTIFIER "=" expression ";"
    
    if_stmt: "if" "(" expression ")" then_block else_block?
    then_block: "{" statement* "}"
    else_block: "else" "{" statement* "}"
    while_stmt: "while" "(" expression ")" "{" statement* "}"
    print_stmt: "print" "(" expression ")" ";"

    ?expression: or_expr

    ?or_expr: and_expr
            | or_expr "||" and_expr -> or_op

    ?and_expr: equality
             | and_expr "&&" equality -> and_op

    ?equality: comparison
             | equality "==" comparison -> eq_op
             | equality "!=" comparison -> neq_op

    ?comparison: term
               | comparison "<" term -> lt_op
               | comparison ">" term -> gt_op
               | comparison "<=" term -> lte_op
               | comparison ">=" term -> gte_op

    ?term: factor
         | term "+" factor -> add_op
         | term "-" factor -> sub_op

    ?factor: unary
           | factor "*" unary -> mul_op
           | factor "/" unary -> div_op
           | factor "%" unary -> mod_op

    ?unary: primary
          | "-" unary -> unary_op
          | "!" unary -> unary_op

    ?primary: INTEGER -> int_literal
            | BOOLEAN -> bool_literal
            | IDENTIFIER -> variable
            | "(" expression ")"

    TYPE.2: "int" | "bool"
    BOOLEAN.1: "true" | "false"
    INTEGER: /[0-9]+/
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/

    %import common.WS
    %ignore WS
    COMMENT: "//" /[^\n]*/
    %ignore COMMENT
"""

# AST Builder (Transformer)

class ASTBuilder(Transformer):
    """Transforms parse tree into AST"""
    
    def program(self, items):
        return Program(statements=list(items))
    
    def var_decl(self, items):
        var_type = str(items[0])
        name = str(items[1])
        value = items[2] if len(items) > 2 else None
        return VarDecl(var_type=var_type, name=name, value=value)
    
    def assignment(self, items):
        return Assignment(name=str(items[0]), value=items[1])
    
    def if_stmt(self, items):
        condition = items[0]
        then_block = items[1]  # This is now a then_block node
        else_block = items[2] if len(items) > 2 else None  # This is an else_block node
        return IfStmt(condition=condition, then_block=then_block, else_block=else_block)
    
    def then_block(self, items):
        return list(items)
    
    def else_block(self, items):
        return list(items)
    
    def while_stmt(self, items):
        return WhileStmt(condition=items[0], body=list(items[1:]))
    
    def print_stmt(self, items):
        return PrintStmt(expression=items[0])
    
    # Binary operators
    def or_op(self, items):
        return BinaryOp(op="||", left=items[0], right=items[1])
    
    def and_op(self, items):
        return BinaryOp(op="&&", left=items[0], right=items[1])
    
    def eq_op(self, items):
        return BinaryOp(op="==", left=items[0], right=items[1])
    
    def neq_op(self, items):
        return BinaryOp(op="!=", left=items[0], right=items[1])
    
    def lt_op(self, items):
        return BinaryOp(op="<", left=items[0], right=items[1])
    
    def gt_op(self, items):
        return BinaryOp(op=">", left=items[0], right=items[1])
    
    def lte_op(self, items):
        return BinaryOp(op="<=", left=items[0], right=items[1])
    
    def gte_op(self, items):
        return BinaryOp(op=">=", left=items[0], right=items[1])
    
    def add_op(self, items):
        return BinaryOp(op="+", left=items[0], right=items[1])
    
    def sub_op(self, items):
        return BinaryOp(op="-", left=items[0], right=items[1])
    
    def mul_op(self, items):
        return BinaryOp(op="*", left=items[0], right=items[1])
    
    def div_op(self, items):
        return BinaryOp(op="/", left=items[0], right=items[1])
    
    def mod_op(self, items):
        return BinaryOp(op="%", left=items[0], right=items[1])
    
    def unary_op(self, items):
        op = str(items[0])
        operand = items[1]
        return UnaryOp(op=op, operand=operand)
    
    def int_literal(self, items):
        return Literal(value=int(items[0]), lit_type='int')
    
    def bool_literal(self, items):
        value = str(items[0]) == 'true'
        return Literal(value=value, lit_type='bool')
    
    def variable(self, items):
        return Variable(name=str(items[0]))

# Compiler Frontend
class TinyLangCompiler:
    """Main compiler class"""
    
    def __init__(self):
        self.parser = Lark(TINYLANG_GRAMMAR, parser='lalr')
        self.ast_builder = ASTBuilder()
    
    def parse(self, source_code: str) -> Program:
        """Parse source code and return AST"""
        try:
            parse_tree = self.parser.parse(source_code)
            ast = self.ast_builder.transform(parse_tree)
            return ast
        except Exception as e:
            print(f"Parse error: {e}")
            raise
    
    def pretty_print_ast(self, node: ASTNode, indent: int = 0) -> str:
        """Pretty print the AST for debugging"""
        prefix = "  " * indent
        
        if isinstance(node, Program):
            result = f"{prefix}Program:\n"
            for stmt in node.statements:
                result += self.pretty_print_ast(stmt, indent + 1)
            return result
        
        elif isinstance(node, VarDecl):
            result = f"{prefix}VarDecl: {node.var_type} {node.name}"
            if node.value:
                result += " =\n" + self.pretty_print_ast(node.value, indent + 1)
            else:
                result += "\n"
            return result
        
        elif isinstance(node, Assignment):
            result = f"{prefix}Assignment: {node.name} =\n"
            result += self.pretty_print_ast(node.value, indent + 1)
            return result
        
        elif isinstance(node, IfStmt):
            result = f"{prefix}If:\n{prefix}  condition:\n"
            result += self.pretty_print_ast(node.condition, indent + 2)
            result += f"{prefix}  then:\n"
            for stmt in node.then_block:
                result += self.pretty_print_ast(stmt, indent + 2)
            if node.else_block:
                result += f"{prefix}  else:\n"
                for stmt in node.else_block:
                    result += self.pretty_print_ast(stmt, indent + 2)
            return result
        
        elif isinstance(node, WhileStmt):
            result = f"{prefix}While:\n{prefix}  condition:\n"
            result += self.pretty_print_ast(node.condition, indent + 2)
            result += f"{prefix}  body:\n"
            for stmt in node.body:
                result += self.pretty_print_ast(stmt, indent + 2)
            return result
        
        elif isinstance(node, PrintStmt):
            result = f"{prefix}Print:\n"
            result += self.pretty_print_ast(node.expression, indent + 1)
            return result
        
        elif isinstance(node, BinaryOp):
            result = f"{prefix}BinaryOp: {node.op}\n"
            result += self.pretty_print_ast(node.left, indent + 1)
            result += self.pretty_print_ast(node.right, indent + 1)
            return result
        
        elif isinstance(node, UnaryOp):
            result = f"{prefix}UnaryOp: {node.op}\n"
            result += self.pretty_print_ast(node.operand, indent + 1)
            return result
        
        elif isinstance(node, Literal):
            return f"{prefix}Literal: {node.value} ({node.lit_type})\n"
        
        elif isinstance(node, Variable):
            return f"{prefix}Variable: {node.name}\n"
        
        return f"{prefix}{node}\n"

# Demo & Testing

def main():
    # Example TinyLang programs
    example_programs = [
        # Example 1: Simple variable declaration and arithmetic
        """
        int x = 10;
        int y = 20;
        int z = x + y * 2;
        print(z);
        """,
        
        # Example 2: Conditionals
        """
        int age = 25;
        bool isAdult = age >= 18;
        
        if (isAdult) {
            print(1);
        } else {
            print(0);
        }
        """,
        
        # Example 3: While loop
        """
        int counter = 0;
        while (counter < 5) {
            print(counter);
            counter = counter + 1;
        }
        """,
        
        # Example 4: Complex expressions
        """
        int a = 5;
        int b = 10;
        bool result = (a < b) && (b > 0) || (a == 5);
        
        if (result) {
            int c = a * b + 15;
            print(c);
        }
        """
    ]
    
    compiler = TinyLangCompiler()
    
    for i, program in enumerate(example_programs, 1):
        print(f"\n{'='*60}")
        print(f"Example {i}:")
        print('='*60)
        print("Source Code:")
        print(program)
        print("\n" + "-"*60)
        print("AST:")
        print("-"*60)
        
        try:
            ast = compiler.parse(program)
            print(compiler.pretty_print_ast(ast))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()