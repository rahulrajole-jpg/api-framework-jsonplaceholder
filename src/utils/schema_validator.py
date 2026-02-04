import json
from jsonschema import validate, ValidationError

def validate_schema(data, schema_path):
    with open(schema_path) as f:
        schema = json.load(f)
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise AssertionError(f"Schema validation error: {e.message}")
    