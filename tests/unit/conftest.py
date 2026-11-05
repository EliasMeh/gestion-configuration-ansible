# Rend la collection importable par pytest sans l'installer (ansible_collections.nova.platform…).
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ansible", "collections"))
