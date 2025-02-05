use quintus::server::build;

#[rocket::main]
async fn main() -> Result<(), rocket::Error> {
    let _rocket = build().launch().await?;

    Ok(())
}
