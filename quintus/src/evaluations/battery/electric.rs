use crate::evaluations::composer::Composer;
use crate::evaluations::evaluation::Evaluation;
use crate::structures::{Component, ComponentType, Unit};
use std::collections::HashMap;

use super::helpers::no_of_cells_in_stack;
use super::mass::mass_func;

pub fn capacity_func(composer: &Composer, components: &HashMap<ComponentType, &Component>) -> f64 {
    let anode = *components
        .get("anode")
        .expect("Filter should have prevented not finding the component.");
    let anode_areal_capacity = anode
        .properties
        .get("areal_capacity")
        .expect("Filter should have prevented not finding the measurement.");
    let anode_maximum_usage = anode
        .properties
        .get("active_layers")
        .expect("Filter should have prevented not finding the measurement.")
        .get_value_in_si();

    let cathode = *components
        .get("cathode")
        .expect("Filter should have prevented not finding the component.");
    let cathode_areal_capacity = cathode
        .properties
        .get("areal_capacity")
        .expect("Filter should have prevented not finding the measurement.");
    let cathode_maximum_usage = cathode
        .properties
        .get("active_layers")
        .expect("Filter should have prevented not finding the measurement.")
        .get_value_in_si();

    let eff_capacity = anode_areal_capacity
        .get_value_in_si()
        .min(cathode_areal_capacity.get_value_in_si());
    let num_cells = no_of_cells_in_stack(
        composer,
        anode_maximum_usage as u8,
        cathode_maximum_usage as u8,
    );
    return eff_capacity * num_cells as f64;
}

pub fn capacity_evaluation() -> Evaluation {
    Evaluation::new_require_exisiting_property_only(
        "areal_capacity",
        Unit {
            unit: String::from("C/m2"),
            to_si_factor: 1.0,
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
        ]),
        Box::new(capacity_func),
    )
}

fn voltage_func(_composer: &Composer, components: &HashMap<ComponentType, &Component>) -> f64 {
    let anode = *components
        .get("anode")
        .expect("Filter should have prevented not finding the component.");
    let cathode = *components
        .get("cathode")
        .expect("Filter should have prevented not finding the component.");

    let anode_potential = anode
        .properties
        .get("potential_vs_li")
        .expect("Filter should have prevented not finding the measurement.");
    let cathode_potential = cathode
        .properties
        .get("potential_vs_li")
        .expect("Filter should have prevented not finding the measurement.");

    return cathode_potential.get_value_in_si() - anode_potential.get_value_in_si();
}

pub fn voltage_evaluation() -> Evaluation {
    Evaluation::new_require_exisiting_property_only(
        "voltage",
        Unit {
            unit: String::from("V"),
            to_si_factor: 1000.0,
        },
        HashMap::from([
            ("anode".to_string(), vec!["potential_vs_li".to_string()]),
            ("cathode".to_string(), vec!["potential_vs_li".to_string()]),
        ]),
        Box::new(voltage_func),
    )
}

fn energy_func(composer: &Composer, components: &HashMap<ComponentType, &Component>) -> f64 {
    let capacity = capacity_func(composer, components);
    let voltage = voltage_func(composer, components);
    let mass = mass_func(composer, components);

    return capacity * voltage / mass;
}

pub fn energy_evaluation() -> Evaluation {
    Evaluation::new_require_exisiting_property_only(
        "energy_density",
        Unit {
            unit: String::from("Wh/kg"),
            to_si_factor: 3600.0,
        },
        HashMap::from([
            (
                "anode".to_string(),
                vec![
                    "areal_mass".to_string(),
                    "areal_capacity".to_string(),
                    "active_layers".to_string(),
                    "potential_vs_li".to_string(),
                ],
            ),
            (
                "cathode".to_string(),
                vec![
                    "areal_mass".to_string(),
                    "areal_capacity".to_string(),
                    "active_layers".to_string(),
                    "potential_vs_li".to_string(),
                ],
            ),
            ("separator".to_string(), vec!["areal_mass".to_string()]),
            ("foil".to_string(), vec!["areal_mass".to_string()]),
            (
                "electrolyte".to_string(),
                vec!["electrolyte_mass_per_capacity".to_string()],
            ),
        ]),
        Box::new(energy_func),
    )
}

#[cfg(test)]
mod tests {
    use crate::{
        evaluations::battery::{new_battery_composer, Electrode},
        structures::Measurement,
    };

    use super::*;

    #[test]
    fn test_capacity_unit() {
        let eval = capacity_evaluation();
        let unit = &eval.result_unit;
        let computed_factor = Unit::from(&unit.unit).unwrap().to_si_factor;
        assert_eq!(computed_factor, unit.to_si_factor);
    }

    #[test]
    fn test_voltage_unit() {
        let eval = voltage_evaluation();
        let unit = &eval.result_unit;
        let computed_factor = Unit::from(&unit.unit).unwrap().to_si_factor;
        assert_eq!(computed_factor, unit.to_si_factor);
    }

    #[test]
    fn test_energy_density_unit() {
        let eval = energy_evaluation();
        let unit = &eval.result_unit;
        let computed_factor = Unit::from(&unit.unit).unwrap().to_si_factor;
        assert_eq!(computed_factor, unit.to_si_factor);
    }

    #[test]
    fn test_capacity_func() {
        let composer = new_battery_composer(2, Electrode::Anode);
        let mut anode = Component::new();
        let mut areal_cap = Measurement::new();
        areal_cap.name = "areal_capacity".to_string();
        areal_cap.value = 4.0;
        areal_cap.unit = Unit::from(&"mAh/cm^2".to_string()).unwrap();
        anode.add_measurement(areal_cap);

        let mut active_layer = Measurement::new();
        active_layer.name = "active_layers".to_string();
        active_layer.value = 2.0;
        active_layer.unit = Unit::from(&"1".to_string()).unwrap();
        anode.add_measurement(active_layer);

        let mut cathode = Component::new();
        let mut areal_cap = Measurement::new();
        areal_cap.name = "areal_capacity".to_string();
        areal_cap.value = 1.0;
        areal_cap.unit = Unit::from(&"mAh/cm^2".to_string()).unwrap();
        cathode.add_measurement(areal_cap);

        let mut active_layer = Measurement::new();
        active_layer.name = "active_layers".to_string();
        active_layer.value = 2.0;
        active_layer.unit = Unit::from(&"1".to_string()).unwrap();
        cathode.add_measurement(active_layer);

        let unit = Unit::from(&"mAh/cm^2".to_string()).unwrap();
        println!("unit fac: {}", unit.to_si_factor);

        let components = HashMap::from([
            ("anode".to_string(), &anode),
            ("cathode".to_string(), &cathode),
        ]);
        assert_eq!(
            capacity_func(&composer, &components),
            1.0 * unit.to_si_factor
        );

        let eval = capacity_evaluation();
        assert_eq!(
            eval.evaluate(&composer, &components).get_value_in_si(),
            1.0 * unit.to_si_factor
        );

        // c_3 0194d13ee1977510b4c89ab75094df75
        // a_1 0194d13ee05e707384032e9760522fc2
        // sep T 12µm PP-Separator
        // ElViS_p_1
        // energy_density 2365.2735758351077 Wh/kg
        // stiffness 2208309489863.2183 N/m^2
        // areal_mass 91.82565696372595 kg/m2
        // areal_capacity 390947.04000000004 C/m^2
        // voltage 2000 V
    }

    #[test]
    fn test_voltage_func() {
        let composer = new_battery_composer(2, Electrode::Anode);
        let mut anode = Component::new();
        let mut potential = Measurement::new();
        potential.name = "potential_vs_li".to_string();
        potential.value = 0.1;
        potential.unit = Unit::from(&"V".to_string()).unwrap();
        anode.add_measurement(potential);

        let mut cathode = Component::new();
        let mut potential = Measurement::new();
        potential.name = "potential_vs_li".to_string();
        potential.value = 2.1;
        potential.unit = Unit::from(&"V".to_string()).unwrap();
        cathode.add_measurement(potential);

        let unit = Unit::from(&"V".to_string()).unwrap();
        let result = voltage_func(
            &composer,
            &HashMap::from([
                ("anode".to_string(), &anode),
                ("cathode".to_string(), &cathode),
            ]),
        ) / unit.to_si_factor;
        assert_eq!(result, 2.0);
    }
}
