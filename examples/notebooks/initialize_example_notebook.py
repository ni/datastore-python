import sys
from pathlib import Path

examples_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(examples_directory))

from common._example_context import ExampleContext

example_context = ExampleContext()
example_context.initialize()