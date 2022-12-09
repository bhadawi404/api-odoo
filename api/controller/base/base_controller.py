from dataacess.da.base_da import BaseDA
from response.product.product_response import ProductResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, permissions
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from shared.helper.dict2obj import Dict2Obj as dt_obj # pylint: disable=import-error
from datetime import datetime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import json
import os



class base_controller(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

def controller_translator(controllerName):
    result = ""

    if controllerName not in [None, ""]:
        if str(controllerName).lower() == 'product':
            result = 'product.product'
        

    return result

@api_view(['GET'])
def page(request, controllerName):
    
    modelDA = BaseDA()
    modelResponse = ProductResponse()
    BaseDA.TABLE_NAME = controller_translator(controllerName)
    data = []
    total_data = 0
    error_message = []

    try:
        response = modelDA.getall(controllerName)
        dataResponse = modelResponse.detail(response)
        
        if not dataResponse :
            error_message = 'data tidak ada'
            content = {
                "error_message": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
                "data": json.loads(json.dumps(data, default=lambda o: o.__dict__)),
                "status": False,
                "total_data": 0
            }
            return Response(status=status.HTTP_200_OK, data=content)
        data = dataResponse
        # data = response
        error_message = []
    except Exception as ex:
        error_message.append(str(ex))

    content = {
        "error_message": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
        "data": json.loads(json.dumps(data, default=lambda o: o.__dict__)),
        "status": (True if len(error_message) == 0 else False)
    }

    response_status = (status.HTTP_200_OK if content["status"] is True else status.HTTP_400_BAD_REQUEST)

    return Response(status=response_status, data=content)