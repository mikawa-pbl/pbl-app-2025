from dataclasses import dataclass


@dataclass
class Door:
    id: str
    label: str
    coordinate: tuple[float, float]


DOORS = [
    Door("A1_1", "A-1棟ドア1", (137.41035258899626, 34.70185110733382)),
    Door("A_1", "A棟ドア1", (137.4109608495179, 34.701228083281634)),
]
