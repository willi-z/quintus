use crate::{helpers::queries::select_component_with_properties, structures::{Component, ComponentType, Measurement, PropertyName, Source, SourceType, Unit}};
use std::collections::HashMap;

use super::composer::Composer;

pub type SQLQuery = String;


pub type EvaluationFunction = dyn Fn(&Composer, &HashMap<ComponentType, &Component>) -> f64;

pub struct Evaluation{
    pub result_name: String,
    pub result_unit: Unit,
    pub components_filters: HashMap<ComponentType, SQLQuery>,
    pub func: Box<EvaluationFunction>
}

impl Evaluation{
    pub fn new(
        result_name: &str, result_unit: Unit, 
        components_filters: HashMap<ComponentType, SQLQuery>,
        func: Box<EvaluationFunction>) -> Evaluation{
        Evaluation{
            result_name: result_name.to_string(),
            result_unit: result_unit,
            components_filters: components_filters,
            func: func,
        }
    }

    pub fn new_require_exisiting_property_only(
        result_name: &str, result_unit: Unit, 
        required_properties: HashMap<ComponentType, Vec<PropertyName>>,
        func: Box<EvaluationFunction>) -> Evaluation{
        let mut components_filter = HashMap::new();
        for (ctype, property_names) in required_properties.iter(){
            components_filter.insert(ctype.clone(), select_component_with_properties(property_names));
        }
        Evaluation{
            result_name: result_name.to_string(),
            result_unit: result_unit,
            components_filters: components_filter,
            func: func,
        }
    }
    pub fn evaluate(&self, composer: &Composer, input: &HashMap<ComponentType, &Component>) -> Measurement{
        let mut result = Measurement::new();
        result.name = self.result_name.clone();
        result.value = (self.func)(composer, input)/self.result_unit.to_si_factor;
        result.unit= self.result_unit.clone();
        result.source = Some(Source{
            source_type: SourceType::COMPUTATION,
            remark: String::new(),
        });
        return result;
    }
}