import logging
import json
import uuid
import os
import base64
import azure.functions as func
from azure.data.tables import TableClient

app = func.FunctionApp()

@app.route(route="createtask", auth_level=func.AuthLevel.ANONYMOUS)
def create_task(req: func.HttpRequest) -> func.HttpResponse:

    # --- Auth ---
    client_principal_encoded = req.headers.get('x-ms-client-principal')
    if not client_principal_encoded:
        return func.HttpResponse("Auth Failed", status_code=401)

    try:
        client_principal = json.loads(
            base64.b64decode(client_principal_encoded).decode('utf-8')
        )
    except Exception:
        return func.HttpResponse("Invalid auth header.", status_code=401)

    user_id = client_principal.get('userId')
    if not user_id:
        return func.HttpResponse("User ID not found in client principal.", status_code=401)

    # --- Request body ---
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON body.", status_code=400)

    task_description = req_body.get('description')
    if not task_description:
        return func.HttpResponse("Missing 'description' field.", status_code=400)

    # --- Table connection ---
    try:
        table_client = TableClient.from_connection_string(
            conn_str=os.environ["AzureWebJobsStorage"], 
            table_name="tasks"
        )
    except Exception as e:
        logging.error(f"Error connecting to storage: {e}")
        return func.HttpResponse("Storage connection failed.", status_code=500)

    # --- Task entity ---
    task_id = str(uuid.uuid4())
    entity = {
        'PartitionKey': user_id,
        'RowKey': task_id,
        'description': task_description,
        'isCompleted': False
    }

    try:
        table_client.create_entity(entity=entity)
    except Exception as e:
        logging.error(f"Error creating task entity: {e}")
        return func.HttpResponse("Failed to create task.", status_code=500)

    # --- Success ---
    return func.HttpResponse(
        json.dumps(entity),
        status_code=201,
        mimetype="application/json"
    )
