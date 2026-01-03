# 1. Install dependencies
pip install lark rich

# 2. Run the demo (shows everything)
python src/semantic_codegen.py

# 3. View AST only
cd src
python main.py ../tests/test_programs/fibonacci.tiny

# 4. Run tests
cd ..
python tests/test_runner.py