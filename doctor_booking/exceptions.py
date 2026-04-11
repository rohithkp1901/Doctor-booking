from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'success': False,
            'message': 'An error occurred.',
            'errors': response.data,
        }
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                error_data['message'] = str(response.data['detail'])
                error_data['errors'] = {}
        elif isinstance(response.data, list):
            error_data['message'] = 'Validation error.'
        response.data = error_data

    return response
