use std::collections::{HashMap, HashSet};

use log::warn;

use crate::{evaluations::{composer::Composer, evaluation::{self, Evaluation, SQLQuery}}, helpers::queries::{self, select_component_with_subcomponents, select_component_with_tags}, io::traits::{DataSet, DataWriter, WriteModus}, structures::{Component, ComponentType}};

pub struct Evaluater<'a, S, W> 
where
    S: DataSet,
    W: DataWriter,
{
    pub dataset: &'a S,
    pub write_to: &'a mut W,
    pub  evaluations: Vec<Evaluation>,
    pub composer: Composer
}

fn calc_set_indeces(index: &usize, sizes: &Vec<usize>) -> Vec<usize>{
    let mut index = index.clone();
    let mut indeces = vec![0_usize; sizes.len()];
    let mut digit = 0;
    while index > 0 {
        let rest = index % sizes[digit];
        index = (index - rest) / sizes[digit];
        indeces[digit] = rest;
        digit += 1
    }
    return indeces
}

#[inline]
fn get_config<'a>(no: usize, sets: &'a HashMap<ComponentType, Vec<Component>>, sizes: &'a Vec<usize>) -> HashMap<ComponentType, &'a Component>{
    // sets: &HashMap<ComponentType, Vec<Component>>
    let indeces = calc_set_indeces(&no, sizes);
    let mut config: HashMap<ComponentType, &Component> = HashMap::new();
    for (index, (ctype, list)) in sets.iter().enumerate(){
        config.insert(ctype.clone(), &list[indeces[index]]);
    }
    return  config;
}

impl<S, W> Evaluater<'_, S, W> 
where
    S: DataSet,
    W: DataWriter,
{
    pub fn new<'a>(dataset: &'a S, datawriter: &'a mut W, evaluations: Vec<Evaluation>, composer: Option<Composer>)-> Result<Evaluater<'a, S, W>, String> {
        let composer = match composer{
            Some(comp) => comp,
            None => Composer::new()
        };

        let mut requested_ctypes = HashSet::new();
        for evaluation in evaluations.iter(){
            for ctype in evaluation.components_filters.keys(){
                requested_ctypes.insert(ctype.clone());
            }
        }
        for required_ctype in composer.require_component_types.iter(){
            if !requested_ctypes.contains(required_ctype) {
                warn!(target: "Runner", "Composer required component type: '{}', which is not required by evaluations", required_ctype);
                return Err(format!("Composer required component type: '{}', which is not required by evaluations", required_ctype));
            }
        }
        
        Ok(Evaluater::<'a, S, W> {
            dataset,
            write_to: datawriter,
            evaluations: evaluations,
            composer,
        })
    }

    fn create_minimal_queries(&self) -> HashMap<ComponentType, SQLQuery>{
        let mut queries: HashMap<ComponentType, SQLQuery> = HashMap::new();
        for evaluation in self.evaluations.iter(){
            for (ctype, query) in evaluation.components_filters.iter(){
                match queries.get_mut(ctype) {
                    Some(existing_query) => {
                        existing_query.push_str(" INTERSECT ");
                        existing_query.push_str(&query);
                    },
                    None => {
                        queries.insert(ctype.clone(), query.clone());
                    }
                }
            }
        }
        return queries;
    }

    fn query_sets(&self, queries: HashMap<ComponentType, SQLQuery>) -> HashMap<ComponentType, Vec<Component>>{
        let mut sets: HashMap<ComponentType, Vec<Component>> = HashMap::new();
        for (ctype, query) in queries {
            match self.dataset.find(&query) {
                Ok(result) => {
                    if result.len() == 0 {
                        warn!(target: "Runner", "Query '{query}' for component type: '{ctype}' produced no result!");
                    }
                    sets.insert(ctype.clone(), result);
                },
                Err(_err) => ()
            }
        }
        return sets;
    }

    fn evaluate(&mut self, subcomponent_sets: HashMap<ComponentType, Vec<Component>>){
        let mut sizes = Vec::with_capacity(subcomponent_sets.len());
        let mut total_combinations = 1_usize;
        for (attr, list) in subcomponent_sets.iter(){
            if list.len() == 0 {
                warn!(target: "Runner", "No match found for required attribute: '{}'", attr);
                return
            }
            sizes.push(list.len());
            total_combinations = total_combinations * list.len();
        }
        println!("RUN for {} total combinations", total_combinations);
        
        for i in 0..total_combinations {
            let config = get_config(i, &subcomponent_sets, &sizes);
            let mut component;
            let compostions_exits: bool;
            let subcomponents: Vec<(String, String)>  = config.iter().map(|(ctype, &comp)| (ctype.clone(), comp.id.clone())).collect();
            let existing = self.dataset.find(&select_component_with_subcomponents(&subcomponents)).unwrap();
            if existing.len() != 0 {
                compostions_exits = true;
                component = existing[0].clone();
            } else {
                component = Component::new();
                let mut composition = HashMap::new();
                for (ctype, &component) in config.iter(){
                    composition.insert(ctype.clone(), component.id.clone());
                }
                component.composition= Some(composition);
                compostions_exits = false;
            }
            for evaluation in self.evaluations.iter(){
                component.add_measurement(evaluation.evaluate(&self.composer, &config));
            }
            if !component.tags.contains("battery"){
                component.tags.insert("battery".to_string());
            }
            if compostions_exits{
                self.write_to.write_component(&component, &WriteModus::Update).expect("Updating Component should not be an issue!");
            }else {
                self.write_to.write_component(&component, &WriteModus::Insert).expect("Writing new Component should not be an issue!");
            }
        }
    }

    pub fn evaluate_only_taged(&mut self) {
        let mut queries = self.create_minimal_queries();
        for (ctype, query) in queries.iter_mut(){
            query.push_str(" INTERSECT ");
            query.push_str(&select_component_with_tags(&vec![ctype.clone()]));
        }
        let subcomponent_sets: HashMap<ComponentType, Vec<Component>> = self.query_sets(queries);
        self.evaluate(subcomponent_sets);
    }

    pub fn evaluate_all(&mut self) {
        let subcomponent_sets: HashMap<ComponentType, Vec<Component>> = self.query_sets(self.create_minimal_queries());
        self.evaluate(subcomponent_sets);
    } 
    
}