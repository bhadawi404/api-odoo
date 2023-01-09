import xmlrpc.client



class BaseDA(object):
   
    #get all
    def getall(self, controllerName, limit=False, offset=False, serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        
        result = []
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if uid:
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            fields = models.execute_kw(db, uid, password, controllerName, 'fields_get', [], {'attributes': ['name']})
            
            fields_list = []
            for x in fields:
                fields_list.append(x)
            if limit:
                response =models.execute_kw(db, uid, password, controllerName, 'search_read', [[]], {'fields': fields_list,'limit':int(limit)})
            if offset:
                response =models.execute_kw(db, uid, password, controllerName, 'search_read', [[]], {'fields': fields_list,'offset':int(offset)})
            if offset and limit:
                response =models.execute_kw(db, uid, password, controllerName, 'search_read', [[]], {'fields': fields_list,'limit':int(limit),'offset':int(offset)})
            if not offset and not limit:
                response =models.execute_kw(db, uid, password, controllerName, 'search_read', [[]], {'fields': fields_list})
            if not response :
                response = []

            result = response
        else:
            response = 'Access Denied'
            result = response
        return result
    
    #get all
    def getbybarcode(self, controllerName,id,serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
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
    def getbyidscan(self, controllerName,barcode, serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        result = []
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if uid:

            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            fields = models.execute_kw(db, uid, password, controllerName, 'fields_get', [], {'attributes': ['name']})
            
            fields_list = []
            for x in fields:
                fields_list.append(x)
            
            response =models.execute_kw(db, uid, password, controllerName, 'search_read', [['|',['name','=',barcode],['picking_group.name','=',barcode]]], {'fields': fields_list})
            if not response:
                
                response = []

            result = response
        else:
            response = 'Access Denied'
            result = response
        return result
    
    #get id
    def getbyid(self, controllerName,id, serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        result = []
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if uid:
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            fields = models.execute_kw(db, uid, password, controllerName, 'fields_get', [], {'attributes': ['name']})
            
            fields_list = []
            for x in fields:
                fields_list.append(x)
            
            response =models.execute_kw(db, uid, password, controllerName, 'search_read', [[['id','=',id]]], {'fields': fields_list})

            if not response :
                response = []

            result = response
        else:
            response = 'Access Denied'
            result = response
        return result
    
    #get all
    def update(self,controllerName,id, serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        result = []
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        fields = models.execute_kw(db, uid, password, controllerName, 'fields_get', [], {'attributes': ['name']})
        
        fields_list = []
        for x in fields:
            fields_list.append(x)
        
        response =models.execute_kw(db, uid, password, controllerName, 'search_read', [[['id','=',id]]], {'fields': fields_list})

        if not response :
            response = []

        result = response
        return result

