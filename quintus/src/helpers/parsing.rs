use crate::structures::Tolerance;
use log::warn;
use regex::Regex;

pub fn parse_tol_value(txt_with_optional_tolerance: &str) -> Result<(f64, Tolerance), ()> {
    if txt_with_optional_tolerance.contains("+/-") {
        let re =
            Regex::new(r"([-]?[0-9]*\.?[0-9]*)\s*(?:\(\+\/-\s?([-+]?[0-9]*\.?[0-9]*)\))").unwrap();
        let capture = match re.captures(txt_with_optional_tolerance) {
            Some(cap) => cap,
            None => {
                warn!(target:"tolerance value parsing", "While parsing value with tolerance '{txt_with_optional_tolerance:?}' no match found!");
                return Err(());
            }
        };
        let cap_val = capture.get(1).unwrap().as_str();
        let value = match cap_val.parse::<f64>() {
            Ok(val) => val,
            Err(_err) => {
                warn!(target:"tolerance value parsing", "While converting value str to float '{:?}'", cap_val);
                return Err(());
            }
        };
        let cap_tol = capture.get(2).unwrap().as_str();
        let tol = match cap_tol.parse::<f64>() {
            Ok(val) => val,
            Err(_err) => {
                warn!(target:"tolerance value parsing", "While converting tolerance str to float '{:?}'", cap_tol);
                return Err(());
            }
        };
        return Ok((
            value,
            Tolerance {
                max: tol.clone(),
                min: -1.0 * tol,
            },
        ));
    } else {
        let re = Regex::new(r"([-]?[0-9]*\.?[0-9]*)").unwrap();
        let capture = match re.captures(txt_with_optional_tolerance) {
            Some(cap) => cap,
            None => {
                warn!(target:"tolerance value parsing", "While parsing value '{txt_with_optional_tolerance:?}' no match found!");
                return Err(());
            }
        };
        let cap_val = capture.get(1).unwrap().as_str();
        let value = match cap_val.parse::<f64>() {
            Ok(val) => val,
            Err(_err) => {
                warn!(target:"tolerance value parsing", "While converting str to float '{:?}'", cap_val);
                return Err(());
            }
        };
        return Ok((value, Tolerance { min: 0.0, max: 0.0 }));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_values() {
        let test_cases = vec![
            (
                "3.2312 (+/-23.2312)",
                (
                    3.2312,
                    Tolerance {
                        min: -23.2312,
                        max: 23.2312,
                    },
                ),
            ),
            (
                "42 (+/- 2)",
                (
                    42.0,
                    Tolerance {
                        min: -2.0,
                        max: 2.0,
                    },
                ),
            ),
            ("32233.2312", (32233.2312, Tolerance { min: 0.0, max: 0.0 })),
            (
                "110(+/-0.8)",
                (
                    110.0,
                    Tolerance {
                        min: -0.8,
                        max: 0.8,
                    },
                ),
            ),
        ];

        for (input, expected) in test_cases {
            let result = parse_tol_value(input);
            assert!(result.is_ok());
            let result = result.unwrap();
            assert_eq!(result.0, expected.0);
            assert_eq!(result.1.min, expected.1.min);
            assert_eq!(result.1.max, expected.1.max);
        }
    }
}
