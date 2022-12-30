from rest_framework import renderers
import json

class UserRenderer(renderers.JSONRenderer):
  print("render dlu")
  charset='utf-8'
  def render(self, data, accepted_media_type=None, renderer_context=None):
    response = ''
    if 'ErrorDetail' in str(data):
      print("masukkkk detail error1")
      response = json.dumps({'errors':data})
    if 'AttributeError' in str(data):
      response = json.dumps({'errors':data})
    if 'detail' in str(data):
      print("masukkkk detail error2")
      response = json.dumps({'errors':data})
    else:
      print("masukkkk detail error3")
      response = json.dumps(data)
    
    return response