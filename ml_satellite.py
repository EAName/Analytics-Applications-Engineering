from google.cloud import bigquery
client = bigquery.Client()
from datetime import datetime
  

def query_data():
    query = """
SELECT * FROM `flight-data-1.dsongcp.sat_analytics` LIMIT 1000
"""
    query_job = client.query(query)

    results = query_job.result()
    results_json = []
    for row in results:
        row_json = {}
        for key in row.keys():
            row_json[key] = str(row[key])
        results_json.append(row_json)

    return results_json

def load_csv(csv):
    job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
)
    now = datetime.now()
    timestamp = round(datetime.timestamp(now))
    file_name = f'sat_upload_{timestamp}'
    table_id = f"flight-data-1.dsongcp.{file_name}"

    job = client.load_table_from_file(csv,table_id,job_config=job_config)
    job.result()
    query = f"SELECT * FROM `{table_id}` LIMIT 1000"
    query_job = client.query(query)

    results = query_job.result()
    ml_query = f"""
    SELECT * FROM ML.PREDICT(MODEL `flight-data-1.dsongcp.sample_model`,
    (
    SELECT class AS label,  
Aattr AS A,  
Battr AS B,
Cattr AS C,
Dattr AS D,
Eattr AS E,
Fattr AS F,
A1attr AS A1,
B2attr AS B2,
C3attr AS C3,
D4attr AS D4,
E5attr AS E5,
F6attr AS F6,
A7attr AS A7,
B8attr AS B8,
C9attr AS C9,
D10attr AS D10,
E11attr AS E11,
F12attr AS F12,
A13attr AS A13,
B14attr AS B14,
C15attr AS C15,
D16attr AS D16,
E17attr AS E17,
F18attr AS F18,
A19attr AS A19,
B20attr AS B20,
C21attr AS C21,
D22attr AS D22,
E23attr AS E23,
F24attr AS F24,
A25attr AS A25,
B26attr AS B26,
C27attr AS C27,
D28attr AS D28,
E29attr AS E29,
F30attr AS F30
 FROM `{table_id}`)) 
    """
    ml_query_job = client.query(ml_query)
    ml_result = ml_query_job.result()
    results_json = []
    for row in ml_result:
        row_json = {}
        for key in row.keys():
            row_json[key] = str(row[key])
        results_json.append(row_json)

    return results_json   