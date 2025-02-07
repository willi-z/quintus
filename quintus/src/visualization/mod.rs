use core::f64;

use plotters::{
    coord::Shift,
    prelude::{
        ChartBuilder, Circle, DrawingArea, DrawingBackend, FontStyle, PathElement, Polygon, Text,
        TextStyle, BLACK,
    },
    style::{
        text_anchor::{HPos, Pos, VPos},
        Color, FontDesc, FontFamily, FontTransform, IntoFont, IntoTextStyle, RGBAColor, ShapeStyle,
        WHITE,
    },
};

use crate::{
    helpers::queries::select_component_with_properties, io::traits::DataSet, structures::Unit,
};

pub fn plot_properties<DS: DataSet, DB: DrawingBackend>(
    dataset: DS,
    root_drawing_area: &DrawingArea<DB, Shift>,
    properties: &Vec<(&str, &Unit, Option<&str>)>,
    benchmarks: Option<Vec<f64>>,
) -> Result<(), Box<dyn std::error::Error>>
where
    <DB as DrawingBackend>::ErrorType: 'static,
{
    let width = root_drawing_area.get_pixel_range().0.max().unwrap();
    let height = root_drawing_area.get_pixel_range().0.max().unwrap();
    let critical_length = width.min(height) + 1;
    let scale: i32 = critical_length / 200;
    // println!("INFO: Plotting Results...");
    let lit_colors: Vec<RGBAColor> = vec![
        RGBAColor(52, 107, 26, 1.0),
        RGBAColor(188, 90, 148, 1.0),
        RGBAColor(54, 154, 204, 1.0),
        RGBAColor(124, 221, 67, 1.0),
        RGBAColor(248, 225, 111, 1.0),
        RGBAColor(244, 137, 95, 1.0),
        RGBAColor(222, 50, 76, 1.0),
    ];

    let mut generated: Vec<(String, Vec<f64>)> = Vec::new();
    let mut literature: Vec<(String, Vec<f64>)> = Vec::new();
    let property_names: Vec<String> = properties
        .iter()
        .map(|&(property_name, _, _)| property_name.to_string())
        .collect();

    //println!("INFO: Finding Data");
    for comp in dataset
        .find(&select_component_with_properties(&property_names))
        .expect("Query should not fail!")
    {
        let values: Vec<f64> = properties
            .iter()
            .map(|&(property_name, unit, _)| {
                &comp
                    .properties
                    .get(property_name)
                    .unwrap()
                    .get_value_in_si()
                    / unit.to_si_factor
            })
            .collect();
        if comp.tags.contains("literature") {
            literature.push((comp.name.to_string(), values));
        } else {
            generated.push((comp.name.to_string(), values))
        }
    }

    //println!("INFO: Preparing Label and Ranges");
    root_drawing_area.fill(&WHITE).expect("Should work!");

    let (x_prop, x_unit, x_alt_label) = properties[0];
    let (y_prop, y_unit, y_alt_label) = properties[1];
    let mut x_data = Vec::with_capacity(generated.len() + literature.len());
    let mut y_data = Vec::with_capacity(generated.len() + literature.len());
    for data in generated.iter() {
        x_data.push(data.1[0]);
        y_data.push(data.1[1]);
    }

    let x_label: String;
    if x_alt_label.is_some() {
        x_label = x_alt_label.unwrap().to_string();
    } else {
        x_label = format!("{} [{}]", x_prop, x_unit.unit);
    }

    let y_label: String;
    if x_alt_label.is_some() {
        y_label = y_alt_label.unwrap().to_string();
    } else {
        y_label = format!("{} [{}]", y_prop, y_unit.unit);
    }

    let mut x_max = x_data
        .iter()
        .fold(f64::NEG_INFINITY, |arg0: f64, other: &f64| {
            f64::max(arg0, *other)
        }) as f32;
    let mut y_max = y_data
        .iter()
        .fold(f64::NEG_INFINITY, |arg0: f64, other: &f64| {
            f64::max(arg0, *other)
        }) as f32;
    //println!("Plot max: {}|{}", x_max, y_max);
    if benchmarks.is_some() {
        let benches = benchmarks.as_ref().unwrap();
        x_max = x_max.max(benches[0] as f32);
        y_max = y_max.max(benches[1] as f32);
    }

    //println!("Plot max: {}|{} (new)", x_max, y_max);
    let x_digits = x_max.log10().floor();
    let y_digits = y_max.log10().floor();
    x_max = ((x_max / (5.0 * x_digits)).ceil() + 1.0) * 5.0 * x_digits;
    y_max = ((y_max / (5.0 * y_digits)).ceil() + 1.0) * 5.0 * y_digits;

    //println!("Plot max: {}|{} (new)", x_max, y_max);

    //println!("INFO: Setup Chart");
    let mut chart = ChartBuilder::on(root_drawing_area)
        //.caption("QUINTUS", ("sans-serif", 30).into_font())
        .margin_left(7 * scale + 7)
        .margin_bottom(5 * scale + 5)
        .margin_top(2 * scale)
        .margin_right(3 * scale + 3)
        .x_label_area_size(5 * scale)
        .y_label_area_size(5 * scale)
        .build_cartesian_2d(0.0..x_max, 0.0..y_max)?;

    if benchmarks.is_some() {
        let benches = benchmarks.as_ref().unwrap();
        let mut area_of_multifunctionality_vertices = vec![
            (benches[0] as f32, 0.0),
            (x_max, 0.0),
            (x_max, y_max),
            (0.0, y_max),
            (0.0, benches[1] as f32),
        ];
        let area_color = RGBAColor(1, 176, 77, 1.0);
        chart.draw_series(std::iter::once(Polygon::new(
            area_of_multifunctionality_vertices.clone(),
            area_color.mix(0.2),
        )))?;
        area_of_multifunctionality_vertices.push(area_of_multifunctionality_vertices[0]);
        chart.draw_series(std::iter::once(PathElement::new(
            area_of_multifunctionality_vertices,
            area_color,
        )))?;

        let area_label_color = RGBAColor(0, 73, 32, 1.0);
        let caption_font = FontDesc::new(FontFamily::Serif, (6 * scale).into(), FontStyle::Bold);
        let caption_style = TextStyle {
            font: caption_font,
            color: area_label_color.to_backend_color(),
            pos: Pos::new(HPos::Center, VPos::Center),
        };
        root_drawing_area.draw_text(
            "Multifunktionali-",
            &caption_style,
            (width / 2 + 20 * scale, height / 2),
        )?;
        root_drawing_area.draw_text(
            "tätsbereich",
            &caption_style,
            (width / 2 + 20 * scale, height / 2 + 5 * scale),
        )?;
    }

    //println!("INFO: Configure Axis and Mesh");
    chart
        .configure_mesh()
        .x_label_formatter(&|v| format!("{:.1}", v).replace('.', ","))
        .y_label_formatter(&|v| format!("{:.1}", v).replace('.', ","))
        .x_label_style(("serif", 4 * scale).with_color(BLACK))
        .y_label_style(("serif", 4 * scale).with_color(BLACK))
        .draw()?;

    //println!("INFO: print QUNITUS result");
    chart
        .draw_series(generated.iter().map(|(_, v)| {
            plotters::element::EmptyElement::at((v[0] as f32, v[1] as f32))
                + Circle::new(
                    (0, 0),
                    1 * scale + 1,
                    ShapeStyle {
                        color: RGBAColor(119, 123, 132, 1.0),
                        filled: true,
                        stroke_width: 0,
                    },
                )
                + Circle::new(
                    (0, 0),
                    1 * scale + 1,
                    ShapeStyle {
                        color: RGBAColor(90, 90, 90, 1.0),
                        filled: false,
                        stroke_width: 1,
                    },
                )
        }))?
        .label("QUNITUS")
        .legend(|(x, y)| {
            plotters::element::EmptyElement::at((x, y))
                + Circle::new(
                    (0, 0),
                    2 * (scale - 1),
                    ShapeStyle {
                        color: RGBAColor(119, 123, 132, 1.0),
                        filled: true,
                        stroke_width: 0,
                    },
                )
                + Circle::new(
                    (0, 0),
                    2 * (scale - 1),
                    ShapeStyle {
                        color: RGBAColor(90, 90, 90, 1.0),
                        filled: false,
                        stroke_width: 1,
                    },
                )
        });

    let mut color: &RGBAColor;
    //println!("INFO: Draw Literature");
    for (idx, (label, v)) in literature.iter().enumerate() {
        color = &lit_colors[idx];
        chart
            .draw_series(vec![v].iter().map(|&v| {
                plotters::element::EmptyElement::at((v[0] as f32, v[1] as f32))
                    + Circle::new(
                        (0, 0),
                        1 * scale + 1,
                        ShapeStyle {
                            color: color.clone(),
                            filled: true,
                            stroke_width: 0,
                        },
                    )
                    + Circle::new(
                        (0, 0),
                        1 * scale + 1,
                        ShapeStyle {
                            color: RGBAColor(0, 0, 0, 1.0),
                            filled: false,
                            stroke_width: 1,
                        },
                    )
            }))?
            .label(label)
            .legend(|(x, y)| {
                return plotters::element::EmptyElement::at((x, y))
                    + Circle::new(
                        (0, 0),
                        2 * (scale - 1),
                        ShapeStyle {
                            color: color.clone(),
                            filled: true,
                            stroke_width: 0,
                        },
                    )
                    + Circle::new(
                        (0, 0),
                        2 * (scale - 1),
                        ShapeStyle {
                            color: RGBAColor(0, 0, 0, 1.0),
                            filled: false,
                            stroke_width: 1,
                        },
                    );
            });
    }

    //println!("INFO: Draw Legend");
    let label_font = FontDesc::new(FontFamily::Serif, (6 * scale).into(), FontStyle::Normal);
    let label_style = TextStyle {
        font: label_font,
        color: BLACK.to_backend_color(),
        pos: Pos::new(HPos::Left, VPos::Top),
    };
    chart
        .configure_series_labels()
        .position(plotters::chart::SeriesLabelPosition::UpperRight)
        .label_font(label_style)
        .background_style(&WHITE.mix(1.0))
        .border_style(&BLACK)
        .draw()?;

    let caption_font = FontDesc::new(FontFamily::Serif, (6 * scale).into(), FontStyle::Bold);
    let caption_style = TextStyle {
        font: caption_font,
        color: BLACK.to_backend_color(),
        pos: Pos::new(HPos::Center, VPos::Center),
    };
    root_drawing_area.draw_text(
        &x_label,
        &caption_style,
        (width / 2 + 2 * scale + 1, height - 2 * scale - 2),
    )?;
    root_drawing_area.draw_text(
        &y_label,
        &caption_style.transform(FontTransform::Rotate270),
        (2 * scale, height / 2 - 3 * scale),
    )?;

    //println!("INFO: Finished Plotting");
    Ok(())
}
