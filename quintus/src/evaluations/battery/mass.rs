use crate::evaluations::composer::Composer;
use crate::evaluations::evaluation::Evaluation;
use crate::structures::{Component, ComponentType, Unit};
use std::collections::HashMap;

use super::electric::capacity_func;
use super::helpers::generate_layup;

pub(crate) fn electrolyte_mass_func(
    composer: &Composer,
    components: &HashMap<ComponentType, &Component>,
) -> f64 {
    let electrolyte = *components.get("electrolyte").unwrap();
    return electrolyte
        .properties
        .get("electrolyte_mass_per_capacity")
        .unwrap()
        .get_value_in_si()
        * capacity_func(composer, components);
}

pub fn electrolyte_mass_evaluation() -> Evaluation {
    Evaluation::new_require_exisiting_property_only(
        "areal_electrolyte_mass",
        Unit {
            unit: String::from("kg/m2"),
            to_si_factor: 1000.0,
        },
        HashMap::from([
            (
                "anode".to_string(),
                vec!["areal_capacity".to_string(), "active_layers".to_string()],
            ),
            (
                "cathode".to_string(),
                vec!["areal_capacity".to_string(), "active_layers".to_string()],
            ),
            (
                "electrolyte".to_string(),
                vec!["electrolyte_mass_per_capacity".to_string()],
            ),
        ]),
        Box::new(electrolyte_mass_func),
    )
}

pub(crate) fn mass_func(
    composer: &Composer,
    components: &HashMap<ComponentType, &Component>,
) -> f64 {
    let anode = *components.get("anode").unwrap();
    let cathode = *components.get("cathode").unwrap();
    let separator = *components.get("separator").unwrap();
    let foil = *components.get("foil").unwrap();
    let layup = generate_layup(&composer, anode, cathode, foil, separator);
    let mut m_sum = 0_f64;
    for component in layup {
        m_sum += component
            .properties
            .get("areal_mass")
            .unwrap()
            .get_value_in_si();
    }
    m_sum += electrolyte_mass_func(composer, components);
    return m_sum;
}

pub fn areal_mass_evaluation() -> Evaluation {
    Evaluation::new_require_exisiting_property_only(
        "areal_mass",
        Unit {
            unit: String::from("kg/m2"),
            to_si_factor: 1000.0,
        },
        HashMap::from([
            (
                "anode".to_string(),
                vec![
                    "areal_mass".to_string(),
                    "areal_capacity".to_string(),
                    "active_layers".to_string(),
                ],
            ),
            (
                "cathode".to_string(),
                vec![
                    "areal_mass".to_string(),
                    "areal_capacity".to_string(),
                    "active_layers".to_string(),
                ],
            ),
            ("foil".to_string(), vec!["areal_mass".to_string()]),
            ("separator".to_string(), vec!["areal_mass".to_string()]),
            (
                "electrolyte".to_string(),
                vec!["electrolyte_mass_per_capacity".to_string()],
            ),
        ]),
        Box::new(mass_func),
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_areal_mass_unit() {
        let eval = areal_mass_evaluation();
        let unit = &eval.result_unit;
        let computed_factor = Unit::from(&unit.unit).unwrap().to_si_factor;
        assert_eq!(computed_factor, unit.to_si_factor);
    }
}
