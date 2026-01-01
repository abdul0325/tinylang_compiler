"""
TinyLang Compiler - Part 2: Semantic Analysis + TAC + Optimization + Bytecode VM
Complete backend: semantic checking, IR generation, optimization, and execution
"""

from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Tuple
from enum import Enum
import sys

# Import AST nodes from Part 1 (assuming they're available)
# from lexer_parser import *

# ============================================================================
# Symbol Table
# ============================================================================

@dataclass
class Symbol:
    """Symbol table entry"""
    name: str
    var_type: str  # 'int' or 'bool'
    scope_level: int
    initialized: bool = True

class SymbolTable:
    """Manages variable scopes and declarations"""
    
    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Stack of scopes
        self.current_scope = 0
    
    def enter_scope(self):
        """Enter a new scope (e.g., inside if/while block)"""
        self.scopes.append({})
        self.current_scope += 1
    
    def exit_scope(self):
        """Exit current scope"""
        if self.current_scope > 0:
            self.scopes.pop()
            self.current_scope -= 1
    
    def declare(self, name: str, var_type: str) -> bool:
        """Declare a variable in current scope. Returns False if already declared."""
        if name in self.scopes[self.current_scope]:
            return False
        self.scopes[self.current_scope][name] = Symbol(
            name=name, var_type=var_type, scope_level=self.current_scope
        )
        return True
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a variable in current and parent scopes"""
        for i in range(self.current_scope, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i][name]
        return None
    
    def get_all_symbols(self) -> List[Symbol]:
        """Get all symbols from all scopes"""
        symbols = []
        for scope in self.scopes:
            symbols.extend(scope.values())
        return symbols

# ============================================================================
# Three-Address Code (TAC) / Intermediate Representation
# ============================================================================

class TACOp(Enum):
    """TAC operation types"""
    # Arithmetic
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    MOD = "%"
    NEG = "neg"
    
    # Relational
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="
    EQ = "=="
    NEQ = "!="
    
    # Logical
    AND = "&&"
    OR = "||"
    NOT = "!"
    
    # Assignment & Copy
    ASSIGN = "="
    COPY = "copy"
    
    # Control flow
    LABEL = "label"
    GOTO = "goto"
    IF_FALSE = "if_false"
    IF_TRUE = "if_true"
    
    # I/O
    PRINT = "print"

@dataclass
class TACInstruction:
    """Three-address code instruction (quadruple)"""
    op: TACOp
    arg1: Optional[Any] = None
    arg2: Optional[Any] = None
    result: Optional[str] = None
    
    def __str__(self):
        if self.op == TACOp.LABEL:
            return f"{self.result}:"
        elif self.op == TACOp.GOTO:
            return f"goto {self.result}"
        elif self.op == TACOp.IF_FALSE:
            return f"if_false {self.arg1} goto {self.result}"
        elif self.op == TACOp.IF_TRUE:
            return f"if_true {self.arg1} goto {self.result}"
        elif self.op == TACOp.PRINT:
            return f"print {self.arg1}"
        elif self.op == TACOp.ASSIGN:
            return f"{self.result} = {self.arg1}"
        elif self.op == TACOp.COPY:
            return f"{self.result} = {self.arg1}"
        elif self.op in [TACOp.NEG, TACOp.NOT]:
            return f"{self.result} = {self.op.value} {self.arg1}"
        elif self.arg2 is None:
            return f"{self.result} = {self.arg1}"
        else:
            return f"{self.result} = {self.arg1} {self.op.value} {self.arg2}"

class TACGenerator:
    """Generates Three-Address Code from AST"""
    
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_counter = 0
        self.label_counter = 0
    
    def new_temp(self) -> str:
        """Generate a new temporary variable"""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def new_label(self) -> str:
        """Generate a new label"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def emit(self, op: TACOp, arg1=None, arg2=None, result=None):
        """Emit a TAC instruction"""
        self.instructions.append(TACInstruction(op, arg1, arg2, result))
    
    def generate(self, ast_node) -> Optional[str]:
        """Generate TAC for an AST node, returns the result temp/var"""
        from lexer_parser import (
            Program, VarDecl, Assignment, IfStmt, WhileStmt, PrintStmt,
            BinaryOp, UnaryOp, Literal, Variable
        )
        
        if isinstance(ast_node, Program):
            for stmt in ast_node.statements:
                self.generate(stmt)
            return None
        
        elif isinstance(ast_node, VarDecl):
            if ast_node.value:
                value_temp = self.generate(ast_node.value)
                self.emit(TACOp.ASSIGN, value_temp, None, ast_node.name)
            return None
        
        elif isinstance(ast_node, Assignment):
            value_temp = self.generate(ast_node.value)
            self.emit(TACOp.ASSIGN, value_temp, None, ast_node.name)
            return None
        
        elif isinstance(ast_node, IfStmt):
            cond_temp = self.generate(ast_node.condition)
            else_label = self.new_label()
            end_label = self.new_label()
            
            self.emit(TACOp.IF_FALSE, cond_temp, None, else_label)
            
            # Then block
            for stmt in ast_node.then_block:
                self.generate(stmt)
            self.emit(TACOp.GOTO, None, None, end_label)
            
            # Else block
            self.emit(TACOp.LABEL, None, None, else_label)
            if ast_node.else_block:
                for stmt in ast_node.else_block:
                    self.generate(stmt)
            
            self.emit(TACOp.LABEL, None, None, end_label)
            return None
        
        elif isinstance(ast_node, WhileStmt):
            start_label = self.new_label()
            end_label = self.new_label()
            
            self.emit(TACOp.LABEL, None, None, start_label)
            cond_temp = self.generate(ast_node.condition)
            self.emit(TACOp.IF_FALSE, cond_temp, None, end_label)
            
            for stmt in ast_node.body:
                self.generate(stmt)
            
            self.emit(TACOp.GOTO, None, None, start_label)
            self.emit(TACOp.LABEL, None, None, end_label)
            return None
        
        elif isinstance(ast_node, PrintStmt):
            expr_temp = self.generate(ast_node.expression)
            self.emit(TACOp.PRINT, expr_temp)
            return None
        
        elif isinstance(ast_node, BinaryOp):
            left_temp = self.generate(ast_node.left)
            right_temp = self.generate(ast_node.right)
            result_temp = self.new_temp()
            
            op_map = {
                "+": TACOp.ADD, "-": TACOp.SUB, "*": TACOp.MUL,
                "/": TACOp.DIV, "%": TACOp.MOD,
                "<": TACOp.LT, ">": TACOp.GT,
                "<=": TACOp.LTE, ">=": TACOp.GTE,
                "==": TACOp.EQ, "!=": TACOp.NEQ,
                "&&": TACOp.AND, "||": TACOp.OR
            }
            
            self.emit(op_map[ast_node.op], left_temp, right_temp, result_temp)
            return result_temp
        
        elif isinstance(ast_node, UnaryOp):
            operand_temp = self.generate(ast_node.operand)
            result_temp = self.new_temp()
            
            op_map = {"-": TACOp.NEG, "!": TACOp.NOT}
            self.emit(op_map[ast_node.op], operand_temp, None, result_temp)
            return result_temp
        
        elif isinstance(ast_node, Literal):
            temp = self.new_temp()
            self.emit(TACOp.ASSIGN, ast_node.value, None, temp)
            return temp
        
        elif isinstance(ast_node, Variable):
            return ast_node.name
        
        return None

# ============================================================================
# Semantic Analyzer
# ============================================================================

class SemanticError(Exception):
    """Semantic analysis error"""
    pass

class SemanticAnalyzer:
    """Performs type checking and semantic validation"""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[str] = []
    
    def error(self, message: str):
        """Record a semantic error"""
        self.errors.append(message)
    
    def analyze(self, ast_node) -> Optional[str]:
        """Analyze AST node, returns the type ('int' or 'bool')"""
        from lexer_parser import (
            Program, VarDecl, Assignment, IfStmt, WhileStmt, PrintStmt,
            BinaryOp, UnaryOp, Literal, Variable
        )
        
        if isinstance(ast_node, Program):
            for stmt in ast_node.statements:
                self.analyze(stmt)
            return None
        
        elif isinstance(ast_node, VarDecl):
            # Check if variable already declared in current scope
            if not self.symbol_table.declare(ast_node.name, ast_node.var_type):
                self.error(f"Variable '{ast_node.name}' already declared in this scope")
            
            # Type check initialization
            if ast_node.value:
                value_type = self.analyze(ast_node.value)
                if value_type != ast_node.var_type:
                    self.error(f"Type mismatch: cannot assign {value_type} to {ast_node.var_type} variable '{ast_node.name}'")
            return None
        
        elif isinstance(ast_node, Assignment):
            symbol = self.symbol_table.lookup(ast_node.name)
            if not symbol:
                self.error(f"Undeclared variable '{ast_node.name}'")
                return None
            
            value_type = self.analyze(ast_node.value)
            if value_type != symbol.var_type:
                self.error(f"Type mismatch: cannot assign {value_type} to {symbol.var_type} variable '{ast_node.name}'")
            return None
        
        elif isinstance(ast_node, IfStmt):
            cond_type = self.analyze(ast_node.condition)
            if cond_type != 'bool':
                self.error(f"If condition must be bool, got {cond_type}")
            
            self.symbol_table.enter_scope()
            for stmt in ast_node.then_block:
                self.analyze(stmt)
            self.symbol_table.exit_scope()
            
            if ast_node.else_block:
                self.symbol_table.enter_scope()
                for stmt in ast_node.else_block:
                    self.analyze(stmt)
                self.symbol_table.exit_scope()
            return None
        
        elif isinstance(ast_node, WhileStmt):
            cond_type = self.analyze(ast_node.condition)
            if cond_type != 'bool':
                self.error(f"While condition must be bool, got {cond_type}")
            
            self.symbol_table.enter_scope()
            for stmt in ast_node.body:
                self.analyze(stmt)
            self.symbol_table.exit_scope()
            return None
        
        elif isinstance(ast_node, PrintStmt):
            self.analyze(ast_node.expression)
            return None
        
        elif isinstance(ast_node, BinaryOp):
            left_type = self.analyze(ast_node.left)
            right_type = self.analyze(ast_node.right)
            
            if ast_node.op in ['+', '-', '*', '/', '%']:
                if left_type != 'int' or right_type != 'int':
                    self.error(f"Arithmetic operator '{ast_node.op}' requires int operands")
                return 'int'
            
            elif ast_node.op in ['<', '>', '<=', '>=']:
                if left_type != 'int' or right_type != 'int':
                    self.error(f"Comparison operator '{ast_node.op}' requires int operands")
                return 'bool'
            
            elif ast_node.op in ['==', '!=']:
                if left_type != right_type:
                    self.error(f"Comparison requires same types, got {left_type} and {right_type}")
                return 'bool'
            
            elif ast_node.op in ['&&', '||']:
                if left_type != 'bool' or right_type != 'bool':
                    self.error(f"Logical operator '{ast_node.op}' requires bool operands")
                return 'bool'
        
        elif isinstance(ast_node, UnaryOp):
            operand_type = self.analyze(ast_node.operand)
            if ast_node.op == '-':
                if operand_type != 'int':
                    self.error(f"Unary minus requires int operand")
                return 'int'
            elif ast_node.op == '!':
                if operand_type != 'bool':
                    self.error(f"Logical NOT requires bool operand")
                return 'bool'
        
        elif isinstance(ast_node, Literal):
            return ast_node.lit_type
        
        elif isinstance(ast_node, Variable):
            symbol = self.symbol_table.lookup(ast_node.name)
            if not symbol:
                self.error(f"Undeclared variable '{ast_node.name}'")
                return 'int'  # Default to avoid cascade errors
            return symbol.var_type
        
        return None

# ============================================================================
# TAC Optimizer
# ============================================================================

class TACOptimizer:
    """Optimizes TAC instructions"""
    
    def __init__(self):
        pass
    
    def optimize(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Apply all optimizations"""
        instructions = self.constant_folding(instructions)
        instructions = self.dead_code_elimination(instructions)
        instructions = self.algebraic_simplification(instructions)
        return instructions
    
    def constant_folding(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Fold constant expressions"""
        optimized = []
        constants = {}  # Track constant values
        
        for instr in instructions:
            if instr.op == TACOp.ASSIGN and isinstance(instr.arg1, int):
                constants[instr.result] = instr.arg1
                optimized.append(instr)
            
            elif instr.op in [TACOp.ADD, TACOp.SUB, TACOp.MUL, TACOp.DIV, TACOp.MOD]:
                val1 = constants.get(instr.arg1, instr.arg1)
                val2 = constants.get(instr.arg2, instr.arg2)
                
                if isinstance(val1, int) and isinstance(val2, int):
                    # Perform constant folding
                    if instr.op == TACOp.ADD:
                        result = val1 + val2
                    elif instr.op == TACOp.SUB:
                        result = val1 - val2
                    elif instr.op == TACOp.MUL:
                        result = val1 * val2
                    elif instr.op == TACOp.DIV:
                        result = val1 // val2 if val2 != 0 else 0
                    elif instr.op == TACOp.MOD:
                        result = val1 % val2 if val2 != 0 else 0
                    
                    constants[instr.result] = result
                    optimized.append(TACInstruction(TACOp.ASSIGN, result, None, instr.result))
                else:
                    optimized.append(instr)
            else:
                optimized.append(instr)
        
        return optimized
    
    def dead_code_elimination(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Remove unused temporary variables"""
        # Simple DCE: remove assignments to temps that are never used
        used_vars = set()
        
        # First pass: collect all used variables
        for instr in instructions:
            if instr.arg1 and isinstance(instr.arg1, str):
                used_vars.add(instr.arg1)
            if instr.arg2 and isinstance(instr.arg2, str):
                used_vars.add(instr.arg2)
        
        # Second pass: remove assignments to unused temps
        optimized = []
        for instr in instructions:
            if instr.op == TACOp.ASSIGN and instr.result and instr.result.startswith('t'):
                if instr.result in used_vars:
                    optimized.append(instr)
            else:
                optimized.append(instr)
        
        return optimized
    
    def algebraic_simplification(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Apply algebraic identities (x+0=x, x*1=x, x*0=0)"""
        optimized = []
        
        for instr in instructions:
            if instr.op == TACOp.ADD:
                if instr.arg2 == 0:
                    optimized.append(TACInstruction(TACOp.COPY, instr.arg1, None, instr.result))
                elif instr.arg1 == 0:
                    optimized.append(TACInstruction(TACOp.COPY, instr.arg2, None, instr.result))
                else:
                    optimized.append(instr)
            
            elif instr.op == TACOp.MUL:
                if instr.arg2 == 1:
                    optimized.append(TACInstruction(TACOp.COPY, instr.arg1, None, instr.result))
                elif instr.arg1 == 1:
                    optimized.append(TACInstruction(TACOp.COPY, instr.arg2, None, instr.result))
                elif instr.arg2 == 0 or instr.arg1 == 0:
                    optimized.append(TACInstruction(TACOp.ASSIGN, 0, None, instr.result))
                else:
                    optimized.append(instr)
            
            else:
                optimized.append(instr)
        
        return optimized

# ============================================================================
# Bytecode Definition & Generator
# ============================================================================

class BytecodeOp(Enum):
    """Bytecode operations"""
    PUSH = 1        # Push constant
    LOAD = 2        # Load variable
    STORE = 3       # Store to variable
    ADD = 4
    SUB = 5
    MUL = 6
    DIV = 7
    MOD = 8
    NEG = 9
    LT = 10
    GT = 11
    LTE = 12
    GTE = 13
    EQ = 14
    NEQ = 15
    AND = 16
    OR = 17
    NOT = 18
    JUMP = 19       # Unconditional jump
    JUMP_IF_FALSE = 20
    LABEL = 21      # Label (for jumps)
    PRINT = 22
    HALT = 23

@dataclass
class BytecodeInstruction:
    """Single bytecode instruction"""
    op: BytecodeOp
    arg: Any = None
    
    def __str__(self):
        if self.arg is not None:
            return f"{self.op.name} {self.arg}"
        return self.op.name

class BytecodeGenerator:
    """Converts TAC to bytecode"""
    
    def __init__(self):
        self.bytecode: List[BytecodeInstruction] = []
        self.labels: Dict[str, int] = {}  # Label -> address
    
    def generate(self, tac_instructions: List[TACInstruction]) -> List[BytecodeInstruction]:
        """Convert TAC to bytecode"""
        # First pass: generate all bytecode without label resolution
        for instr in tac_instructions:
            if instr.op == TACOp.LABEL:
                # Record the position of this label
                self.labels[instr.result] = len(self.bytecode)
            else:
                self._generate_instruction(instr)
        
        self.bytecode.append(BytecodeInstruction(BytecodeOp.HALT))
        
        # Second pass: resolve label addresses
        self._resolve_labels()
        
        return self.bytecode
    
    def _generate_instruction(self, instr: TACInstruction):
        """Generate bytecode for a single TAC instruction"""
        if instr.op == TACOp.ASSIGN:
            if isinstance(instr.arg1, int):
                self.bytecode.append(BytecodeInstruction(BytecodeOp.PUSH, instr.arg1))
            else:
                self.bytecode.append(BytecodeInstruction(BytecodeOp.LOAD, instr.arg1))
            self.bytecode.append(BytecodeInstruction(BytecodeOp.STORE, instr.result))
        
        elif instr.op == TACOp.COPY:
            self.bytecode.append(BytecodeInstruction(BytecodeOp.LOAD, instr.arg1))
            self.bytecode.append(BytecodeInstruction(BytecodeOp.STORE, instr.result))
        
        elif instr.op in [TACOp.ADD, TACOp.SUB, TACOp.MUL, TACOp.DIV, TACOp.MOD]:
            self._load_operand(instr.arg1)
            self._load_operand(instr.arg2)
            
            op_map = {
                TACOp.ADD: BytecodeOp.ADD, TACOp.SUB: BytecodeOp.SUB,
                TACOp.MUL: BytecodeOp.MUL, TACOp.DIV: BytecodeOp.DIV,
                TACOp.MOD: BytecodeOp.MOD
            }
            self.bytecode.append(BytecodeInstruction(op_map[instr.op]))
            self.bytecode.append(BytecodeInstruction(BytecodeOp.STORE, instr.result))
        
        elif instr.op in [TACOp.LT, TACOp.GT, TACOp.LTE, TACOp.GTE, TACOp.EQ, TACOp.NEQ]:
            self._load_operand(instr.arg1)
            self._load_operand(instr.arg2)
            
            op_map = {
                TACOp.LT: BytecodeOp.LT, TACOp.GT: BytecodeOp.GT,
                TACOp.LTE: BytecodeOp.LTE, TACOp.GTE: BytecodeOp.GTE,
                TACOp.EQ: BytecodeOp.EQ, TACOp.NEQ: BytecodeOp.NEQ
            }
            self.bytecode.append(BytecodeInstruction(op_map[instr.op]))
            self.bytecode.append(BytecodeInstruction(BytecodeOp.STORE, instr.result))
        
        elif instr.op in [TACOp.AND, TACOp.OR]:
            self._load_operand(instr.arg1)
            self._load_operand(instr.arg2)
            op_map = {TACOp.AND: BytecodeOp.AND, TACOp.OR: BytecodeOp.OR}
            self.bytecode.append(BytecodeInstruction(op_map[instr.op]))
            self.bytecode.append(BytecodeInstruction(BytecodeOp.STORE, instr.result))
        
        elif instr.op in [TACOp.NEG, TACOp.NOT]:
            self._load_operand(instr.arg1)
            op_map = {TACOp.NEG: BytecodeOp.NEG, TACOp.NOT: BytecodeOp.NOT}
            self.bytecode.append(BytecodeInstruction(op_map[instr.op]))
            self.bytecode.append(BytecodeInstruction(BytecodeOp.STORE, instr.result))
        
        elif instr.op == TACOp.PRINT:
            self._load_operand(instr.arg1)
            self.bytecode.append(BytecodeInstruction(BytecodeOp.PRINT))
        
        elif instr.op == TACOp.GOTO:
            self.bytecode.append(BytecodeInstruction(BytecodeOp.JUMP, instr.result))
        
        elif instr.op == TACOp.IF_FALSE:
            self._load_operand(instr.arg1)
            self.bytecode.append(BytecodeInstruction(BytecodeOp.JUMP_IF_FALSE, instr.result))
        
        elif instr.op == TACOp.LABEL:
            pass  # Labels are handled in first pass
    
    def _load_operand(self, operand):
        """Load an operand onto the stack"""
        if isinstance(operand, int):
            self.bytecode.append(BytecodeInstruction(BytecodeOp.PUSH, operand))
        else:
            self.bytecode.append(BytecodeInstruction(BytecodeOp.LOAD, operand))
    
    def _resolve_labels(self):
        """Replace label names with actual addresses"""
        for instr in self.bytecode:
            if instr.op in [BytecodeOp.JUMP, BytecodeOp.JUMP_IF_FALSE]:
                if isinstance(instr.arg, str) and instr.arg in self.labels:
                    instr.arg = self.labels[instr.arg]

# ============================================================================
# Virtual Machine
# ============================================================================

class VirtualMachine:
    """Stack-based VM for executing bytecode"""
    
    def __init__(self):
        self.stack: List[Any] = []
        self.variables: Dict[str, Any] = {}
        self.pc = 0  # Program counter
        self.output: List[str] = []
    
    def execute(self, bytecode: List[BytecodeInstruction]):
        """Execute bytecode instructions"""
        self.pc = 0
        
        while self.pc < len(bytecode):
            instr = bytecode[self.pc]
            
            if instr.op == BytecodeOp.PUSH:
                self.stack.append(instr.arg)
            
            elif instr.op == BytecodeOp.LOAD:
                value = self.variables.get(instr.arg, 0)
                self.stack.append(value)
            
            elif instr.op == BytecodeOp.STORE:
                value = self.stack.pop()
                self.variables[instr.arg] = value
            
            elif instr.op == BytecodeOp.ADD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)
            
            elif instr.op == BytecodeOp.SUB:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)
            
            elif instr.op == BytecodeOp.MUL:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)
            
            elif instr.op == BytecodeOp.DIV:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a // b if b != 0 else 0)
            
            elif instr.op == BytecodeOp.MOD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a % b if b != 0 else 0)
            
            elif instr.op == BytecodeOp.NEG:
                a = self.stack.pop()
                self.stack.append(-a)
            
            elif instr.op == BytecodeOp.LT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a < b else 0)
            
            elif instr.op == BytecodeOp.GT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a > b else 0)
            
            elif instr.op == BytecodeOp.LTE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a <= b else 0)
            
            elif instr.op == BytecodeOp.GTE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a >= b else 0)
            
            elif instr.op == BytecodeOp.EQ:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a == b else 0)
            
            elif instr.op == BytecodeOp.NEQ:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if a != b else 0)
            
            elif instr.op == BytecodeOp.AND:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if (a and b) else 0)
            
            elif instr.op == BytecodeOp.OR:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(1 if (a or b) else 0)
            
            elif instr.op == BytecodeOp.NOT:
                a = self.stack.pop()
                self.stack.append(0 if a else 1)
            
            elif instr.op == BytecodeOp.PRINT:
                value = self.stack.pop()
                self.output.append(str(value))
                print(value)
            
            elif instr.op == BytecodeOp.JUMP:
                self.pc = instr.arg
                continue
            
            elif instr.op == BytecodeOp.JUMP_IF_FALSE:
                condition = self.stack.pop()
                if not condition:
                    self.pc = instr.arg
                    continue
            
            elif instr.op == BytecodeOp.HALT:
                break
            
            self.pc += 1

# ============================================================================
# Complete Compiler Pipeline
# ============================================================================

class TinyLangFullCompiler:
    """Complete compiler with all phases"""
    
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()
        self.tac_generator = TACGenerator()
        self.optimizer = TACOptimizer()
        self.bytecode_generator = BytecodeGenerator()
        self.vm = VirtualMachine()
    
    def compile_and_run(self, ast):
        """Complete compilation pipeline"""
        print("="*60)
        print("SEMANTIC ANALYSIS")
        print("="*60)
        self.semantic_analyzer.analyze(ast)
        
        if self.semantic_analyzer.errors:
            print("❌ Semantic Errors:")
            for error in self.semantic_analyzer.errors:
                print(f"  - {error}")
            return
        
        print("✅ No semantic errors")
        print("\nSymbol Table:")
        for symbol in self.semantic_analyzer.symbol_table.get_all_symbols():
            print(f"  {symbol.name}: {symbol.var_type} (scope {symbol.scope_level})")
        
        print("\n" + "="*60)
        print("TAC GENERATION")
        print("="*60)
        self.tac_generator.generate(ast)
        print("TAC Instructions (before optimization):")
        for i, instr in enumerate(self.tac_generator.instructions):
            print(f"  {i:3d}: {instr}")
        
        print("\n" + "="*60)
        print("OPTIMIZATION")
        print("="*60)
        original_count = len(self.tac_generator.instructions)
        optimized_tac = self.optimizer.optimize(self.tac_generator.instructions)
        optimized_count = len(optimized_tac)
        
        print(f"Original instructions: {original_count}")
        print(f"Optimized instructions: {optimized_count}")
        print(f"Reduction: {original_count - optimized_count} instructions ({((original_count-optimized_count)/original_count*100):.1f}%)")
        
        print("\nOptimized TAC:")
        for i, instr in enumerate(optimized_tac):
            print(f"  {i:3d}: {instr}")
        
        print("\n" + "="*60)
        print("BYTECODE GENERATION")
        print("="*60)
        bytecode = self.bytecode_generator.generate(optimized_tac)
        print(f"Generated {len(bytecode)} bytecode instructions:")
        for i, instr in enumerate(bytecode):
            print(f"  {i:3d}: {instr}")
        
        print("\n" + "="*60)
        print("EXECUTION")
        print("="*60)
        print("Program output:")
        self.vm.execute(bytecode)
        
        print("\nFinal variable values:")
        for var, value in sorted(self.vm.variables.items()):
            if not var.startswith('t'):  # Skip temporaries
                print(f"  {var} = {value}")

# ============================================================================
# Demo
# ============================================================================

def main():
    """Run Part 2 demo"""
    # Import from Part 1
    from lexer_parser import TinyLangCompiler
    
    # Example program
    program = """
    int x = 10;
    int y = 20;
    int z = x + y * 2;
    print(z);
    
    int counter = 0;
    while (counter < 3) {
        print(counter);
        counter = counter + 1;
    }
    """
    
    print("TinyLang Complete Compiler - Full Pipeline Demo")
    print("="*60)
    print("Source Code:")
    print(program)
    print()
    
    # Part 1: Parse
    parser = TinyLangCompiler()
    ast = parser.parse(program)
    
    # Part 2: Semantic + Codegen + Execution
    compiler = TinyLangFullCompiler()
    compiler.compile_and_run(ast)

if __name__ == "__main__":
    main()