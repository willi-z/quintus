use super::traits::{DataReader, DataSet, DataWriter, WriteModus};
use crate::structures::{
    Component, CompositionType, Measurement, Source, SourceType, Tolerance, Unit,
};
use log::{info, warn};
use rusqlite::{params, Connection, Result};
use sha2::{Digest, Sha256};
use std::{
    collections::{HashMap, HashSet},
    path::Path,
    sync::{Arc, Mutex},
};

#[derive(Clone)]
pub struct SQLiteData {
    conn: Arc<Mutex<Connection>>,
    idx_view: String,
}

impl SQLiteData {
    pub fn new(path: &str) -> Result<SQLiteData> {
        let is_new: bool;
        if Path::new(path).exists() {
            is_new = false;
        } else {
            is_new = true;
        }
        let conn = Connection::open(path)?;
        let sqlite = SQLiteData {
            conn: Arc::new(Mutex::new(conn)),
            idx_view: String::from("all_components"),
        };
        if is_new {
            sqlite.create_tables()?;
        }
        sqlite.create_view(Option::None);
        Ok(sqlite)
    }

    pub fn from_connection(conn: Connection) -> Result<SQLiteData> {
        let sqlite = SQLiteData {
            conn: Arc::new(Mutex::new(conn)),
            idx_view: String::from("all_components"),
        };
        sqlite.create_tables()?;
        sqlite.create_view(Option::None);
        Ok(sqlite)
    }

    fn create_view(&self, filter: Option<String>) {
        let conn = self.conn.lock().unwrap();
        let sql: String;
        if filter.is_none() {
            sql = format!(
                "CREATE TEMP VIEW IF NOT EXISTS {} (id) AS
            SELECT
            id    STRING
            FROM components;",
                self.idx_view
            );
        } else {
            sql = format!(
                "CREATE TEMP VIEW IF NOT EXISTS {} (id) AS
            SELECT
            id    STRING
            FROM components
            WHERE components.id IN ({});",
                self.idx_view,
                filter.unwrap()
            );
        }
        match conn.execute(
            sql.as_str(),
            (), // empty list of parameters.
        ) {
            Ok(_) => {
                info!(target:"sqlite_events", "Created Table components");
            }
            Err(err) => {
                let view_id: String = self.idx_view.clone();
                warn!(target:"sqlite_events", "While creating view {view_id:?} components: {err:?}")
            }
        }
    }

    fn create_tables(&self) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        match conn.execute(
            "CREATE TABLE IF NOT EXISTS components (
                id    STRING PRIMARY KEY,
                name  TEXT NOT NULL,
                description  TEXT,
                composition_type TEXT
            )",
            (), // empty list of parameters.
        ) {
            Ok(_) => {
                info!(target:"sqlite_events", "Created Table components");
            }
            Err(err) => {
                warn!(target:"sqlite_events", "While creating table components: {err:?}")
            }
        }

        match conn.execute(
            "CREATE TABLE IF NOT EXISTS compositions (
                composition_id    STRING,
                component_id    STRING,
                component_type  TEXT NOT NULL,
                PRIMARY KEY (composition_id, component_id, component_type),
                FOREIGN KEY(composition_id) REFERENCES components(id),
                FOREIGN KEY(component_id) REFERENCES components(id)
            )",
            (), // empty list of parameters.
        ) {
            Ok(_) => {
                info!(target:"sqlite_events", "Created Table compositions");
            }
            Err(err) => {
                warn!(target:"sqlite_events", "While creating table compositions: {err:?}")
            }
        }

        match conn.execute(
            "CREATE TABLE IF NOT EXISTS tags (
                component_id    STRING NOT NULL REFERENCES components(id),
                tag  TEXT NOT NULL,
                UNIQUE (component_id, tag)
            )",
            (), // empty list of parameters.
        ) {
            Ok(_) => {
                info!(target:"sqlite_events", "Created Table tags");
            }
            Err(err) => {
                warn!(target:"sqlite_events", "While creating table tags: {err:?}")
            }
        }
        match conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_comp_tags ON tags (component_id, tag)",
            (), // empty list of parameters.
        ) {
            Ok(_) => {
                info!(target:"sqlite_events", "Created Index for faster searches in tags");
            }
            Err(err) => {
                warn!(target:"sqlite_events", "While creating index for table tags: {err:?}")
            }
        }
        match conn.execute(
            "CREATE TABLE IF NOT EXISTS measurements (
                id STRING PRIMARY KEY,
                component_id STRING REFERENCES components(id),
                name  STRING NOT NULL,
                value REAL NOT NULL,
                unit  STRING,
                tol_min REAL,
                tol_max REAL,
                source_type STRING,
                source_remark TEXT,
                condition_of STRING REFERENCES measurements(id)
            )",
            (), // empty list of parameters.
        ) {
            Ok(_) => {
                info!(target:"sqlite_events", "Created Table measurement");
            }
            Err(err) => {
                warn!(target:"sqlite_events", "While creating table measurement: {err:?}")
            }
        }
        info!(target:"sqlite_events", "Created Database Tables");
        Ok(())
    }

    pub fn does_similar_exits(&self, component: &Component) -> bool {
        let composition_type = match &component.composition_type {
            Some(ctype) => ctype.to_string(),
            None => String::from("NULL"),
        };
        let conn = self.conn.lock().unwrap();
        match conn.query_row("SELECT components.id FROM components WHERE name = ?1 AND description = ?2 AND composition_type = ?3", params![&component.name, &component.description, composition_type], |row| row.get::<_, String>(0)){
            Ok(_) => return true,
            Err(_) => return false
        }
    }
}

impl DataReader for SQLiteData {
    fn components(&self) -> Vec<Component> {
        let conn = self.conn.lock().unwrap();
        let mut stmt_component = conn.prepare(format!("SELECT components.id, name, description, composition_type FROM components INNER JOIN {} on {}.id = components.id", self.idx_view, self.idx_view).as_str()).unwrap();
        let mut stmt_tags = conn
            .prepare("SELECT tag FROM tags WHERE component_id = :id")
            .unwrap();
        let mut stmt_properties = conn.prepare("SELECT id, name, value, unit, tol_min, tol_max, source_type, source_remark FROM measurements WHERE component_id = :id").unwrap();
        let mut stmt_composition = conn
            .prepare(
                "SELECT component_type, component_id FROM compositions WHERE composition_id = :id",
            )
            .unwrap();
        let comp_iter = match stmt_component.query_map([], |row| {
            let id: String = row.get(0)?;
            let mut component = Component {
                id: id.clone(),
                name: row.get(1)?,
                description: row.get(2)?,
                composition_type: CompositionType::from(
                    row.get::<usize, String>(3).unwrap().as_str(),
                ),
                tags: HashSet::new(),
                properties: HashMap::new(),
                composition: Option::None,
            };
            let tags_iter = stmt_tags.query_map(&[(":id", &id)], |row| row.get(0))?;
            for tag in tags_iter {
                component.tags.insert(tag?);
            }

            let properties_iter = stmt_properties.query_map(&[(":id", &id)], |row| {
                let source_type: String = row.get(6)?;
                let source_remark: String = row.get(7)?;

                let source: Option<Source>;
                if source_type == "NULL" {
                    source = Option::None
                } else {
                    source = Some(Source {
                        source_type: SourceType::from(&source_type.as_str()).unwrap(),
                        remark: source_remark,
                    })
                }
                Ok(Measurement {
                    id: row.get(0)?,
                    name: row.get(1)?,
                    value: row.get(2)?,
                    unit: Unit::from(&row.get(3)?).unwrap(),
                    tolerance: Tolerance {
                        min: row.get(4)?,
                        max: row.get(5)?,
                    },
                    source: source,
                    conditions: Option::None,
                })
            })?;
            for property in properties_iter {
                let property = property.unwrap();
                component.properties.insert(property.name.clone(), property);
            }

            let composition_iter = stmt_composition.query_map(&[(":id", &id)], |row| {
                let ctype: String = row.get(0)?;
                let cid: String = row.get(1)?;
                Ok((ctype, cid))
            })?;

            let mut composition: HashMap<String, String> = HashMap::new();
            for sub_component in composition_iter {
                let (ctype, cid) = sub_component.unwrap();
                composition.insert(ctype, cid);
            }
            if composition.len() != 0 {
                component.composition = Some(composition);
            }
            Ok(component)
        }) {
            Ok(iter) => {
                info!(target:"sqlite_events", "Iterating over components");
                iter
            }
            Err(err) => {
                warn!(target:"sqlite_events", "While iterating over components: {err:?}");
                return Vec::new();
            }
        };
        let mut result = Vec::new();
        for com in comp_iter {
            result.push(com.unwrap());
        }
        result
    }
}

impl DataWriter for SQLiteData {
    fn clean_up(&self) {
        let con = self
            .conn
            .lock()
            .expect("Get a Lock of the mutex should work!");
        con.execute("DELETE FROM compositions where component_id NOT IN (SELECT components.id from components)", []).expect("Should not fail!");
        con.execute("DELETE FROM measurements where component_id NOT IN (SELECT components.id from components)", []).expect("Should not fail!");
        con.execute(
            "DELETE FROM tags where component_id NOT IN (SELECT components.id from components)",
            [],
        )
        .expect("Should not fail!");
        con.execute("VACUUM", []).expect("Should not fail!");
    }

    fn delete_component(&mut self, component: &Component) {
        let mut conn = self.conn.lock().unwrap();
        let tx = conn
            .transaction()
            .expect("Starting a transaction should normaly not fail");
        tx.execute(
            &"DELETE FROM compositions WHERE composition_id = ?1 OR component_id = ?1",
            (&component.id,),
        )
        .expect("Should not fail!");
        tx.execute(
            &"DELETE FROM tags WHERE component_id = ?1",
            (&component.id,),
        )
        .expect("Should not fail!");
        tx.execute(
            &"DELETE FROM measurements WHERE component_id = ?1 OR component_id = ?1",
            (&component.id,),
        )
        .expect("Should not fail!");
        tx.execute(&"DELETE FROM components WHERE id = ?1", (&component.id,))
            .expect("Should not fail!");
        tx.commit().expect("Should not fail!");
    }

    fn write_component(
        &mut self,
        component: &Component,
        modus: &WriteModus,
    ) -> Result<(), impl std::error::Error> {
        let stmt_component = match modus {
            WriteModus::Insert => "INSERT INTO components (id, name, description, composition_type) VALUES (?1, ?2, ?3, ?4)",
            WriteModus::Update => "UPDATE components SET name = ?2, description = ?3, composition_type = ?4 WHERE id = ?1"
        };

        let mut conn = self.conn.lock().unwrap();
        let tx = match conn.transaction() {
            Ok(tx) => tx,
            Err(err) => {
                warn!(target:"sqlite_events", "While starting transaction to insert component: {err:?}");
                return Err(err);
            }
        };

        let composition_type = match &component.composition_type {
            Some(ctype) => ctype.to_string(),
            None => String::from("NULL"),
        };
        let component_id = &component.id;
        match tx.execute(
            &stmt_component,
            rusqlite::params![
                &component.id,
                &component.name,
                &component.description,
                composition_type
            ],
        ) {
            Ok(_) => {
                info!(target:"sqlite_events", "Successfully inserted component with id: {component_id:?}");
            }
            Err(err) => {
                warn!(target:"sqlite_events", "While inserting component with id: {component_id:?}: {err:?}");
                return Err(err);
            }
        }

        {
            if matches!(modus, WriteModus::Update) {
                tx.execute(
                    "DELETE FROM tags WHERE component_id = ?1",
                    params![&component_id],
                )
                .expect("Deleting should not cause an error!");
            }
            let mut stmt = tx
                .prepare("INSERT INTO tags (component_id, tag) VALUES (?1, ?2)")
                .expect("Should not fail if setup correct!");
            for tag in &component.tags {
                match stmt.execute((&component.id, tag.to_string())) {
                    Ok(_) => {
                        info!(target:"sqlite_events", "Successfully inserted tag: {tag:?} for component with id: {component_id:?}");
                    }
                    Err(err) => {
                        warn!(target:"sqlite_events", "Error while inserting tag: {tag:?} from component with id: {component_id:?}, got: {err:?}");
                        return Err(err);
                    }
                }
            }
        }

        {
            if matches!(modus, WriteModus::Update) {
                tx.execute(
                    "DELETE FROM measurements WHERE component_id = ?1",
                    params![&component_id],
                )
                .expect("Deleting should not cause an error!");
            }
            let mut stmt = tx.prepare("INSERT INTO measurements (id, component_id, name, value, unit, tol_min, tol_max, source_type, source_remark, condition_of) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)").expect("Should not fail if setup correct!");
            for (property_name, measurement) in &component.properties {
                let conditionof = String::from("NULL");
                let source_type: String;
                let source_remark: String;
                if measurement.source.is_none() {
                    source_type = String::from("NULL");
                    source_remark = String::from("NULL");
                } else {
                    let source = measurement.source.as_ref().unwrap();
                    source_type = source.source_type.to_string();
                    source_remark = source.remark.clone();
                }
                match stmt.execute(rusqlite::params![
                    &measurement.id,
                    &component_id,
                    &measurement.name,
                    &measurement.value,
                    &measurement.unit.unit,
                    &measurement.tolerance.min,
                    &measurement.tolerance.max,
                    &source_type,
                    &source_remark,
                    conditionof
                ]) {
                    Ok(_) => {
                        info!(target:"sqlite_events", "Successfully inserted property: {property_name:?} for component with id: {component_id:?}");
                    }
                    Err(err) => {
                        warn!(target:"sqlite_events", "Error while inserting property: {property_name:?} from component with id: {component_id:?}, got: {err:?}");
                        return Err(err);
                    }
                }
            }
        }
        {
            if matches!(modus, WriteModus::Update) {
                tx.execute(
                    "DELETE FROM compositions WHERE composition_id = ?1",
                    params![&component_id],
                )
                .expect("Deleting should not cause an error!");
            }
            if component.composition.is_some() {
                let mut stmt = tx.prepare("INSERT INTO compositions (composition_id, component_id, component_type) VALUES (?,?,?)").unwrap();
                let Some(composition) = &component.composition else {
                    panic!("Should not reach here!")
                };
                for (component_type, id) in composition {
                    stmt.execute((component_id.to_string(), id.to_string(), component_type))
                        .unwrap();
                }
            }
        }

        match tx.commit() {
            Ok(_) => {
                info!(target:"sqlite_events", "Transaction successfully ended!");
            }
            Err(err) => {
                warn!(target:"sqlite_events", "While finishing transaction: {err:?}");
                return Err(err);
            }
        }

        Ok(())
    }
}

impl DataSet for SQLiteData {
    type Output = SQLiteData;
    fn reduce(&self, filter: &str) -> Self::Output {
        let mut hasher = Sha256::new();
        hasher.update(filter);
        let filter_hash = hasher.finalize();
        let idx_view =
            String::from(self.idx_view.as_str()) + "_" + hex::encode(filter_hash).as_str();
        let sqlite = SQLiteData {
            conn: Arc::clone(&self.conn),
            idx_view: idx_view,
        };
        sqlite.create_view(Some(filter.to_string()));
        return sqlite;
    }

    fn find(&self, filter: &str) -> Result<std::vec::Vec<Component>, impl std::error::Error> {
        let conn = self.conn.lock().unwrap();
        let select_component_stmt = format!("SELECT components.id, name, description, composition_type FROM components INNER JOIN {} ON {}.id = components.id WHERE components.id IN ({})", self.idx_view, self.idx_view, filter);
        let mut stmt_component = match conn.prepare(select_component_stmt.as_str()) {
            Ok(stmt) => stmt,
            Err(err) => {
                warn!(target: "sqlite_events", "Error while preparing statement: '{select_component_stmt}', got {err}");
                return Err(err);
            }
        };
        let mut stmt_tags = conn
            .prepare("SELECT tag FROM tags WHERE component_id = :id")
            .unwrap();
        let mut stmt_properties = conn.prepare("SELECT id, name, value, unit, tol_min, tol_max, source_type, source_remark FROM measurements WHERE component_id = :id").unwrap();
        let mut stmt_composition = conn
            .prepare(
                "SELECT component_type, component_id FROM compositions WHERE composition_id = :id",
            )
            .unwrap();
        let comp_iter = match stmt_component.query_map([], |row| {
            let id: String = row.get(0)?;
            let mut component = Component {
                id: id.clone(),
                name: row.get(1)?,
                description: row.get(2)?,
                composition_type: CompositionType::from(row.get::<usize,String>(3).unwrap().as_str()),
                tags: HashSet::new(),
                properties: HashMap::new(),
                composition: Option::None
            };
            let tags_iter = stmt_tags.query_map(&[(":id", &id)], |row| row.get(0))?;
            for tag in tags_iter {
                component.tags.insert(tag?);
            }

            let properties_iter = stmt_properties.query_map(&[(":id", &id)], |row| {
                let source_type: String = row.get(6)?;
                let source_remark: String = row.get(7)?;

                let source: Option<Source>;
                if source_type == "NULL" {
                    source = Option::None
                } else {
                    source = Some(Source{
                        source_type: SourceType::from(&source_type.as_str()).unwrap(),
                        remark: source_remark
                    })
                }
                let measure_id: String = row.get(0)?;
                let unit_str: String = match row.get(3) {
                    Ok(txt) => txt,
                    Err(err) => {
                        warn!(target: "sqlite_events", "While parsing unit from measurement with id '{measure_id}', got {err}");
                        return Err(err);
                    }
                };

                Ok(
                    Measurement{
                        id: measure_id,
                        name: row.get(1)?,
                        value: row.get(2)?,
                        unit: Unit::from(&unit_str).unwrap(),
                        tolerance: Tolerance{min: row.get(4)?, max: row.get(5)?},
                        source: source,
                        conditions: Option::None
                    }
                )
            })?;
            for property in properties_iter {
                let property = property.unwrap();
                component.add_measurement(property);
            }

            let composition_iter = stmt_composition.query_map(&[(":id", &id)], |row| {
                let ctype:String = row.get(0)?;
                let cid: String = row.get(1)?;
                Ok((ctype, cid))
            })?;

            let mut composition: HashMap<String, String> = HashMap::new();
            for sub_component in composition_iter {
                let (ctype, cid) = sub_component.unwrap();
                composition.insert(ctype, cid);
            }
            if composition.len() != 0{
                component.composition = Some(composition);
            }
            Ok(component)
        }){
            Ok(iter) => {
                info!(target:"sqlite_events", "Iterating over components");
                iter
            }
            Err(err) => {
                warn!(target:"sqlite_events", "While iterating over components: {err:?}");
                return Err(err)
            }
        };
        let mut result = Vec::new();
        for com in comp_iter {
            result.push(com.unwrap());
        }
        Ok(result)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn insert_component() -> Result<(), std::fmt::Error> {
        let _ = env_logger::try_init();

        let connection = match Connection::open_in_memory() {
            Ok(conn) => conn,
            Err(_err) => panic!("should not reach here!"),
        };
        let mut dataset = SQLiteData::from_connection(connection).unwrap();
        // match dataset.create_tables(){
        //     Ok(()) => (),
        //     Err(_err) => panic!("Unexpected error while creating the tables!")
        // }
        let component = Component::new();
        assert_eq!(
            dataset
                .write_component(&component, &WriteModus::Insert)
                .is_ok(),
            true
        );
        return Ok(()); // ::<(),std::fmt::Error>(())
    }

    #[test]
    fn get_all_component() -> Result<(), std::fmt::Error> {
        let _ = env_logger::try_init();

        let connection = match Connection::open_in_memory() {
            Ok(conn) => conn,
            Err(_err) => panic!("should not reach here!"),
        };
        let mut dataset = SQLiteData::from_connection(connection).unwrap();

        let should_be_empty = dataset.components();
        assert_eq!(should_be_empty.len(), 0);

        let mut list_of_components = Vec::new();
        for _ in 0..10 {
            list_of_components.push(Component::new());
        }

        for component in &list_of_components {
            match dataset.write_component(component, &WriteModus::Insert) {
                Ok(_) => (),
                Err(_err) => panic!("should not reach here!"),
            }
        }
        let components_found = dataset.components();
        assert_eq!(components_found.len(), list_of_components.len());
        for (c_expected, c_recieved) in list_of_components.iter().zip(components_found.iter()) {
            assert_eq!(c_expected.id, c_recieved.id);
        }
        return Ok(()); // ::<(),std::fmt::Error>(())
    }

    #[test]
    fn reduce() -> Result<(), std::fmt::Error> {
        let _ = env_logger::try_init();

        let store_db = false;
        let mut dataset: SQLiteData;
        if store_db {
            dataset = SQLiteData::new("./test_reduce.db").unwrap();
        } else {
            let connection = match Connection::open_in_memory() {
                Ok(conn) => conn,
                Err(_err) => panic!("should not reach here!"),
            };
            dataset = SQLiteData::from_connection(connection).unwrap();
        }

        let mut components_empty = Vec::new();
        let mut components_incomplet = Vec::new();
        let mut components_completed = Vec::new();
        for i in 0..10 {
            let mut comp = Component::new();
            comp.name = format!("empty_{}", i);
            components_empty.push(comp);
        }
        for i in 0..10 {
            let mut comp_incomplete = Component::new();
            comp_incomplete.name = format!("incomplete_{}", i * 2);
            let mut measurement = Measurement::new();
            measurement.name += "one";
            comp_incomplete.add_measurement(measurement);
            components_incomplet.push(comp_incomplete);

            let mut comp_incomplete = Component::new();
            comp_incomplete.name = format!("incomplete_{}", i * 2 + 1);
            let mut measurement = Measurement::new();
            measurement.name += "two";
            comp_incomplete.add_measurement(measurement);
            components_incomplet.push(comp_incomplete);
        }

        for i in 0..10 {
            let mut comp_complete = Component::new();
            comp_complete.name = format!("complete_{}", i);
            let mut measurement = Measurement::new();
            measurement.name += "one";
            comp_complete.add_measurement(measurement);
            let mut measurement = Measurement::new();
            measurement.name += "two";
            comp_complete.add_measurement(measurement);
            components_completed.push(comp_complete);
        }

        for component in &components_empty {
            match dataset.write_component(component, &WriteModus::Insert) {
                Ok(_) => (),
                Err(_err) => panic!("should not reach here!"),
            }
        }
        for component in &components_incomplet {
            match dataset.write_component(component, &WriteModus::Insert) {
                Ok(_) => (),
                Err(_err) => panic!("should not reach here!"),
            }
        }
        for component in &components_completed {
            match dataset.write_component(component, &WriteModus::Insert) {
                Ok(_) => (),
                Err(_err) => panic!("should not reach here!"),
            }
        }

        let reduced_dataset = dataset.reduce("SELECT component_id FROM measurements WHERE name = 'one' INTERSECT SELECT component_id FROM measurements WHERE name = 'two'");

        let components_found = reduced_dataset.components();
        assert_eq!(components_found.len(), components_completed.len());
        for (c_expected, c_recieved) in components_completed.iter().zip(components_found.iter()) {
            assert_eq!(c_expected.id, c_recieved.id);
        }

        Ok(())
    }

    #[test]
    fn filter_tags() -> Result<(), std::fmt::Error> {
        let _ = env_logger::try_init();

        let store_db = false;
        let mut dataset: SQLiteData;
        if store_db {
            dataset = SQLiteData::new("./test_filter_tags.db").unwrap();
        } else {
            let connection = match Connection::open_in_memory() {
                Ok(conn) => conn,
                Err(_err) => panic!("should not reach here!"),
            };
            dataset = SQLiteData::from_connection(connection).unwrap();
        }

        let mut components_taged_none = Vec::new();
        let mut components_taged_one = Vec::new();
        let mut components_taged_two = Vec::new();
        for _ in 0..10 {
            components_taged_none.push(Component::new());

            let mut comp_taged_one = Component::new();
            comp_taged_one.tags.insert(String::from("one"));
            components_taged_one.push(comp_taged_one);

            let mut comp_taged_two = Component::new();
            comp_taged_two.tags.insert(String::from("one"));
            comp_taged_two.tags.insert(String::from("two"));
            components_taged_two.push(comp_taged_two);
        }

        for i in 0_usize..10 {
            match dataset.write_component(&components_taged_none[i], &WriteModus::Insert) {
                Ok(_) => (),
                Err(_err) => panic!("should not reach here!"),
            }
            match dataset.write_component(&components_taged_one[i], &WriteModus::Insert) {
                Ok(_) => (),
                Err(_err) => panic!("should not reach here!"),
            }
            match dataset.write_component(&components_taged_two[i], &WriteModus::Insert) {
                Ok(_) => (),
                Err(_err) => panic!("should not reach here!"),
            }
        }

        let should_be_equal_taged_two =
            dataset.find("SELECT component_id FROM tags WHERE tag = 'two'");
        assert_eq!(should_be_equal_taged_two.is_ok(), true);
        let components_found = should_be_equal_taged_two.unwrap();
        assert_eq!(components_found.len(), components_taged_two.len());
        for (c_expected, c_recieved) in components_taged_two.iter().zip(components_found.iter()) {
            assert_eq!(c_expected.id, c_recieved.id);
        }

        Ok(())
    }
}
