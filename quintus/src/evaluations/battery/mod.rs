use std::collections::{HashMap, HashSet};

use crate::structures::CompositionType;

use super::composer::{Composer, PropertyType};

pub enum Electrode {
    Anode,
    Cathode,
}

pub fn new_battery_composer(no_electrode_layers: usize, outer_electrode: Electrode) -> Composer {
    Composer {
        ctype: CompositionType::LAYERED,
        tag_with: vec!["battery".to_string()],
        require_component_types: HashSet::from([
            "anode".to_string(),
            "cathode".to_string(),
            "foil".to_string(),
            "separator".to_string(),
        ]),
        properties: HashMap::from([
            (
                String::from("NO_ELECTRODE_LAYERS"),
                PropertyType::Int(no_electrode_layers),
            ),
            (
                String::from("OUTER_ELECTRODE_LAYER"),
                match outer_electrode {
                    Electrode::Anode => PropertyType::String(String::from("anode")),
                    Electrode::Cathode => PropertyType::String(String::from("cathode")),
                },
            ),
        ]),
    }
}

pub mod electric;
mod helpers;
pub mod mass;
pub mod stiffness;
