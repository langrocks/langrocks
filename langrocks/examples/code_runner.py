import logging
from pathlib import Path

from langrocks.client.code_runner import (
    CodeRunner,
    CodeRunnerContextManager,
    Content,
    ContentMimeType,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test the code runner with session
print("\nTesting CodeRunner with session")
try:
    with CodeRunner(base_url="localhost:50051") as code_runner:
        print("Runner state:", code_runner.get_state())

        # Run simple print statement
        print("\nRunning simple print statement:")
        for output in code_runner.run_python_code("print('Hello, World!')"):
            print(output.decode())

        # Test session persistence
        print("\nTesting session persistence:")
        for output in code_runner.run_python_code("x = 42"):
            print(output.decode())

        for output in code_runner.run_python_code("print(f'x = {x}')"):
            print(output.decode())

        print("\nRunner final state:", code_runner.get_state())
        print("Session data:", code_runner.get_session())
except Exception as e:
    logger.error(f"Error in CodeRunner test: {e}")

# Test the code runner context manager
print("\nTesting CodeRunnerContextManager")
try:
    with CodeRunnerContextManager("localhost:50051") as runner:
        print("Running one-off code execution:")
        for output in runner.run_code("print('One-off execution')"):
            print(output.decode())
except Exception as e:
    logger.error(f"Error in CodeRunnerContextManager test: {e}")

# Test file execution
print("\nTesting file execution")
test_file = Path("test_script.py")
test_file.write_text(
    """
def greet(name):
    return f"Hello, {name}!"

# Test the function
names = ["Alice", "Bob", "Charlie"]
for name in names:
    print(greet(name))
"""
)

try:
    with CodeRunnerContextManager("localhost:50051") as runner:
        print("Running Python file:")
        for output in runner.run_python_file(str(test_file)):
            print(output.decode())
except Exception as e:
    logger.error(f"Error in file execution test: {e}")
finally:
    test_file.unlink()

# Test error handling
print("\nTesting error handling")
try:
    with CodeRunnerContextManager("localhost:50051") as runner:
        print("Running code with syntax error:")
        code_with_syntax_error = """
print('This line is fine')
print('This line has an error'
"""
        for output in runner.run_code(code_with_syntax_error):
            print(output.decode())
except Exception as e:
    logger.error(f"Error in syntax error test: {e}")

# Test with additional files
print("\nTesting execution with additional files")
try:
    with CodeRunnerContextManager("localhost:50051") as runner:
        # Create test data file content
        data_content = b"Hello from data file!"
        data_file = Content(mime_type=ContentMimeType.TEXT, data=data_content, name="data.txt")

        # First, write the file
        code_write = """
import os
with open('data.txt', 'wb') as f:
    f.write(b'Hello from data file!')
print(f"File written successfully: {os.path.exists('data.txt')}")
"""
        print("\nWriting file:")
        for output in runner.run_code(code_write, files=[data_file]):
            print(output.decode())

        # Then read the file
        code_read = """
with open('data.txt', 'r') as f:
    content = f.read()
print(f"Content from file: {content}")
"""
        print("\nReading file:")
        for output in runner.run_code(code_read):
            print(output.decode())

except Exception as e:
    logger.error(f"Error in additional files test: {e}")

# Test matplotlib output
print("\nTesting matplotlib output")
try:
    with CodeRunnerContextManager("localhost:50051") as runner:
        plot_code = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.title('Sine Wave')
plt.savefig('plot.png')
print("Plot saved successfully")
"""
        for output in runner.run_code(plot_code):
            print(output.decode())

except Exception as e:
    logger.error(f"Error in matplotlib test: {e}")
