from google.cloud import bigquery
client = bigquery.Client()

  

def query_data():
    query = """
SELECT * FROM `flight-data-1._bfc2a53340092fabda17f8b6571dc270ec3bc88b.anon4f314c22_b523_4313_bd73_47c5cf38b9f8_imported_data_split_eval_data` LIMIT 1000
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