use std::{collections::HashMap, path::Path, sync::Arc};

use rocket::{
    self,
    fs::{FileServer, NamedFile},
    get, routes, Build, Rocket, State,
};
use serde::Serialize;

use crate::{io::{sqlite::SQLiteData, traits::DataReader}, structures::{Component, ComponentType, ID}};

type DBHandel = Arc<SQLiteData>;

#[get("/")]
async fn index() -> Option<NamedFile> {
    NamedFile::open(Path::new("quintus/resources/web/index.html")).await.ok()
}

#[derive(Serialize)]
struct RefUsedInComposition {
    id: String,
    name: String,
    ctype: String,
}


#[derive(Serialize)]
struct ComponentOverview{
    #[serde(flatten)]
    component: Component,
    used_in: Vec<RefUsedInComposition>
}

#[get("/overview")]
async fn overview() -> Option<NamedFile> {
    NamedFile::open(Path::new("quintus/resources/web/overview.html")).await.ok()
}



#[get("/components")]
fn get_components(sql: & State<DBHandel>) -> String {
    let components = sql.components();
    let conn = sql.conn.lock().unwrap();
    let mut stmt = conn.prepare("SELECT components.id, components.name, compositions.component_type FROM components INNER JOIN compositions ON compositions.composition_id = components.id WHERE compositions.component_id = ?;").expect("Should not fail!");

    let mut result: Vec<ComponentOverview> = Vec::with_capacity(components.len());
    for component in  components{

        let used_in = stmt.query_map([&component.id], |row| {
            Ok(RefUsedInComposition{
                id: row.get(0).unwrap(),
                name: row.get(1).unwrap(),
                ctype: row.get(2).unwrap(),
            })
        }).unwrap().map(|res| res.unwrap()).collect();
        
        result.push(ComponentOverview{
            component: component,
            used_in: used_in,
        });
    }
    
    return serde_json::to_string(&result).unwrap();
}


pub fn build() -> Rocket<Build> {
    rocket::build()
        .manage(Arc::new(SQLiteData::new("./test.db").unwrap()))
        .mount("/", routes![index, overview])
        .mount("/assets", FileServer::from("quintus/resources/web"))
        .mount("/api", routes![get_components])
}
