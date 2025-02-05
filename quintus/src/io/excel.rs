use super::traits::DataReader;
use crate::helpers::parsing::parse_tol_value;
use crate::structures::CanBeEmpty;
use crate::structures::{Component, Measurement, Source, SourceType, Unit};
use log::{info, warn};
use serde::{Deserialize, Serialize};
use std::{
    collections::{HashMap, HashSet},
    fs,
    sync::{Arc, Mutex},
};
use umya_spreadsheet::{reader::xlsx, Spreadsheet, Worksheet};

#[derive(Serialize, Deserialize, Debug)]
struct Attribute {
    value: f64,
    unit: String,
}

#[derive(Serialize, Deserialize, Clone)]
struct ConfigPointer {
    prefix: u32, // row idx where prefixes are found
    names: u32,  // row idx where measurements names are found
    units: u32,  // row idx where measurements units are found
    start: u32,  // row idx where the data is found
}

#[derive(Serialize, Deserialize, Clone)]
struct NameTransformers {
    sources: Option<HashMap<String, SourceType>>,
    properties: Option<HashMap<String, String>>,
}

impl NameTransformers {
    fn new() -> NameTransformers {
        NameTransformers {
            sources: Option::None,
            properties: Option::None,
        }
    }
    fn get_source(&self, source_type: &String) -> Source {
        let mut remark = String::new();
        if let Some(sources) = &self.sources {
            if let Some(source_type) = sources.get(source_type) {
                return Source {
                    source_type: source_type.clone(),
                    remark: remark,
                };
            }
        }
        let parsed_type = match SourceType::from(&source_type.to_string()) {
            Some(parsed_type) => parsed_type,
            None => {
                remark = String::from(source_type);
                SourceType::UNKNOWN
            }
        };
        return Source {
            source_type: parsed_type,
            remark: remark,
        };
    }
}

#[derive(Serialize, Deserialize, Clone)]
struct ConfigSheet {
    tags: Option<Vec<String>>,
    pointers: Option<ConfigPointer>,
    transformers: Option<NameTransformers>,
}

impl ConfigSheet {
    fn new() -> ConfigSheet {
        ConfigSheet {
            tags: Option::None,
            pointers: Option::None,
            transformers: Option::None,
        }
    }
}

#[derive(Serialize, Deserialize)]
struct ConfigExcel {
    ignore: Option<Vec<String>>,
    sheets: HashMap<String, ConfigSheet>,
    pointers: ConfigPointer,
    transformers: Option<NameTransformers>,
}

#[derive(Debug, Eq, Hash, PartialEq)]
struct ColorString {
    argb: String,
}

#[derive(Debug)]
struct SourceColorCoding {
    color_coding: HashMap<ColorString, Source>,
}

impl SourceColorCoding {
    fn new() -> SourceColorCoding {
        SourceColorCoding {
            color_coding: HashMap::new(),
        }
    }
    fn from_sheet(sheet: &Worksheet, transformer: &NameTransformers) -> SourceColorCoding {
        let mut result = SourceColorCoding::new();
        for row_idx in 1..=sheet.get_highest_row() {
            let cell = sheet.get_cell((1, row_idx));
            if cell.is_none() {
                break;
            }
            let cell = cell.unwrap();
            let source_color: ColorString;
            let source_value: String = String::from(cell.get_value());

            if let Some(color) = cell.get_style().get_background_color() {
                source_color = ColorString {
                    argb: color.get_argb().to_string(),
                };
            } else {
                break;
            }
            info!(target: "excel_events", "{}: '{}'", source_color.argb, source_value);
            result
                .color_coding
                .insert(source_color, transformer.get_source(&source_value));
        }
        return result;
    }
}

struct ParsingState {
    main_component_id: String,
    child_component_id: Option<String>,
}

impl ParsingState {
    fn get_current_component_id(&self) -> &String {
        if let Some(result) = &self.child_component_id {
            return result;
        } else {
            return &self.main_component_id;
        }
    }
}

pub struct ExcelData {
    workbook_mutex: Arc<Mutex<Spreadsheet>>,
    config: ConfigExcel,
}

fn is_valid_cell_value(value: &str) -> bool {
    return value != ""
        && value != "."
        && value != "-"
        && value != "#DIV/0!"
        && value != "#VALUE!"
        && !value.is_empty();
}

impl ExcelData {
    pub fn new(xlsx_path: &str, config_path: &str) -> Result<ExcelData, impl std::error::Error> {
        let woorkbook = xlsx::read(xlsx_path).expect("Cannot open file");
        let config_content = fs::read_to_string(&config_path).expect("Cannot open file");
        let config = match serde_json::from_str::<ConfigExcel>(&config_content) {
            Ok(config) => config,
            Err(err) => {
                warn!(target:"excel_events", "While parsing config file: {err:?}");
                return Err(err);
            }
        };
        Ok(ExcelData {
            workbook_mutex: Arc::new(Mutex::new(woorkbook)),
            config: config,
        })
    }

    fn read_row(&self, sheet: &Worksheet, row_idx: u32) -> Vec<String> {
        let mut result = Vec::new();
        for col_idx in 1..=sheet.get_highest_column() {
            if let Some(cell) = sheet.get_cell((col_idx, row_idx)) {
                result.push(cell.get_value().to_string());
            } else {
                result.push(String::new());
            }
        }
        result
    }

    fn read_sheet(&self, sheet: &Worksheet, config: &ConfigSheet) -> Vec<Component> {
        // let _sheet = self.workbook_mutex.lock().unwrap().worksheet_range(sheet_name).unwrap();
        let transformer = match &config.transformers {
            Some(transformer) => transformer,
            None => &NameTransformers::new(),
        };
        let source_coding = SourceColorCoding::from_sheet(sheet, transformer).color_coding;
        let pointers = config.pointers.as_ref().unwrap();
        let prefixes = self.read_row(sheet, pointers.prefix.clone());
        let column_names = self.read_row(sheet, pointers.names.clone());
        let unit: Vec<Unit> = self
            .read_row(sheet, pointers.units.clone())
            .into_iter()
            .map(|txt| Unit::from(&txt).unwrap())
            .collect();

        let mut components_lookup = HashMap::<String, Component>::new();
        for row_idx in pointers.start..=sheet.get_highest_row() {
            let mut component = Component::new();
            if config.tags.is_some() {
                let tags = config.tags.clone().unwrap();
                for tag in tags {
                    component.tags.insert(tag);
                }
            }
            let mut state = ParsingState {
                main_component_id: component.id.clone(),
                child_component_id: Option::None,
            };
            components_lookup.insert(component.id.clone(), component);

            for col_idx in 0..=sheet.get_highest_column() - 1 {
                let cell = match sheet.get_cell((col_idx + 1, row_idx)) {
                    Some(cell) => cell,
                    None => continue,
                };

                if !is_valid_cell_value(&cell.get_value()) {
                    continue;
                }
                let name: String;
                if column_names[col_idx as usize] != "" {
                    name = column_names[col_idx as usize].to_lowercase();
                } else {
                    // conected cells
                    let mut previous_name: Option<String> = Option::None;
                    for i in 1..(col_idx) {
                        let col_name_idx: usize = (col_idx - i) as usize;
                        if column_names[col_name_idx] != "" {
                            previous_name = Some(column_names[col_name_idx].to_lowercase());
                            break;
                        }
                    }
                    if previous_name.is_some() {
                        name = previous_name.unwrap();
                    } else {
                        //name = String::new();
                        panic!("No name found!");
                    }
                }

                let prefix = prefixes.get(col_idx as usize).unwrap();
                if !prefix.is_empty() {
                    if !prefix.starts_with('{') {
                        {
                            let component = components_lookup
                                .get_mut::<String>(&state.main_component_id)
                                .unwrap();
                            if component.composition.is_none() {
                                component.composition = Some(HashMap::new());
                            }
                            if component
                                .composition
                                .as_ref()
                                .unwrap()
                                .get(prefix)
                                .is_none()
                            {
                                let sub_component = Component::new();
                                component
                                    .composition
                                    .as_mut()
                                    .unwrap()
                                    .insert(prefix.clone(), sub_component.id.clone());
                                components_lookup.insert(sub_component.id.clone(), sub_component);
                            }
                        }
                        let component = components_lookup
                            .get::<String>(&state.main_component_id)
                            .unwrap();
                        state.child_component_id = Some(
                            component
                                .composition
                                .as_ref()
                                .unwrap()
                                .get(prefix)
                                .unwrap()
                                .clone(),
                        );
                    } else {
                        state.child_component_id = Option::None;
                    }
                } else {
                    state.child_component_id = Option::None;
                }

                match &name as &str {
                    "name" | "material" => {
                        let component = components_lookup
                            .get_mut::<String>(state.get_current_component_id())
                            .unwrap();
                        component.name = cell.get_value().to_string();
                    }
                    "description" => {
                        let component = components_lookup
                            .get_mut::<String>(state.get_current_component_id())
                            .unwrap();
                        component.description = cell.get_value().to_string();
                    }
                    "sources" | "comment" => {
                        let component = components_lookup
                            .get_mut::<String>(&state.main_component_id)
                            .unwrap();
                        for (_, property) in &mut component.properties {
                            if property.source.is_some() {
                                let source = property.source.as_mut().unwrap();
                                source.remark =
                                    source.remark.clone() + &cell.get_value().to_string() + "\n";
                            } else {
                                property.source = Some(Source {
                                    source_type: SourceType::LITERATURE,
                                    remark: String::from(cell.get_value().to_string() + "\n"),
                                })
                            }
                        }
                    }
                    "attributes" => {
                        let component = components_lookup
                            .get_mut::<String>(&state.get_current_component_id())
                            .unwrap();
                        let attribute_str = &cell.get_value().to_string().clone();
                        let attribute_str = attribute_str.replace("\'", "\"");
                        let attributes: Vec<HashMap<String, Attribute>> = match serde_json::from_str(
                            &attribute_str,
                        ) {
                            Ok(result) => result,
                            Err(err) => {
                                warn!(target: "excel_events", "While parsing attributs with value: '{}' (sheet: {}, cell:  {:?}),\n got {:?}", &attribute_str, sheet.get_name(), cell.get_coordinate(), err);
                                continue;
                            }
                        };
                        for map in attributes {
                            for (name, attribute) in map {
                                let mut property = Measurement::new();
                                let name = name.replace("  ", "").replace(' ', "_");
                                property.name = name.clone();
                                property.value = attribute.value.clone();
                                property.unit = Unit::from(&attribute.unit).unwrap();
                                if let Some(color) = cell.get_style().get_background_color() {
                                    if let Some(source) = source_coding.get(&ColorString {
                                        argb: color.get_argb().to_string(),
                                    }) {
                                        property.source = Some(source.clone());
                                    } else {
                                        warn!(target: "excel_events", "found undecleared color code'{}' in cell with row|col: {row_idx}|{}", color.get_argb(), col_idx+1);
                                    }
                                }
                                component.properties.insert(name, property);
                            }
                        }
                    }
                    _ => {
                        let component = components_lookup
                            .get_mut::<String>(&state.get_current_component_id())
                            .unwrap();
                        let mut property = Measurement::new();
                        property.name = name.replace("  ", "").replace(' ', "_");
                        let value_str = cell.get_value().to_string();
                        let (value, tol) = parse_tol_value(&value_str).expect(&format!(
                            "Error value str: {}, in property: {}",
                            &value_str, &property.name
                        ));
                        property.value = value;
                        property.unit = unit.get(col_idx as usize).unwrap().clone();
                        property.tolerance = tol;
                        let prefix = &prefixes[col_idx as usize];
                        if prefix.starts_with('{') {
                            warn!(target: "excel_events", "missed prefix: '{}'", prefix);
                        }

                        if let Some(color) = cell.get_style().get_background_color() {
                            if let Some(source) = source_coding.get(&ColorString {
                                argb: color.get_argb().to_string(),
                            }) {
                                property.source = Some(source.clone());
                            } else {
                                warn!(target: "excel_events", "found undecleared color code'{}' sheet: {}, cell with row|col: {row_idx}|{}", color.get_argb(), sheet.get_name() ,col_idx+1);
                            }
                        }
                        component.properties.insert(property.name.clone(), property);
                    }
                };
            }
        }
        let mut components = Vec::new();
        for (_, comp) in components_lookup {
            if !(comp.is_empty()) {
                components.push(comp);
            }
        }
        return components;
    }
}

impl DataReader for ExcelData {
    fn components(&self) -> Vec<Component> {
        let workbook = self.workbook_mutex.lock().unwrap();
        let mut result: Vec<Component> = Vec::new();
        let ignore: HashSet<&String>;
        if self.config.ignore.is_some() {
            ignore = self.config.ignore.as_ref().unwrap().into_iter().collect();
        } else {
            ignore = HashSet::new();
        }
        for sheet in workbook.get_sheet_collection() {
            // println!("INFO: Found Exel-Sheet: {}", sheet.get_name().to_string());
            if ignore.contains(&sheet.get_name().to_string()) {
                continue;
            }
            // println!("INFO: Process Exel-Sheet: {}", sheet.get_name().to_string());
            let mut sheet_config: ConfigSheet;
            let existing_config = self.config.sheets.get(&sheet.get_name().to_string());
            if existing_config.is_some() {
                sheet_config = existing_config.expect("Should not reach here").clone();
            } else {
                sheet_config = ConfigSheet::new();
            }
            if sheet_config.pointers.is_none() {
                sheet_config.pointers = Some(self.config.pointers.clone());
            }
            if sheet_config.transformers.is_none() && self.config.transformers.is_some() {
                sheet_config.transformers = self.config.transformers.clone();
            }
            result.append(&mut self.read_sheet(&sheet, &sheet_config));
        }
        return result;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::helpers::tests::test_case;

    #[test]
    fn is_valid_value() {
        let expected = vec![("", false), ("-", false)];
        for (input, expected_result) in expected {
            assert_eq!(is_valid_cell_value(input), expected_result);
        }
    }

    #[test]
    fn create_from_file() {
        let xlsx_path = test_case!("excel/quintus_data_v1.0.0.xlsx");
        let config_path = test_case!("excel/config_v1.0.0.json");
        assert!(ExcelData::new(xlsx_path, config_path).is_ok());
    }

    #[test]
    fn read_legend() {
        let xlsx_path = test_case!("excel/quintus_data_v1.0.0.xlsx");
        let config_path = test_case!("excel/config_v1.0.0.json");
        let data = ExcelData::new(xlsx_path, config_path).unwrap();
        let workbook = data.workbook_mutex.lock().unwrap();
        let sheet = workbook.get_sheet(&0).unwrap();
        let recived_coding =
            SourceColorCoding::from_sheet(&sheet, &data.config.transformers.unwrap());
        let expected_color_coding: HashMap<ColorString, Source> = HashMap::from([
            (
                ColorString {
                    argb: String::from("FFFF0000"),
                },
                Source {
                    source_type: SourceType::APPROXIMATION,
                    remark: String::new(),
                },
            ),
            (
                ColorString {
                    argb: String::from("FFFFFF00"),
                },
                Source {
                    source_type: SourceType::LITERATURE,
                    remark: String::new(),
                },
            ),
            (
                ColorString {
                    argb: String::from("FF92D050"),
                },
                Source {
                    source_type: SourceType::EXPERIMENT,
                    remark: String::new(),
                },
            ),
            (
                ColorString {
                    argb: String::from("FF00B0F0"),
                },
                Source {
                    source_type: SourceType::COMPUTATION,
                    remark: String::new(),
                },
            ),
        ]);
        assert_eq!(
            recived_coding.color_coding.len(),
            expected_color_coding.len()
        );
        for (color_expected, source_expected) in &expected_color_coding {
            let source_found = recived_coding.color_coding.get(color_expected);
            assert!(source_found.is_some());
            assert_eq!(
                source_found.unwrap().source_type,
                source_expected.source_type
            );
        }
    }

    #[test]
    fn read_all_components() {
        let xlsx_path = test_case!("excel/quintus_data_v1.0.0.xlsx");
        let config_path = test_case!("excel/config_v1.0.0.json");
        let data = ExcelData::new(xlsx_path, config_path).unwrap();
        let components_found = data.components();
        assert_eq!(components_found.len(), 133);
    }
}
