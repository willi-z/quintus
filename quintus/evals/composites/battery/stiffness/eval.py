from quintus.evals.composites.battery.evaluation import BatteryEvaluation
from .model import StiffMaterial
from ..constants import OUTER_ELECTRODE_LAYER, NUM_ELECTRODE_LAYERS
from quintus.structures import get_SI_value
from pymaterial.materials import IsotropicMaterial, TransverselyIsotropicMaterial
from pymaterial.combis.clt import Stackup, Ply


class StiffnessEvaluation(BatteryEvaluation):
    def __init__(self):
        super().__init__(
            "stiffness",
            "N/m^2",
            anode_cls=StiffMaterial,
            cathode_cls=StiffMaterial,
            foil_cls=StiffMaterial,
            separator_cls=StiffMaterial,
        )

    def compute_battery(
        self,
        anode: StiffMaterial,
        cathode: StiffMaterial,
        foil: StiffMaterial,
        separator: StiffMaterial,
    ) -> float:
        layup = [foil]
        for i in range(NUM_ELECTRODE_LAYERS):
            if OUTER_ELECTRODE_LAYER == "cathode":
                if i % 2 == 0:
                    layup.append(cathode)
                else:
                    layup.append(anode)
            else:
                if i % 2 == 0:
                    layup.append(anode)
                else:
                    layup.append(cathode)
            if i + 1 < NUM_ELECTRODE_LAYERS:
                layup.append(separator)
        layup.append(foil)

        plies = []
        for layer in layup:
            if layer.E_t_yy is None:
                plies.append(
                    Ply(
                        IsotropicMaterial(
                            get_SI_value(layer.E_t_xx), get_SI_value(layer.nu_xy), 1.0
                        ),
                        get_SI_value(layer.thickness),
                    )
                )
            else:
                plies.append(
                    Ply(
                        TransverselyIsotropicMaterial(
                            get_SI_value(layer.E_t_xx),
                            get_SI_value(layer.E_t_yy),
                            get_SI_value(layer.nu_xy),
                            get_SI_value(layer.G_xy),
                            1.0,
                        ),
                        get_SI_value(layer.thickness),
                    )
                )
        stackup = Stackup(plies=plies, bot_to_top=True)
        homo = stackup.calc_homogenized()
        return homo.E_l
