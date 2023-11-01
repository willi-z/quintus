from quintus.evals.composites.battery.evaluation import BatteryEvaluation
from quintus.evals.composites.battery.helpers import generate_layup
from .model import StiffComponent
from quintus.structures import get_SI_value
from pymaterial.materials import IsotropicMaterial, TransverselyIsotropicMaterial
from pymaterial.combis.clt import Stackup, Ply


class StiffnessEvaluation(BatteryEvaluation):
    def __init__(self):
        super().__init__(
            "stiffness",
            "N/m^2",
            anode=StiffComponent(),
            cathode=StiffComponent(),
            foil=StiffComponent(),
            separator=StiffComponent(),
        )

    def compute_battery(
        self,
        anode: StiffComponent,
        cathode: StiffComponent,
        foil: StiffComponent,
        separator: StiffComponent,
    ) -> float:
        layup = generate_layup(anode, cathode, foil, separator)

        plies = []
        for layer in layup:
            layer_properties = layer.properties
            if layer_properties.get("E_t_yy") is None:
                plies.append(
                    Ply(
                        IsotropicMaterial(
                            get_SI_value(layer_properties.get("E_t_xx")),
                            get_SI_value(layer_properties.get("nu_xy")),
                            1.0,
                        ),
                        get_SI_value(layer_properties.get("thickness")),
                    )
                )
            else:
                plies.append(
                    Ply(
                        TransverselyIsotropicMaterial(
                            get_SI_value(layer_properties.get("E_t_xx")),
                            get_SI_value(layer_properties.get("E_t_yy")),
                            get_SI_value(layer_properties.get("nu_xy")),
                            get_SI_value(layer_properties.get("G_xy")),
                            1.0,
                        ),
                        get_SI_value(layer_properties.get("thickness")),
                    )
                )
        stackup = Stackup(plies=plies, bot_to_top=True)
        homo = stackup.calc_homogenized()
        return homo.E_l
