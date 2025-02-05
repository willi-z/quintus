#[doc(hidden)]
#[macro_export]
macro_rules! test_case {
    ($fname:expr) => {
        concat!(env!("CARGO_MANIFEST_DIR"), "/resources/test/", $fname) // assumes Linux ('/')!
    };
}

#[allow(unused_imports)]
pub(crate) use test_case;