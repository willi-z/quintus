use crate::structures::{ComponentType, CompositionType};
use std::collections::{HashMap, HashSet};

#[derive(Debug)]
pub enum PropertyType {
    Int(usize),
    String(String),
}

pub struct Composer {
    pub ctype: CompositionType,
    pub tag_with: Vec<String>,
    pub require_component_types: HashSet<ComponentType>,
    pub properties: HashMap<String, PropertyType>,
}

impl Composer {
    pub fn new() -> Self {
        Self {
            tag_with: Vec::new(),
            ctype: CompositionType::PURE,
            require_component_types: HashSet::new(),
            properties: HashMap::new(),
        }
    }
}
