#!/usr/bin/env python3
"""
pytest configuration - registers custom transformers for pickle loading.
"""

import sys
from pathlib import Path

# CRITICAL: This must happen BEFORE pytest's internal imports
# Register the custom classes in a way that pickle can find them

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent / "9.SCRIPTS"
sys.path.insert(0, str(SCRIPTS_DIR))

# Import the module to get the classes
import feature_2_2_preprocessing
from feature_2_2_preprocessing import TrainOnlyOutlierClipper, ScaledOneHotEncoder

# Register in multiple places pickle might look
import __main__
__main__.TrainOnlyOutlierClipper = TrainOnlyOutlierClipper
__main__.ScaledOneHotEncoder = ScaledOneHotEncoder

# Also register in sys.modules as __main__ for pickle
sys.modules['__main__'].TrainOnlyOutlierClipper = TrainOnlyOutlierClipper
sys.modules['__main__'].ScaledOneHotEncoder = ScaledOneHotEncoder
