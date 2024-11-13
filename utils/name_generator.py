import random
from typing import Union

# Lists for random name generation
nouns = ["Explorer", "Gizmo", "Critter", "Widget", "Rocket"]
adjectives = ["Brave", "Swift", "Silent", "Radiant", "Mighty"]

def create_unique_filename(ext: Union[str, None]) -> str:
    """Generate a unique file name with an optional extension."""
    name = f"{random.choice(adjectives)}{random.choice(nouns)}"
    return f"{name}.{ext}" if ext else name
