use plotters::prelude::{BitMapBackend, IntoDrawingArea, SVGBackend};
use quintus::evaluations::battery::new_battery_composer;
use quintus::io::traits::{DataReader, DataWriter, WriteModus};

use quintus::structures::{Component, Measurement, Source, Unit};
use quintus::visualization::plot_properties;
// use quintus::io::excel::*;
use quintus::{evaluations::{battery, filler}, io::{excel::ExcelData, sqlite::SQLiteData}, runner};

macro_rules! resource {($fname:expr) => (
    concat!(env!("CARGO_MANIFEST_DIR"), "/resources/test/", $fname) // assumes Linux ('/')!
)}



fn data_fill_from_exel(sql: &mut SQLiteData){
    println!("INFO: READ from EXEL File");
    let excel = ExcelData::new(resource!("excel/quintus_data_v1.0.0.xlsx"), resource!("excel/config_v1.0.0.json")).expect("EXCEL file or config was not found!");
    for component in excel.components().iter(){
        if sql.does_similar_exits(&component){
            print!(".");
            continue;
        }
        sql.write_component(component, &WriteModus::Insert).expect("Writing new component should not fail.");
    }
    println!("");
    sql.clean_up();
}

fn data_add_literature(sql: &mut SQLiteData){
    println!("INFO: ADD Literature");
    let literature = vec![
        ("Asp et al.".to_owned(), "10.1002/aesr.202000093".to_owned(), 24.0, 25.0),
        ("Saraj et al.".to_owned(), "10.1002/aesr.202300109".to_owned(), 41.0, 26.0),
        ("Meng  et al.".to_owned(), "10.1021/acs.nanolett.8b03510".to_owned(), 1.5, 0.7),
        ("Thakur & Dong".to_owned(), "A. Thakur, X. Dong, Manuf. Lett. 2020, 24,1.".to_owned(), 24.0, 0.29),
        ("Moyler".to_owned(), "K. Moyer, C. Meng, B. Marshall, O. Assal, J. Eaves, D. Perez, R. Karkkainen,
        L. Roberson, C. L. Pint, Energy Stor. Mater. 2020, 24,676".to_owned(), 35.0, 2.0),
        ("Liu".to_owned(), "10.1016/j.jpowsour.2008.09.082".to_owned(), 35.0, 3.0),
        ("Comm. Pouchcell".to_owned(), "10.1002/aesr.202000093".to_owned(), 240.0, 0.7),
    ];
    let energy_unit = Unit::from(&"Wh/kg".to_string()).expect("Should not fail!");
    let stiff_unit = Unit::from(&"GPa".to_string()).expect("Should not fail!");
    for (authors, doi, energy_val, stiffness_val) in literature{
        let mut batt_lit = Component::new();
        batt_lit.name = authors;
        batt_lit.tags.insert("battery".to_string());
        batt_lit.tags.insert("literature".to_string());
        let mut energy = Measurement::new();
        energy.name = "energy_density".to_owned();
        energy.value = energy_val;
        energy.unit = energy_unit.to_owned();
        energy.source = Some(Source{source_type: quintus::structures::SourceType::LITERATURE, remark: doi.clone()});
        batt_lit.add_measurement(energy);
        let mut stiffness = Measurement::new();
        stiffness.name = "stiffness".to_owned();
        stiffness.value = stiffness_val;
        stiffness.unit = stiff_unit.to_owned();
        stiffness.source = Some(Source{source_type: quintus::structures::SourceType::LITERATURE, remark: doi.clone()});
        batt_lit.add_measurement(stiffness);
        if sql.does_similar_exits(&batt_lit){
            continue;
        }
        sql.write_component(&batt_lit, &WriteModus::Insert).expect("Should not fail!");
    }

}

fn data_extension(sql: &mut SQLiteData){
    println!("INFO: RUN Data Extension");
    let read_from = sql.clone();
    let mut write_to = sql.clone();
    let mut runner = runner::Evaluater::new(&read_from, &mut write_to, vec![filler::active_layers(), filler::capacity_evaluation()], None).unwrap();
    runner.evaluate_all();
}

fn data_evaluation(sql: &mut SQLiteData){
    println!("INFO: RUN Data Evaluation");
    let read_from = sql.clone();
    let mut write_to = sql.clone();
    let mut runner= runner::Evaluater::new(
        &read_from, &mut write_to, 
        vec![battery::mass::areal_mass_evaluation(), battery::mass::electrolyte_mass_evaluation(), battery::stiffness::stiffness_evaluation(), battery::electric::capacity_evaluation(), battery::electric::voltage_evaluation(), battery::electric::energy_evaluation()], 
        Some(new_battery_composer(4, battery::Electrode::Anode))
    ).unwrap(); // add composer here?
    runner.evaluate_only_taged();
}

fn main() {
    let _ = env_logger::try_init();
    let mut sql = SQLiteData::new("./test.db").expect("SQL was not found!");
    data_fill_from_exel(&mut sql);
    data_add_literature(&mut sql);
    data_extension(&mut sql);
    data_evaluation(&mut sql);

    let _png= BitMapBackend::new("./plot.png", (600, 600)).into_drawing_area();
    let _svg= SVGBackend::new("./plot.svg", (600, 600)).into_drawing_area();
    let energy_unit = Unit::from(&("Wh/kg").to_string()).unwrap();
    println!("{} => {}", energy_unit.unit, energy_unit.to_si_factor);
    let stiff_unit = Unit::from(&("GPa".to_string())).unwrap();
    println!("{} => {}", stiff_unit.unit, stiff_unit.to_si_factor);
    let benchmarks = vec![
        240.0, //Wh/kg
        32.0, // GPa
    ];
    plot_properties(sql, &_png, &vec![("energy_density", &energy_unit), ("stiffness", &stiff_unit)], Some(benchmarks)).expect("Should not fail!");
    _png.present().expect("Should not Fail");
    println!("finished");
}
