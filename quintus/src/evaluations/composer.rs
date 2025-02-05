use std::collections::{HashMap, HashSet};
use crate::structures::{ComponentType, CompositionType};

pub enum PropertyType {
    Int(usize),
    String(String),
}

pub struct Composer{
    pub ctype: CompositionType,
    pub require_component_types: HashSet<ComponentType>,
    pub properties: HashMap<String, PropertyType>
}

impl Composer {
    pub fn new() -> Self{
        Self { ctype: CompositionType::PURE, require_component_types: HashSet::new(), properties: HashMap::new() }
    }
}