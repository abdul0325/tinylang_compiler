from lexer_parser import TinyLangCompiler
from semantic_codegen import TinyLangFullCompiler

def repl():
    """Interactive REPL for TinyLang"""
    print("TinyLang Interactive Compiler")
    print("Type 'exit' to quit, 'help' for help")
    print("Enter multiple lines, then type 'run' to compile and execute")
    print()
    
    buffer = []
    
    while True:
        try:
            if not buffer:
                line = input(">>> ")
            else:
                line = input("... ")
            
            if line.strip() == "exit":
                break
            elif line.strip() == "help":
                print("Commands:")
                print("  run   - Compile and execute buffered code")
                print("  clear - Clear buffer")
                print("  exit  - Exit REPL")
                continue
            elif line.strip() == "clear":
                buffer = []
                print("Buffer cleared")
                continue
            elif line.strip() == "run":
                if not buffer:
                    print("Buffer is empty")
                    continue
                
                source = "\n".join(buffer)
                buffer = []
                
                # Compile and run
                parser = TinyLangCompiler()
                try:
                    ast = parser.parse(source)
                    compiler = TinyLangFullCompiler()
                    compiler.compile_and_run(ast)
                except Exception as e:
                    print(f"Error: {e}")
                
                continue
            
            buffer.append(line)
            
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nInterrupted")
            buffer = []

if __name__ == "__main__":
    repl()