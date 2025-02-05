use crate::evaluations::evaluation::Evaluation;
use crate::structures::{Component, ComponentType, Unit};
use std::collections::HashMap;

use super::composer::Composer;

fn capacity_func(_composer: &Composer, components: &HashMap<ComponentType, &Component>) -> f64 {
    let active_layer = *components
        .get("active layer")
        .expect("Filter should have prevented not finding the component.");
    let areal_capacity = active_layer
        .properties
        .get("areal_capacity")
        .expect("Filter should have prevented not finding the measurement.");
    return areal_capacity.get_value_in_si();
}

pub fn capacity_evaluation() -> Evaluation {
    Evaluation::new_require_exisiting_property_only(
        "areal_capacity",
        Unit {
            unit: String::from("C/m2"),
            to_si_factor: 1.0,
        },
        HashMap::from([(
            "active layer".to_string(),
            vec!["areal_capacity".to_string()],
        )]),
        Box::new(capacity_func),
    )
}

fn active_layers_func(
    _composer: &Composer,
    components: &HashMap<ComponentType, &Component>,
) -> f64 {
    let active_layer = *components
        .get("active layer")
        .expect("Filter should have prevented not finding the component.");
    let layers = active_layer
        .properties
        .get("layers")
        .expect("Filter should have prevented not finding the measurement.");
    return layers.get_value_in_si();
}

pub fn active_layers() -> Evaluation {
    Evaluation::new_require_exisiting_property_only(
        "active_layers",
        Unit {
            unit: String::from(""),
            to_si_factor: 1.0,
        },
        HashMap::from([("active layer".to_string(), vec!["layers".to_string()])]),
        Box::new(active_layers_func),
    )
}

#[cfg(test)]
mod tests {
    use crate::{
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
    fn test_active_layers_unit() {
        let eval = active_layers();
        let unit = &eval.result_unit;
        let computed_factor = Unit::from(&unit.unit).unwrap().to_si_factor;
        assert_eq!(computed_factor, unit.to_si_factor);
    }

    #[test]
    fn test_capacity_func() {
        let mut electrode = Component::new();
        let mut areal_cap = Measurement::new();
        areal_cap.name = "areal_capacity".to_string();
        areal_cap.value = 2.3;
        areal_cap.unit = Unit::from(&"mAh/cm^2".to_string()).unwrap();
        electrode.add_measurement(areal_cap);

        let unit_new = Unit::from(&"C/m^2".to_string()).unwrap();
        let unit_old = Unit::from(&"mAh/cm^2".to_string()).unwrap();
        println!("unit fac: {}", unit_new.to_si_factor);

        let composer = Composer::new();

        let components = HashMap::from([("active layer".to_string(), &electrode)]);
        assert_eq!(
            capacity_func(&composer, &components),
            2.3 * unit_old.to_si_factor
        );

        let eval = capacity_evaluation();
        assert_eq!(
            eval.evaluate(&composer, &components).get_value_in_si(),
            2.3 * unit_old.to_si_factor
        );
    }
}
