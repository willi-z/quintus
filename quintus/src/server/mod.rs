use std::{path::Path, sync::Arc};

use rocket::{
    self,
    fs::{FileServer, NamedFile},
    get, routes, Build, Rocket, State,
};

use crate::io::{sqlite::SQLiteData, traits::DataReader};

type DBHandel = Arc<SQLiteData>;

#[get("/")]
async fn index() -> Option<NamedFile> {
    NamedFile::open(Path::new("quintus/resources/web/index.html")).await.ok()
}

#[get("/overview")]
async fn overview() -> Option<NamedFile> {
    NamedFile::open(Path::new("quintus/resources/web/overview.html")).await.ok()
}



#[get("/components")]
fn get_components(sql: & State<DBHandel>) -> String {
    let components = sql.components();
    return serde_json::to_string(&components).unwrap();
}


pub fn build() -> Rocket<Build> {
    rocket::build()
        .manage(Arc::new(SQLiteData::new("./test.db").unwrap()))
        .mount("/", routes![index, overview])
        .mount("/assets", FileServer::from("quintus/resources/web"))
        .mount("/api", routes![get_components])
}
