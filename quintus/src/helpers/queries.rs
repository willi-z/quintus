use crate::structures::{ComponentType, PropertyName, ID};

pub fn select_component_with_properties(property_names: &Vec<PropertyName>) -> String {
    let queries: Vec<String> = property_names
        .iter()
        .map(|name| {
            format!(
                "SELECT component_id FROM measurements WHERE name = '{}'",
                name
            )
        })
        .collect::<Vec<String>>();
    return queries.join(" INTERSECT ");
}

pub fn select_component_with_tags(tag_name: &Vec<String>) -> String {
    let queries: Vec<String> = tag_name
        .iter()
        .map(|name| format!("SELECT component_id FROM tags WHERE tag = '{}'", name))
        .collect::<Vec<String>>();
    return queries.join(" INTERSECT ");
}

pub fn sub_component_has_properties(
    componenttype_propertyname_pairs: &Vec<(ComponentType, PropertyName)>,
) -> String {
    let queries: Vec<String> = componenttype_propertyname_pairs.iter().map(|(component_type, propererty_name)|{
        format!("SELECT composition_id FROM compositions INNER JOIN measurements USING (name) ON compositions.component_id = measurements.component_id WHERE component_type = '{component_type}' AND name = '{propererty_name}'")
    }).collect::<Vec<String>>();
    return queries.join(" INTERSECT ");
}

pub fn select_components_that_are_subcomponent_with_properties(
    component_type: ComponentType,
    property_names: &Vec<PropertyName>,
) -> String {
    let mut queries: Vec<String> = vec![format!(
        "SELECT component_id FROM compositions WHERE component_type = '{component_type}'"
    )];
    queries.push(select_component_with_properties(property_names));
    return queries.join(" INTERSECT ");
}

pub fn select_component_with_subcomponents(subcomponents: &Vec<(ComponentType, ID)>) -> String {
    let queries: Vec<String> = subcomponents.iter().map(|(component_type, component_id)|{
        format!("SELECT composition_id FROM compositions WHERE component_type = '{component_type}' AND component_id = '{component_id}'")
    }).collect::<Vec<String>>();
    return queries.join(" INTERSECT ");
}
