use core::f64;

use plotters::{coord::Shift, prelude::{ChartBuilder, Circle, DrawingArea, DrawingBackend, PathElement, Polygon, BLACK, RED}, style::{Color, RGBAColor, ShapeStyle, WHITE}};

use crate::{helpers::queries::select_component_with_properties, io::traits::DataSet, structures::Unit};

pub fn plot_properties<DS: DataSet, DB: DrawingBackend>(dataset: DS, root_drawing_area: &DrawingArea<DB, Shift>, properties: &Vec<(&str, &Unit)>, benchmarks: Option<Vec<f64>>) -> Result<(), Box<dyn std::error::Error>>
where <DB as DrawingBackend>::ErrorType: 'static
{
    println!("INFO: Plotting Results...");
    let lit_colors: Vec<RGBAColor> = vec![RGBAColor(52, 107, 26, 1.0), RGBAColor(188, 90, 148, 1.0), RGBAColor(54, 154, 204, 1.0), RGBAColor(124, 221, 67, 1.0), RGBAColor(248, 225, 111, 1.0), RGBAColor(244, 137, 95, 1.0), RGBAColor(222, 50, 76, 1.0)];
    let mut generated :Vec<(String,Vec<f64>)>= Vec::new();
    let mut literature: Vec<(String, Vec<f64>)> = Vec::new();
    let property_names: Vec::<String> = properties.iter().map(|&(property_name, _unit)|property_name.to_string()).collect();
    println!("INFO: Finding Data");
    for comp in dataset.find(&select_component_with_properties(&property_names)).expect("Query should not fail!"){
        let values: Vec<f64> = properties.iter().map(|&(property_name, unit)| &comp.properties.get(property_name).unwrap().get_value_in_si()/unit.to_si_factor).collect();
        if comp.tags.contains("literature") {
            literature.push((comp.name.to_string(), values));
        } else {
            generated.push((comp.name.to_string(), values))
        }
    }
    
    println!("INFO: Preparing Label and Ranges");
    root_drawing_area.fill(&WHITE).expect("Should work!");

    let (x_label, x_unit) = properties[0];
    let (y_label, y_unit) = properties[1];
    let mut x_data = Vec::with_capacity(generated.len()+literature.len());
    let mut y_data = Vec::with_capacity(generated.len()+literature.len());
    for data in generated.iter(){
        x_data.push(data.1[0]);
        y_data.push(data.1[1]);
    }

    let x_label = format!("{} [{}]", x_label, x_unit.unit);
    let y_label = format!("{} [{}]", y_label, y_unit.unit);

    let mut x_max = x_data.iter().fold(f64::NEG_INFINITY, |arg0: f64, other: &f64| f64::max(arg0, *other)) as f32;
    let mut y_max = y_data.iter().fold(f64::NEG_INFINITY, |arg0: f64, other: &f64| f64::max(arg0, *other)) as f32;
    println!("Plot max: {}|{}", x_max,y_max);
    if benchmarks.is_some(){
        let benches = benchmarks.as_ref().unwrap();
        x_max = x_max.max(benches[0] as f32);
        y_max = y_max.max(benches[1] as f32);
    }
    println!("Plot max: {}|{} (new)", x_max,y_max);
    
    
    println!("INFO: Setup Chart");
    let mut chart = ChartBuilder::on(root_drawing_area)
        //.caption("QUINTUS", ("sans-serif", 30).into_font())
        .margin_right(10)
        .x_label_area_size(30)
        .y_label_area_size(30)
        .build_cartesian_2d(0.0..x_max, 0.0..y_max)?;

    println!("INFO: Configure Axis and Mesh");
    chart
        .configure_mesh()
        .x_desc(x_label)
        .y_desc(y_label)
        .draw()?;

    println!("INFO: Draw Border");
    chart
        .configure_series_labels()
        .background_style(&WHITE.mix(0.8))
        .border_style(&BLACK)
        .draw()?;

    println!("INFO: Draw Series 1 inner");
    chart.draw_series(
        generated.iter()
            .map(|(_, v)| Circle::new((v[0] as f32, v[1] as f32), 3, ShapeStyle{color: RGBAColor(119, 123, 132, 1.0), filled: true, stroke_width: 0})),
    )?;
    println!("INFO: Draw Series 1 outer");
    chart.draw_series(
        generated.iter()
            .map(|(_, v)| Circle::new((v[0] as f32, v[1] as f32), 3, ShapeStyle{color: RGBAColor(0,0,0,1.0), filled: false, stroke_width: 1})),
    )?;

    println!("INFO: Draw Series 2 inner");
    chart.draw_series(
        literature.iter().enumerate()
            .map(|(idx, (_,v))| Circle::new((v[0] as f32, v[1] as f32), 4, ShapeStyle{color: lit_colors[idx], filled: true, stroke_width: 0})),
    )?;
    println!("INFO: Draw Series 2 outer");
    chart.draw_series(
        literature.iter().enumerate()
            .map(|(_idx, (_,v))| Circle::new((v[0] as f32, v[1] as f32), 4, ShapeStyle{color: RGBAColor(0,0,0,1.0), filled: false, stroke_width: 1})),
    )?;

    if benchmarks.is_some(){
        let benches = benchmarks.as_ref().unwrap();
        let mut area_of_multifunctionality_vertices = vec![
            (benches[0] as f32, 0.0), 
            (x_max, 0.0), 
            (x_max, y_max), 
            (0.0, y_max), 
            (0.0, benches[1] as f32)
        ];
        chart.draw_series(std::iter::once(Polygon::new(
            area_of_multifunctionality_vertices.clone(),
            RED.mix(0.2),
        )))?;
        area_of_multifunctionality_vertices.push(area_of_multifunctionality_vertices[0]);
        chart.draw_series(std::iter::once(PathElement::new(area_of_multifunctionality_vertices, RED)))?;
    }
    
    println!("INFO: Finished Plotting");
    Ok(())
}