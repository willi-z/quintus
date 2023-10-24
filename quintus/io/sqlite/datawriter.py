from quintus.io.datawriter import DataWriter
from quintus.structures import Component
import sqlite3
from pathlib import Path
from quintus.helpers.id_generation import generate_id
import json


class SqliteDataWriter(DataWriter):
    def __init__(
        self,
        db: Path,
        override=True,
    ) -> None:
        self.db = db
        if override:
            if self.db.exists():
                self.db.unlink()
        if not self.db.exists():
            self.db.touch()

        self.__create_tables__()

    def __create_tables__(self) -> None:
        with sqlite3.connect(self.db) as con:
            cur = con.cursor()

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS components (
                    id  TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT
                );
            """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tags (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE
                );
            """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS component_tags (
                    component_id TEXT,
                    tag_id TEXT,
                    PRIMARY KEY (component_id, tag_id),
                    FOREIGN KEY (component_id) REFERENCES components(id),
                    FOREIGN KEY (tag_id) REFERENCES tags(id)
                );
            """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS component_compostions (
                    component_trunk_id TEXT,
                    component_branch_id TEXT,
                    name TEXT,
                    PRIMARY KEY (component_trunk_id, component_branch_id),
                    FOREIGN KEY (component_trunk_id) REFERENCES components(id),
                    FOREIGN KEY (component_branch_id) REFERENCES components(id)
                );
            """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS measurements (
                    component_id TEXT,
                    name TEXT,
                    value REAL,
                    unit TEXT,
                    tol JSON,
                    at JSON,
                    source TEXT,
                    PRIMARY KEY (component_id, name),
                    FOREIGN KEY (component_id) REFERENCES components(id)
                );
            """
            )
            con.commit()

    def __insert_tags__(self, con: sqlite3.Connection, tags: list[str]):
        cur = con.cursor()
        content = []
        for tag in tags:
            content.append((generate_id(), tag))
        cur.executemany("INSERT OR IGNORE INTO tags VALUES (?,?)", content)
        con.commit()
        cur.close()

    def __insert_component__(
        self,
        con: sqlite3.Connection,
        comp: Component,
        trunk_id: str = None,
        name: str = None,
    ):
        cur = con.cursor()
        try:
            cur.execute(
                "INSERT INTO components VALUES (?, ?, ?)",
                (comp._id, comp.name, comp.description),
            )
            con.commit()
        except sqlite3.OperationalError:
            print(comp._id, comp.name, comp.description)
            raise ValueError

        # tags
        if comp.tags is not None:
            self.__insert_tags__(con, comp.tags)
            comp_tags = []
            for tag in comp.tags:
                cur.execute(
                    """
                SELECT id FROM tags WHERE name=?
                """,
                    (tag,),
                )
                tag_id = cur.fetchone()[0]
                comp_tags.append((comp._id, tag_id))
            cur.executemany(
                """
                INSERT INTO component_tags VALUES (?,?)
                """,
                comp_tags,
            )

        # measurments
        if comp.properties is not None:
            measurements = []
            for name, measurement in comp.properties.items():
                measurements.append(
                    (
                        comp._id,
                        name,
                        measurement.value,
                        measurement.unit,
                        json.dumps(measurement.tol),
                        json.dumps(measurement.at),
                        measurement.source,
                    )
                )
            cur.executemany(
                """
                INSERT INTO measurements (
                    component_id,
                    name,
                    value,
                    unit,
                    tol, at, source
                ) VALUES(?,?,?,?,?,?,?,?)
                """,
                measurements,
            )

        if trunk_id is not None:
            cur.execute(
                """
                INSERT INTO component_compostions (
                    component_trunk_id, component_branch_id, name
                ) VALUES(?, ?, ?)
                """,
                (trunk_id, comp._id, name),
            )

        con.commit()
        cur.close()

        if comp.compostion is not None:
            for key, val in comp.compostion.items():
                self.__insert_component__(con, val, comp._id, key)

    def __delete_component__(self, con: sqlite3.Connection, comp: Component):
        if comp.compostion is not None:
            for key, val in comp.compostion.items():
                self.__delete_component__(con, val)

        cur = con.cursor()

        cur.execute(
            """
            DELETE FROM component_compostions
            WHERE component_branch_id = ?
            """,
            (comp._id,),
        )

        cur.execute(
            """
            DELETE FROM measurements
            WHERE component_id = ?
            """,
            (comp._id,),
        )

        cur.execute(
            """
            DELETE FROM component_tags
            WHERE component_id = ?
            """,
            (comp._id,),
        )

        cur.execute(
            """
            DELETE FROM components
            WHERE id = ?
            """,
            (comp._id,),
        )

        con.commit()

    def __delete_unused_tags__(self, con: sqlite3.Connection):
        cur = con.cursor()

        cur.execute(
            """
            DELETE FROM tags
            WHERE id NOT IN
            (
                SELECT id FROM component_tags
            )
            """
        )

        con.commit()

    def write_entry(self, entry: Component, override=True):
        with sqlite3.connect(self.db) as con:
            self.__insert_component__(con, entry)
