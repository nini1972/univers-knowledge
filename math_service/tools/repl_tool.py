import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class PythonREPLInput(BaseModel):
    code: str = Field(..., description="Valid Python code to execute. Can use sympy, pint, math, etc. Must print outputs using print().")

class PythonREPLTool(BaseTool):
    name: str = "Python REPL"
    description: str = (
        "Executes Python code in a separate subprocess and returns the standard output (stdout) and standard error (stderr). "
        "Use this to run mathematical calculations, verify equations symbolically with sympy, "
        "or evaluate numerical results. Print any value you want to see using print()."
    )
    args_schema: Type[BaseModel] = PythonREPLInput

    def _run(self, code: str) -> str:
        # Create a temporary file to hold the code
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as f:
            f.write(code)
            temp_path = Path(f.name)

        try:
            # Run the Python script in a subprocess
            result = subprocess.run(
                [sys.executable, str(temp_path)],
                capture_output=True,
                text=True,
                timeout=15  # Limit execution time to 15s to prevent infinite loops
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            output = []
            if stdout:
                output.append(f"--- stdout ---\n{stdout}")
            if stderr:
                output.append(f"--- stderr ---\n{stderr}")
                
            if not output:
                return "Execution completed successfully with no output. Remember to use print() to see results."
            return "\n\n".join(output)
        except subprocess.TimeoutExpired:
            return "ERROR: Execution timed out (exceeded 15 seconds limit). Avoid infinite loops."
        except Exception as e:
            return f"ERROR: Failed to run subprocess: {e}"
        finally:
            # Clean up the temp file
            try:
                temp_path.unlink()
            except Exception:
                pass
