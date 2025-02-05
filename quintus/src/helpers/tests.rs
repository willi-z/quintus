macro_rules! test_case {($fname:expr) => (
    concat!(env!("CARGO_MANIFEST_DIR"), "/resources/test/", $fname) // assumes Linux ('/')!
)}

pub(crate) use test_case;