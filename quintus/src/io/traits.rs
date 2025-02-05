use crate::structures::Component;
use std::result::Result;
use std::vec::Vec;

pub trait DataReader {
    fn components(&self) -> Vec<Component>;
}

pub trait DataSet {
    type Output: DataSet;
    fn reduce(&self, filter: &str) -> Self::Output;
    fn find(&self, filter: &str) -> Result<Vec<Component>, impl std::error::Error>;
}

pub enum WriteModus {
    Insert,
    Update,
}
pub trait DataWriter {
    fn write_component(
        &mut self,
        component: &Component,
        modus: &WriteModus,
    ) -> Result<(), impl std::error::Error>; // -> Result<()>;
    fn delete_component(&mut self, component: &Component);
    fn clean_up(&self);
}
