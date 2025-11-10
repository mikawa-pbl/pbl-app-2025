from dataclasses import dataclass

@dataclass
class Door:
    id: str
    label: str
    coordinate: Tuple[float, float]

DOORS = [
    Door("A1_1", "A-1棟ドア1", (0, 0)),
    Door("A1_2", "A-1棟ドア2", (3, 3)),
    Door("A_1", "A棟ドア1", (15, 15.4)),
]