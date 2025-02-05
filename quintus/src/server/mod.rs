use std::path::Path;

use rocket::{self, fs::{FileServer, NamedFile}, get, routes, Build, Rocket};

#[get("/")]
async fn index() -> Option<NamedFile> { 
    NamedFile::open(Path::new("public/index.html")).await.ok() 
}

pub fn build() -> Rocket<Build>{
    rocket::build()
    .mount("/", routes![index])
    .mount("/public", FileServer::from("resources/web"))
    .mount("/api", routes![index])
}