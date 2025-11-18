import sys
from pathlib import Path

examples_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(examples_directory))

from common import DataStoreContext

data_store_context = DataStoreContext()
data_store_context.initialize()