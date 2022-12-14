import xmlrpc.client

url = 'https://v4.amtiss.com'
db = 'v4'
username = 'admin'
password = '4mti55'


# url = 'http://localhost:8015'
# db = 'v4'
# username = 'admin' #username odoo
# password = '4mti55'



class BaseDA(object):
   
    #get all
    def getall(self, controllerName):
        result = []
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if uid:
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            fields = models.execute_kw(db, uid, password, controllerName, 'fields_get', [], {'attributes': ['name']})
            
            fields_list = []
            for x in fields:
                fields_list.append(x)
            
            response =models.execute_kw(db, uid, password, controllerName, 'search_read', [[]], {'fields': fields_list})

            if not response :
                response = []

            result = response
        else:
            response = 'Access Denied'
            result = response
        return result
    
    #get all
    def getbybarcode(self, controllerName,id):
        result = []
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if uid:
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            fields = models.execute_kw(db, uid, password, controllerName, 'fields_get', [], {'attributes': ['name']})
            
            fields_list = []
            for x in fields:
                fields_list.append(x)
            
            response =models.execute_kw(db, uid, password, controllerName, 'search_read', [[['barcode','=',id]]], {'fields': fields_list})

            if not response :
                response = []

            result = response
        else:
            response = 'Access Denied'
            result = response
        return result
    
    
    #get all
    def getbyidscan(self, controllerName,barcode):
        result = []
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if uid:
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            fields = models.execute_kw(db, uid, password, controllerName, 'fields_get', [], {'attributes': ['name']})
            
            fields_list = []
            for x in fields:
                fields_list.append(x)
            
            response =models.execute_kw(db, uid, password, controllerName, 'search_read', [[['name','=',barcode]]], {'fields': fields_list})

            if not response :
                response = []

            result = response
        else:
            response = 'Access Denied'
            result = response
        return result
    
    #get all
    def update(self,request, controllerName,id):
        result = []
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        fields = models.execute_kw(db, uid, password, controllerName, 'fields_get', [], {'attributes': ['name']})
        
        fields_list = []
        for x in fields:
            fields_list.append(x)
        
        response =models.execute_kw(db, uid, password, controllerName, 'search_read', [[['id','=',id],['state','=','assigned']]], {'fields': fields_list})

        if not response :
            response = []

        result = response
        return result

