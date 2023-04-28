from dataacess.da.base_da import BaseDA
from response.base.base_response import BaseResponse
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
from user_management.renderers import UserRenderer

from user_management.serializers import UserLoginSerializer, UserSerializer



class base_controller(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    renderer_classes = [UserRenderer]

def controller_translator(controllerName):
    result = ""

    if controllerName not in [None, ""]:
        if str(controllerName).lower() == 'product-product':
            result = 'product.product'
        elif str(controllerName).lower() == 'purchase-order':
            result = 'stock.picking'
        elif str(controllerName).lower() == 'stock-take':
            result = 'product.product'
        elif str(controllerName).lower() == 'validate-purchase':
            result = 'stock.picking'
        elif str(controllerName).lower() == 'internal-transfer':
            result = 'stock.picking'
        elif str(controllerName).lower() == 'validate-internal-transfer':
            result = 'stock.picking'
        elif str(controllerName).lower() == 'internal-transfer-in':
            result = 'stock.picking'
        elif str(controllerName).lower() == 'validate-internal-transfer-in':
            result = 'stock.picking'
        elif str(controllerName).lower() == 'internal-transfer-out':
            result = 'stock.picking'
        elif str(controllerName).lower() == 'validate-internal-transfer-out':
            result = 'stock.picking'
        elif str(controllerName).lower() == 'consume':
            result = 'stock.picking'
        elif str(controllerName).lower() == 'validate-consume':
            result = 'stock.picking'
        elif str(controllerName).lower() == 'return':
            result = 'stock.picking'   
        elif str(controllerName).lower() == 'validate-return':
            result = 'stock.picking'   
        

    return result

def controller_response(controllerName):
    result = ""

    if str(controllerName).lower() == 'product-product':
        result = 'modelResponse.product'
    elif str(controllerName).lower() == 'purchase-order':
        result = 'modelResponse.purchase_order'
    elif str(controllerName).lower() == 'stock-take':
        result = 'modelResponse.stock_take'
    elif str(controllerName).lower() == 'validate-purchase':
        result = 'modelResponse.validate_purchase'
    elif str(controllerName).lower() == 'internal-transfer':
        result = 'modelResponse.internal_transfer'
    elif str(controllerName).lower() == 'validate-internal-transfer':
        result = 'modelResponse.validate_internal_transfer'
    elif str(controllerName).lower() == 'internal-transfer-in':
        result = 'modelResponse.internal_transfer_in'
    elif str(controllerName).lower() == 'validate-internal-transfer-in':
        result = 'modelResponse.validate_internal_transfer_in'
    elif str(controllerName).lower() == 'internal-transfer-out':
        result = 'modelResponse.internal_transfer_out'
    elif str(controllerName).lower() == 'validate-internal-transfer-out':
        result = 'modelResponse.validate_internal_transfer_out'
    elif str(controllerName).lower() == 'consume':
        result = 'modelResponse.consume'
    elif str(controllerName).lower() == 'validate-consume':
        result = 'modelResponse.validate_consume'
    elif str(controllerName).lower() == 'return':
        result = 'modelResponse.return_product'
    elif str(controllerName).lower() == 'validate-return':
            result = 'modelResponse.validate_return'
    

    return result

@api_view(['GET'])
def page(request, controllerName, format=None):
    serializer = UserSerializer(request.user)
    tes =[]
    modelDA = BaseDA()
    modelResponse = BaseResponse()
    controller = controller_translator(controllerName)
    responseDA = controller_response(controllerName)
    data = []
    error_message = []
    limit = request.query_params.get('limit', False)
    offset = request.query_params.get('offset', False)
    try:
        response = modelDA.getall(controller,limit,offset,serializer)
        if response == 'Access Denied':
            error_message = 'Access Denied'
            content = {
                "error_message": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_403_FORBIDDEN, data=content)    
        dataResponse = eval(responseDA)(response)
        
        if not dataResponse :
            error_message = 'DATA NOT FOUND'
            content = {
                "error_message": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
                "data": json.loads(json.dumps(data, default=lambda o: o.__dict__)),
                "status": False,
                "total_data": 0
            }
            return Response(status=status.HTTP_200_OK, data=content)
        if not dataResponse :
            error_message = 'DATA NOT FOUND'
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
        if 'AnonymousUser' in str(ex):
            error_message = 'Autorization Token'
            content = {
                "error_message": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=content)
        
    
    content = {
        "statusCode": 200,
        "statusCodeDesc": 'OK',
        "data": json.loads(json.dumps(data, default=lambda o: o.__dict__)),
        
    }

    response_status = (status.HTTP_200_OK if content["statusCode"] == 200 else status.HTTP_400_BAD_REQUEST)

    return Response(status=response_status, data=content)

@api_view(['GET'])
def detail(request, barcode, controllerName):
    serializer = UserSerializer(request.user)
    modelDA = BaseDA()
    modelResponse = BaseResponse()
    controller = controller_translator(controllerName)
    responseDA = controller_response(controllerName)
    data = []
    total_data = 0
    error_message = []

    try:
        response = modelDA.getbybarcode(controller,barcode, serializer)
        if response == 'Access Denied':
            error_message = 'Access Denied'
            content = {
                "error_message": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_403_FORBIDDEN, data=content) 
        dataResponse = eval(responseDA)(response)
        
        if not dataResponse :
            error_message = 'DATA NOT FOUND'
            content = {
                "statusCode": 404,
                "statusDesc": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_404_NOT_FOUND, data=content)
        data = dataResponse
        # data = response
        error_message = []
    except Exception as ex:
        if 'AnonymousUser' in str(ex):
            error_message = 'Autorization Token'
            content = {
                "error_message": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=content)

    content = {
        "statusCode": 200,
        "statusCodeDesc": 'OK',
        "data": json.loads(json.dumps(data, default=lambda o: o.__dict__)),
        
    }

    response_status = (status.HTTP_200_OK if content["statusCode"] == 200 else status.HTTP_400_BAD_REQUEST)

    return Response(status=response_status, data=content)

@api_view(['GET'])
def detail_id(request, id, controllerName):
    serializer = UserSerializer(request.user)
    print("masuk sini")
    modelDA = BaseDA()
    modelResponse = BaseResponse()
    controller = controller_translator(controllerName)
    responseDA = controller_response(controllerName)
    data = []
    total_data = 0
    error_message = []
    
    try:
        response = modelDA.getbyid(controller,id,serializer)
        if response == 'Access Denied':
            error_message = 'Access Denied'
            content = {
                "error_message": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_403_FORBIDDEN, data=content) 
        dataResponse = eval(responseDA)(response)
        
        if not dataResponse :
            error_message = 'DATA NOT FOUND'
            content = {
                "statusCode": 404,
                "statusDesc": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_404_NOT_FOUND, data=content)
        data = dataResponse
        # data = response
        error_message = []
    except Exception as ex:
        if 'AnonymousUser' in str(ex):
            error_message = 'Autorization Token'
            content = {
                "error_message": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=content)

    content = {
        "statusCode": 200,
        "statusCodeDesc": 'OK',
        "data": json.loads(json.dumps(data, default=lambda o: o.__dict__)),
        
    }

    response_status = (status.HTTP_200_OK if content["statusCode"] == 200 else status.HTTP_400_BAD_REQUEST)

    return Response(status=response_status, data=content)

@api_view(['POST'])
def scan(request, controllerName):
    serializer = UserSerializer(request.user)
    print("bisa")
    barcode = request.data['barcode']
    modelDA = BaseDA()
    modelResponse = BaseResponse()
    controller = controller_translator(controllerName)
    responseDA = controller_response(controllerName)
    data = []
    total_data = 0
    error_message = []

    try:
        
        response = modelDA.getbyidscan(controller,barcode,serializer)
        dataResponse = eval(responseDA)(response,serializer)
        print(dataResponse,"==erere==")
        
        if not dataResponse :
            error_message = 'DATA NOT FOUND'
            content = {
                "statusCode": 404,
                "statusDesc": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_404_NOT_FOUND, data=content)
        data = dataResponse
        # data = response
        error_message = []
    except Exception as ex:
        if 'AnonymousUser' in str(ex):
            error_message = 'Autorization Token'
            content = {
                "error_message": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=content)

    content = {
        "statusCode": 200,
        "statusCodeDesc": 'OK',
        "data": json.loads(json.dumps(data, default=lambda o: o.__dict__)),
        
    }

    response_status = (status.HTTP_200_OK if content["statusCode"] == 200 else status.HTTP_400_BAD_REQUEST)

    return Response(status=response_status, data=content)


@api_view(['PUT'])
def update(request, id, controllerName):
    serializer = UserSerializer(request.user)
    modelDA = BaseDA()
    modelResponse = BaseResponse()
    controller = controller_translator(controllerName)
    responseDA = controller_response(controllerName)
    data = []
    total_data = 0
    error_message = []
    try:
        response = modelDA.update(controller,id)
        dataResponse = eval(responseDA)(response, request, serializer)
        
        if not dataResponse :
            error_message = 'DATA NOT FOUND'
            content = {
                "statusCode": 404,
                "statusDesc": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_404_NOT_FOUND, data=content)
        data = dataResponse
        # data = response
        error_message = []
    except Exception as ex:
        if 'AnonymousUser' in str(ex):
            error_message = 'Autorization Token'
            content = {
                "error_message": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=content)

    content = {
        "statusCode": 200,
        "statusCodeDesc": 'OK',
        "data": json.loads(json.dumps(data, default=lambda o: o.__dict__)),
        
    }

    response_status = (status.HTTP_200_OK if content["statusCode"] == 200 else status.HTTP_400_BAD_REQUEST)

    return Response(status=response_status, data=content)


@api_view(['PUT'])
def validate(request, controllerName):
    # barcode = request.data['barcode']
    serializer = UserSerializer(request.user)
    modelDA = BaseDA()
    modelResponse = BaseResponse()
    controller = controller_translator(controllerName)
    responseDA = controller_response(controllerName)
    data = []
    total_data = 0
    error_message = []
    try:
        # response = modelDA.update(controller,request)
        dataResponse = eval(responseDA)(request,serializer)
        
        if not dataResponse :
            error_message = 'DATA NOT FOUND'
            content = {
                "statusCode": 404,
                "statusDesc": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_404_NOT_FOUND, data=content)
        data = dataResponse
        # data = response
        error_message = []
    except Exception as ex:
        if 'AnonymousUser' in str(ex):
            error_message = 'Autorization Token'
            content = {
                "error_message": json.loads(json.dumps(error_message, default=lambda o: o.__dict__)),
            }
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=content)

    content = {
        "statusCode": 200,
        "statusCodeDesc": 'DATA BERHASIL DI VALIDATE',
        "data": json.loads(json.dumps(data, default=lambda o: o.__dict__)),
        
    }

    response_status = (status.HTTP_200_OK if content["statusCode"] == 200 else status.HTTP_400_BAD_REQUEST)

    return Response(status=response_status, data=content)
