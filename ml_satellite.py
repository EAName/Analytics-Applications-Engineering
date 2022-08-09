from google.cloud import bigquery
client = bigquery.Client()

  

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