from quintus.structures import Measurement, Material


class ElectrodeMaterial(Material):
    potential_vs_Li: Measurement
    thickness: Measurement
    density: Measurement


class WeightMaterial(Material):
    thickness: Measurement
    density: Measurement
