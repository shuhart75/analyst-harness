"""Source-side transport requests; receiver resolution belongs to its harness."""
from __future__ import annotations

import uuid

REQUEST_FILE = 'analysis-task-request.json'
TOKEN = 'receiver-task/'


def validate_request(value, delivery=None):
    if (not isinstance(value, dict) or value.get('schema_version') != 1
            or value.get('target') != 'receiver' or value.get('role') != 'AN'
            or value.get('provider') != 'sbertrek'):
        raise ValueError('Invalid receiver task request')
    if str(uuid.UUID(value.get('request_id', ''))) != value['request_id']:
        raise ValueError('Invalid task request identity')
    for field in ('delivery', 'summary', 'confirmation'):
        if not isinstance(value.get(field), str) or not value[field].strip():
            raise ValueError('Missing task request field: ' + field)
    if delivery is not None and value['delivery'] != delivery:
        raise ValueError('Task request belongs to another delivery')
    if 'key' in value:
        raise ValueError('A request is not a tracker binding')
    return value


def request_token(value):
    return TOKEN + validate_request(value)['request_id']
