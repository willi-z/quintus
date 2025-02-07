use log::warn;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::fmt;
use ucum::system::UnitSystem;
use uuid::Uuid;

pub trait CanBeEmpty {
    fn is_empty(&self) -> bool;
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "UPPERCASE")]
pub enum SourceType {
    APPROXIMATION,
    EXPERIMENT,
    LITERATURE,
    COMPUTATION,
    UNKNOWN,
}

impl Default for SourceType {
    fn default() -> Self {
        SourceType::UNKNOWN
    }
}

impl fmt::Display for SourceType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            SourceType::APPROXIMATION => write!(f, "APPROXIMATION"),
            SourceType::EXPERIMENT => write!(f, "EXPERIMENT"),
            SourceType::LITERATURE => write!(f, "LITERATURE"),
            SourceType::COMPUTATION => write!(f, "COMPUTATION"),
            SourceType::UNKNOWN => write!(f, "UNKNOWN"),
        }
    }
}

impl SourceType {
    pub fn from(field: &str) -> Option<SourceType> {
        match field {
            "APPROXIMATION" => Some(SourceType::APPROXIMATION),
            "EXPERIMENT" => Some(SourceType::EXPERIMENT),
            "LITERATURE" => Some(SourceType::LITERATURE),
            "COMPUTATION" => Some(SourceType::COMPUTATION),
            "UNKNONW" => Some(SourceType::UNKNOWN),
            _ => Option::None,
        }
    }
}

#[derive(Debug, Serialize, Clone)]
pub struct Source {
    pub source_type: SourceType,
    pub remark: String,
}

impl CanBeEmpty for Source {
    fn is_empty(&self) -> bool {
        return self.source_type == SourceType::UNKNOWN && self.remark.is_empty();
    }
}

#[derive(Debug, Serialize, Clone)]
pub struct Tolerance {
    pub max: f64,
    pub min: f64,
}

impl CanBeEmpty for Tolerance {
    fn is_empty(&self) -> bool {
        return self.min == 0.0 && self.max == 0.0;
    }
}

#[derive(Debug, Serialize, Clone)]
pub struct Unit {
    pub unit: String,
    pub to_si_factor: f64,
}

impl CanBeEmpty for Unit {
    fn is_empty(&self) -> bool {
        return self.unit.is_empty() && self.to_si_factor == 1.0;
    }
}

impl Unit {
    fn get_system() -> UnitSystem<f64> {
        return UnitSystem::<f64>::default();
    }
    pub fn new() -> Unit {
        Unit {
            unit: String::new(),
            to_si_factor: 1f64,
        }
    }

    pub fn from(str: &String) -> Result<Unit, impl std::error::Error> {
        match str as &str {
            "" | "1" => Ok(Unit {
                unit: "".to_string(),
                to_si_factor: 1.0,
            }),
            "%" => Ok(Unit {
                unit: str.clone(),
                to_si_factor: 0.01,
            }),
            _ => {
                let txt_cleared = str
                    .replace("µ", "u")
                    .replace("^", "")
                    .replace("/mAh", "/(mAh)")
                    .replace("Ah", "A.h")
                    .replace("Wh", "W.h");
                let q = match Unit::get_system().parse(txt_cleared.clone().leak()) {
                    Ok(q) => q,
                    Err(err) => {
                        warn!(target:"unit_parsing", "While parsing '{txt_cleared:?}' got: {err:?}");
                        return Err(err);
                    }
                };
                Ok(Unit {
                    unit: str.clone(),
                    to_si_factor: q.magnitude(),
                })
            }
        }
    }
}

pub type ID = String;

#[derive(Debug, Serialize, Clone)]
pub struct Measurement {
    pub id: ID,
    pub name: String,
    pub value: f64,
    pub unit: Unit,
    pub tolerance: Tolerance,
    pub source: Option<Source>,
    pub conditions: Option<HashMap<String, Measurement>>,
}

impl Measurement {
    pub fn new() -> Measurement {
        Measurement {
            id: Uuid::now_v7().simple().to_string(),
            name: String::new(),
            value: 0.0,
            unit: Unit::new(),
            tolerance: Tolerance { min: 0.0, max: 0.0 },
            source: Option::None,
            conditions: Option::None,
        }
    }

    pub fn get_value_in_si(&self) -> f64 {
        self.value * self.unit.to_si_factor
    }
}

#[derive(Debug, Serialize, Clone)]
pub enum CompositionType {
    PURE,
    LAYERED,
}

impl CompositionType {
    pub fn from(field: &str) -> Option<CompositionType> {
        match field {
            "PURE" => Some(CompositionType::PURE),
            "LAYERED" => Some(CompositionType::LAYERED),
            _ => Option::None,
        }
    }
}

impl fmt::Display for CompositionType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            CompositionType::PURE => write!(f, "PURE"),
            CompositionType::LAYERED => write!(f, "LAYERED"),
        }
    }
}

pub type ComponentType = String;
pub type Tag = String;
pub type PropertyName = String;

#[derive(Debug, Serialize, Clone)]
pub struct Component {
    pub id: ID,
    pub name: String,
    pub description: String,
    pub tags: HashSet<String>,
    pub properties: HashMap<PropertyName, Measurement>,
    pub composition_type: Option<CompositionType>,
    pub composition: Option<HashMap<ComponentType, ID>>,
}

impl CanBeEmpty for Component {
    fn is_empty(&self) -> bool {
        self.name.is_empty()
            && self.description.is_empty()
            && self.properties.is_empty()
            && self.composition.is_none()
            && self.composition_type.is_none()
    }
}

impl Component {
    pub fn new() -> Component {
        Component {
            id: Uuid::now_v7().simple().to_string(),
            name: String::new(),
            description: String::new(),
            tags: HashSet::new(),
            properties: HashMap::new(),
            composition: Option::None,
            composition_type: Option::None,
        }
    }

    pub fn add_measurement(&mut self, measure: Measurement) {
        self.properties.insert(measure.name.clone(), measure);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn unit_parsing() {
        let txt = String::from("mA");
        let unit = Unit::from(&txt);
        assert!(unit.is_ok());
        assert_eq!(unit.unwrap().to_si_factor, 0.001f64);

        let txt = String::from("mA.h/g");
        let unit = Unit::from(&txt);
        assert!(unit.is_ok());
        //assert_eq!(unit.unwrap().to_si_factor, 0.001f64);

        let txt = String::from("g/mAh");
        let unit = Unit::from(&txt);
        assert!(unit.is_ok());
        assert_eq!(unit.unwrap().to_si_factor, 1.0 / 3.6);
    }
}
