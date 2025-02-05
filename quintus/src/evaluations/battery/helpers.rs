use crate::{
    evaluations::composer::{Composer, PropertyType},
    structures::{Component, ComponentType},
};

pub fn generate_layup_ids(composer: &Composer) -> Vec<ComponentType> {
    let outer_electrode = match composer
        .properties
        .get("OUTER_ELECTRODE_LAYER")
        .expect("Composer for Battery should have Property: 'OUTER_ELECTRODE_LAYER'")
    {
        PropertyType::String(txt) => txt,
        _ => return Vec::new(),
    };
    let num_electrode_layers = match composer
        .properties
        .get("NO_ELECTRODE_LAYERS")
        .expect("Composer for Battery should have Property: 'NO_ELECTRODE_LAYERS'")
    {
        PropertyType::Int(num) => num,
        _ => return Vec::new(),
    };
    let mut layup = Vec::with_capacity(num_electrode_layers + 2 + num_electrode_layers / 2);
    layup.push(String::from("foil"));
    for i in 0..*num_electrode_layers {
        if outer_electrode == "cathode" {
            if i % 2 == 0 {
                layup.push(String::from("cathode"));
            } else {
                layup.push(String::from("anode"));
            }
        } else {
            if i % 2 == 0 {
                layup.push(String::from("anode"));
            } else {
                layup.push(String::from("cathode"));
            }
        }
        if i + 1 < *num_electrode_layers {
            layup.push(String::from("separator"));
        }
    }

    layup.push(String::from("foil"));
    return layup;
}

pub fn generate_layup<'a>(
    composer: &Composer,
    anode: &'a Component,
    cathode: &'a Component,
    foil: &'a Component,
    separator: &'a Component,
) -> Vec<&'a Component> {
    let ids = generate_layup_ids(composer);
    let mut layup = Vec::with_capacity(ids.len());
    for id in ids {
        match id.as_str() {
            "anode" => layup.push(anode),
            "cathode" => layup.push(cathode),
            "foil" => layup.push(foil),
            "separator" => layup.push(separator),
            &_ => todo!(),
        }
    }
    return layup;
}

pub fn no_of_cells_in_stack(
    composer: &Composer,
    anode_no_active_layers: u8,
    cathode_no_active_layers: u8,
) -> u32 {
    let layup = generate_layup_ids(composer);
    let num_electrode_layers = match composer
        .properties
        .get("NO_ELECTRODE_LAYERS")
        .expect("Composer for Battery should have Property: 'NO_ELECTRODE_LAYERS'")
    {
        PropertyType::Int(num) => num.clone(),
        _ => return 0,
    };
    let mut usages = vec![0_u8; num_electrode_layers];
    let mut index_layer = 0_usize;
    let mut num_cells = 0_u32;
    while layup[index_layer] != String::from("anode")
        && layup[index_layer] != String::from("cathode")
    {
        index_layer += 1
    }
    for idx_electrode in 0..num_electrode_layers - 1 {
        // ignore last layer
        let mut index_layer_next_electrode = index_layer + 1;
        while layup[index_layer_next_electrode] != String::from("anode")
            && layup[index_layer_next_electrode] != String::from("cathode")
        {
            index_layer_next_electrode += 1
        }
        if layup[index_layer] == layup[index_layer_next_electrode] {
            index_layer = index_layer_next_electrode;
            continue;
        }
        usages[idx_electrode] += 1;
        usages[idx_electrode + 1] += 1;
        num_cells += 1;

        if usages[idx_electrode]
            > match layup[index_layer].as_str() {
                "anode" => anode_no_active_layers,
                "cathode" => cathode_no_active_layers,
                _ => 0,
            }
        {
            usages[idx_electrode] -= 1;
            usages[idx_electrode + 1] -= 1;
            num_cells -= 1;
        }
        index_layer = index_layer_next_electrode;
    }
    return num_cells;
}

#[cfg(test)]
mod tests {
    use crate::evaluations::battery::{new_battery_composer, Electrode};

    use super::*;

    #[test]
    fn test_layup() {
        let test_sets = vec![
            (
                2,
                Electrode::Anode,
                vec!["foil", "anode", "separator", "cathode", "foil"],
            ),
            (
                3,
                Electrode::Cathode,
                vec![
                    "foil",
                    "cathode",
                    "separator",
                    "anode",
                    "separator",
                    "cathode",
                    "foil",
                ],
            ),
            (
                4,
                Electrode::Cathode,
                vec![
                    "foil",
                    "cathode",
                    "separator",
                    "anode",
                    "separator",
                    "cathode",
                    "separator",
                    "anode",
                    "foil",
                ],
            ),
            (
                5,
                Electrode::Anode,
                vec![
                    "foil",
                    "anode",
                    "separator",
                    "cathode",
                    "separator",
                    "anode",
                    "separator",
                    "cathode",
                    "separator",
                    "anode",
                    "foil",
                ],
            ),
        ];

        for (el_layers, outer_electrode, expected_layup) in test_sets {
            let composer = new_battery_composer(el_layers, outer_electrode);
            let generated_layup = generate_layup_ids(&composer);
            assert_eq!(expected_layup.len(), generated_layup.len());
            for (&expected, recieved) in expected_layup.iter().zip(generated_layup.iter()) {
                assert_eq!(expected, recieved);
            }
        }
    }

    #[test]
    fn test_no_of_cells_in_stack() {
        let test_sets = vec![
            (2, Electrode::Anode, 1_u8, 2_u8, 1_u32),
            (3, Electrode::Cathode, 2_u8, 1_u8, 2_u32),
            (3, Electrode::Cathode, 1_u8, 1_u8, 1_u32),
            (4, Electrode::Cathode, 2_u8, 2_u8, 3_u32),
            (5, Electrode::Anode, 2_u8, 2_u8, 4_u32),
            (5, Electrode::Anode, 1_u8, 2_u8, 3_u32),
            (5, Electrode::Anode, 2_u8, 1_u8, 2_u32),
            (5, Electrode::Anode, 1_u8, 1_u8, 2_u32),
        ];

        for (el_layers, outer_electrode, anode_alayers, cathode_alayers, expected_cells) in
            test_sets
        {
            let composer = new_battery_composer(el_layers, outer_electrode);
            let computed_cells = no_of_cells_in_stack(&composer, anode_alayers, cathode_alayers);
            assert_eq!(computed_cells, expected_cells);
        }
    }
}
