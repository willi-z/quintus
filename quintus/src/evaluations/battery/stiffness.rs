use std::collections::HashMap;
use composites::combis::clt::{Ply, PlyOrdering, Stackup};
use composites::material::Material;

use crate::evaluations::composer::Composer;
use crate::structures::{Component, ComponentType, Unit};
use crate::evaluations::evaluation::Evaluation;

use super::helpers::generate_layup;

fn stiffness_func(composer: &Composer, components: &HashMap<ComponentType, &Component>) -> f64 {
    let anode = *components.get("anode").expect("Filter should have prevented not finding the component.");
    let cathode = *components.get("cathode").expect("Filter should have prevented not finding the component.");
    let separator = *components.get("separator").expect("Filter should have prevented not finding the component.");
    let foil = *components.get("foil").expect("Filter should have prevented not finding the component.");
    let layup = generate_layup(&composer, anode, cathode, foil, separator);
    let mut plies = Vec::with_capacity(layup.len());
    for component in layup{
        match component.properties.get("E_t_yy"){
            Some(e_t_yy) => {
                plies.push(
                    Ply::new(
                        Material::TransverselyIsotropic(
                            component.properties.get("e_t_xx").expect("Filter should have prevented not finding the property.").get_value_in_si(), 
                            e_t_yy.get_value_in_si(),
                            component.properties.get("nu_xy").expect("Filter should have prevented not finding the property.").get_value_in_si(), 
                            component.properties.get("g_xy").expect("Filter should have prevented not finding the property.").get_value_in_si(),
                            match component.properties.get("nu_yy"){
                                Some(nu_tt) => Some(nu_tt.get_value_in_si()),
                                None => None
                            }, 
                            None
                        ),
                        component.properties.get("thickness").expect("Filter should have prevented not finding the property.").get_value_in_si(),
                        0.0
                    )
                );
            }
            None => {
                plies.push(
                    Ply::new(
                        Material::Isotropic(
                            component.properties.get("e_t_xx").expect("Filter should have prevented not finding the property.").get_value_in_si(), 
                            component.properties.get("nu_xy").expect("Filter should have prevented not finding the property.").get_value_in_si(), 
                            None
                        ),
                        component.properties.get("thickness").expect("Filter should have prevented not finding the property.").get_value_in_si(),
                        0.0
                    )
                );
            }
        }
    }
    let stack = Stackup::new(plies, PlyOrdering::BotToTop);
    let scale = 1.0 / stack.thickness * 0.125;
    let abd = stack.abd;
    let em_ll = scale * (abd[(0, 0)] - abd[(0, 1)].powi(2) / abd[(1, 1)]);
    return em_ll;
}

pub fn stiffness_evaluation() -> Evaluation {
    Evaluation::new_require_exisiting_property_only(
        "stiffness",
        Unit{ unit: String::from("GPa"), to_si_factor: 1000000000000.0 },
        HashMap::from([
            ("anode".to_string(), vec!["thickness".to_string(), "e_t_xx".to_string(), "nu_xy".to_string()]),
            ("cathode".to_string(), vec!["thickness".to_string(), "e_t_xx".to_string(), "nu_xy".to_string()]),
            ("foil".to_string(), vec!["thickness".to_string(), "e_t_xx".to_string(), "nu_xy".to_string()]),
            ("separator".to_string(), vec!["thickness".to_string(), "e_t_xx".to_string(), "nu_xy".to_string()]),
        ]),
        Box::new(stiffness_func)
    )
}