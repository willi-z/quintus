from quintus.structures import Measurement, Material


class StiffMaterial(Material):
    thickness: Measurement
    E_t_xx: Measurement
    E_t_yy: Measurement | None
    nu_xy: Measurement
    G_xy: Measurement
