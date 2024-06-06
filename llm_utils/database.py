import pyodbc

def get_db_connection(db_server, db_name, db_user, db_password):
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + db_server
        + ";DATABASE="
        + db_name
        + ";UID="
        + db_user
        + ";PWD="
        + db_password
    )
    return pyodbc.connect(conn_str)


def write_to_db(
    app_config, input_as_json, submit_time, response_time, cost, name_suffix=""
):
    with get_db_connection(
        db_server=app_config.DB_SERVER,
        db_name=app_config.DB_NAME,
        db_user=app_config.DB_USER,
        db_password=app_config.DB_PASSWORD,
    ) as conn:
        cursor = conn.cursor()
        query = """
        INSERT INTO api_interactions (app_name, user_input, submit_time, response_time, total_cost)
        VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(
            query,
            (
                app_config.NAME + name_suffix,
                input_as_json,
                submit_time,
                response_time,
                cost,
            ),
        )
        conn.commit()
