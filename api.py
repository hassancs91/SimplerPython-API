from fastapi import FastAPI, Form
import subprocess
import ast
import time
import resource
import re
import errno

app = FastAPI()

# Define a safe subset of allowed Python operations
ALLOWED_MODULES = ['math', 'random']
ALLOWED_BUILTINS = ['__import__', 'abs', 'max', 'min']

def is_code_safe(code):
    """Checks if the code only uses allowed modules and built-in functions."""
    try:
        parsed_code = ast.parse(code)
    except SyntaxError:
        return False  # Invalid Python syntax

    for node in ast.walk(parsed_code):
        # Check for imports
        if isinstance(node, ast.Import):
            for module_name in node.names:
                if module_name.name not in ALLOWED_MODULES:
                    return False
        # Check for attribute access (e.g., os.system)
        elif isinstance(node, ast.Attribute):
            if node.value.id not in ALLOWED_BUILTINS:
                return False

    return True  # Code seems safe if all checks pass
def check_complexity(code):
    if len(code) > 500:  # Limit code length
        return False
    if code.count('(') > 20:  # Limit nesting depth (heuristic)
        return False
    return True
def sanitize_code(code):
    allowed_pattern = re.compile(r"^[a-zA-Z0-9\s\+\-\*\/\(\)\.\:=<>!%&\|\^~\[\]\{\}\'\"]+$")  # Adjust as needed
    if not allowed_pattern.match(code):
        return None  # Indicate invalid input
    return code


@app.post("/execute")
async def execute_code(code: str = Form(...)):
    if not code:
        return {
            "success": False,
            "message": "Please provide Python code in the 'code' field"
        }

    if not is_code_safe(code):
        return {
            "success": False,
            "message": "Code contains potentially unsafe operations"
        }

    sanitized_code = sanitize_code(code)
    if not sanitized_code:
        return {
            "success": False,
            "message": "Code contains invalid characters"
        }

    if not check_complexity(code):
        return {
            "success": False,
            "message": "Code seems too complex"
        }

    start_time = time.time()
    start_usage = resource.getrusage(resource.RUSAGE_SELF)

    try:
        # Resource Limits
        resource.setrlimit(resource.RLIMIT_CPU, (2, 2))  
        resource.setrlimit(resource.RLIMIT_AS, (50 * 1024 * 1024, 50 * 1024 * 1024))  

        result = subprocess.run(["python", "-c", sanitized_code], capture_output=True, text=True, timeout=5)
        output = result.stdout
        success = True
        message = None  

    except subprocess.TimeoutExpired:
        output = None
        success = False
        message = "Code execution timed out"

    except OSError as e:  
        if e.errno == errno.ENOMEM:
            output = None
            success = False
            message = "Code execution exceeded memory limits"
        else:
            output = None
            success = False
            message = f"An OS error occurred: {str(e)}"

    except Exception as e:
        output = None
        success = False
        message = f"An error occurred: {str(e)}"

    finally:
        end_time = time.time()
        end_usage = resource.getrusage(resource.RUSAGE_SELF)

        execution_time = end_time - start_time
        cpu_time = end_usage.ru_utime - start_usage.ru_utime  # User CPU time
        memory_usage = end_usage.ru_maxrss  # Peak memory usage (approx)

        return {
            "success": success,
            "message": message,
            "output": output,
            "execution_time": execution_time,
            "cpu_time": cpu_time,
            "memory_usage": memory_usage,  # In kilobytes
            "input_length": len(code)
        }