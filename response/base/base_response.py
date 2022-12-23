import xmlrpc.client
from datetime import datetime

url = 'https://v4.amtiss.com'
db = 'v4'
username = 'admin' 
password = '4mti55'

# url = 'http://localhost:8015'
# db = 'v4'
# username = 'admin' 
# password = '4mti55'

# url = 'http://localhost:8015'
# db = 'v4_121222'
# username = 'admin' #username odoo
# password = '4mti55'

class BaseResponse(object):
    def product(self, response):
        result = []
        for x in response:
            uom_id = x['uom_id'][1]
            categ_id = x['categ_id'][1]
            result.append({
                'productId': x['id'],
                'productName': x['name'],
                'productNumber': x['default_code'],
                'productBarcode': x['barcode'],
                'productType':x['detailed_type'],
                'productUom': uom_id,
                'productCategory':categ_id,
                'productCost':x['standard_price'],
                'productStatus':x['active'],   
            })
        return result
    
    def stock_take(self, response):
        result = []
        for x in response:
            result.append({
                'productId': x['id']
            })
        return result
    
    def purchase_order(self, response):
        purchase = []
        for x in response:
            if x['state'] == 'assigned':
                origin = x['origin']
                common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
                uid = common.authenticate(db, username, password, {})
                models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                purchase_data  = models.execute_kw(db, uid, password, 'purchase.order', 'search_read', [[['name','=',origin]]], {'fields': []})
                if purchase_data:
                    for data in purchase_data:
                        purchase_ids = data['id']
                        name = data['name']
                        state = data['state']
                        date_order = data['date_order']
                        date_plan = data['date_planned']
                        vendor_name = data['partner_id'][1]
                        po_id = data['id']
                        picking_ids = x['id']
                        move_data = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',picking_ids]]], {'fields': ['id','purchase_line_id']})
                        move_line_list = []
                        for move in move_data:
                            move_ids = move['id']
                            purchase_line = move['purchase_line_id'][0]
                            order_line = models.execute_kw(db, uid, password, 'purchase.order.line', 'search_read', [[['id','=',purchase_line]]], {'fields': ['qty_received','product_qty']})
                            qty_received = order_line[0]['qty_received']
                            product_qty_request = order_line[0]['product_qty']
                            move_line_data = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',move['id']]]], {'fields': ['product_id','qty_done','product_qty','picking_id']})
                            for move_line in move_line_data:
                                move_line_ids = move_line['id']
                                product_ids = move_line['product_id'][0]
                                product_qty = move_line['product_qty']
                                product_name = move_line['product_id'][1]
                                qty_done = move_line['qty_done']
                                barcode_obj  = models.execute_kw(db, uid, password, 'product.template', 'search_read', [[['id','=',product_ids]]], {'fields': ['barcode']})
                                barcode = barcode_obj[0]['barcode']
                                move_line_list.append({
                                    "pickingId": picking_ids,
                                    "orderLineId": purchase_line,
                                    "moveId": move_ids,
                                    "moveLineId": move_line_ids,
                                    "productId": product_ids,
                                    "productBarcode": barcode,
                                    "productName": product_name,
                                    "productQtyRequestPO": product_qty_request,
                                    "productQtyReceived": qty_received,
                                    "productQtyDemand": product_qty,
                                    "productQtyDone": qty_done,
                                    
                                })   
                    purchase.append({
                        'purchaseOrderVendor': vendor_name,
                        'purchaseOrderId': purchase_ids,
                        'purchaseOrderName': name,
                        'purhcaseOrderState':state,
                        'purchaseOrderDateOrder': date_order,
                        'purchaseOrderReceiptDate': date_plan,
                        'purchaseOrderLine': move_line_list,
                    })
        return purchase
        
    def internal_transfer_in(self, response):
        internal = []
        # print(response)
        for x in response:
            id =x['id']
            type_id = x['picking_type_id'][0]
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            cek_inter = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['name','=','Internal Transfers']]], {'fields': ['name']})
           
            if cek_inter and x['state']=='assigned':
                stock_move  = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',id]]], {'fields': ['product_id','product_qty','id']})
                linesIT=[]
                for data in stock_move:
                    product_ids = data['product_id'][0]
                    product_name = data['product_id'][1]
                    product_qty = data['product_qty']
                    received  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',data['id']]]], {'fields': ['qty_done']})
                    qty_received = 0
                    for rc in received:
                        qty_received = rc['qty_done']
                    linesIT.append(
                        {
                            "stockMoveId": data['id'],
                            "productId": product_ids,
                            "productName": product_name,
                            'productqty': product_qty,
                            'productQtyReceived': qty_received,
                        })
                internal.append({
                    'NoPickingType': x['name'],
                    'SourceLocation': x['location_id'][1],
                    'DestinationLocation':x['location_dest_id'][1],
                    'ScheduleDate': x['scheduled_date'],
                    # 'MRID': x['mr_id'],
                    # 'AssetId': x['asset_id'],
                    'InternalTransferLine': linesIT,
                })
        return internal
    
    def internal_transfer_out(self, response):
        internal = []
        # print(response)
        for x in response:
            id =x['id']
            type_id = x['picking_type_id'][0]
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            cek_inter = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['name','=','Internal Transfers']]], {'fields': ['name']})
            if cek_inter and x['state']=='draft':
                stock_move  = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',id]]], {'fields': ['product_id','product_qty','id']})
                linesIT=[]
                for data in stock_move:
                    product_ids = data['product_id'][0]
                    product_name = data['product_id'][1]
                    product_qty = data['product_qty']
                    received  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',data['id']]]], {'fields': ['qty_done']})
                    qty_received = 0
                    for rc in received:
                        qty_received = rc['qty_done']
                    linesIT.append(
                        {
                            "stockMoveId": data['id'],
                            "productId": product_ids,
                            "productName": product_name,
                            'productqty': product_qty,
                            'productQtyReceived': qty_received,
                        })
                internal.append({
                    'NoPickingType': x['name'],
                    'SourceLocation': x['location_id'][1],
                    'DestinationLocation':x['location_dest_id'][1],
                    'ScheduleDate': x['scheduled_date'],
                    # 'MRID': x['mr_id'],
                    # 'AssetId': x['asset_id'],
                    'InternalTransferLine': linesIT,
                })
        return internal

    def consume(self, response):
        consume = []
        # print(response)
        for x in response:
            id =x['id']
            type_id = x['picking_type_id'][0]
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            consume_cek = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['name','=','Consume']]], {'fields': ['name']})

            # if len(consume_cek) > 0 & x['state']=='approved':
            if len(consume_cek) > 0:
                stock_move  = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',id]]], {'fields': ['product_id','product_qty','id']})
                linesConsume=[]
                for data in stock_move:
                    product_ids = data['product_id'][0]
                    product_name = data['product_id'][1]
                    product_qty = data['product_qty']
                    received  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',data['id']]]], {'fields': ['qty_done']})
                    qty_received = 0
                    for rc in received:
                        qty_received = rc['qty_done']
                    linesConsume.append(
                        {
                            "stockMoveId": data['id'],
                            "productId": product_ids,
                            "productName": product_name,
                            'productqty': product_qty,
                            'productQtyReceived': qty_received,
                        })
                consume.append({
                    'NoPickingType': x['name'],
                    'SourceLocation': x['location_id'][1],
                    'DestinationLocation':x['location_dest_id'][1],
                    'ScheduleDate': x['scheduled_date'],
                    # 'MRID': x['mr_id'],
                    # 'AssetId': x['asset_id'],
                    'ConsumeLine': linesConsume,
                })
        return consume
    
    def return_product(self, response):
        return_product = []
        # print(response)
        for x in response:
            id =x['id']
            type_id = x['picking_type_id'][0]
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            cek_inter = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['name','in',['Internal Transfers','Consume']]]], {'fields': ['name']})
            if len(cek_inter) > 0 :
                common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
                uid = common.authenticate(db, username, password, {})
                models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                stock_move  = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',id]]], {'fields': ['product_id','product_qty','id']})
                linesReturn=[]
                for data in stock_move:
                    product_ids = data['product_id'][0]
                    product_name = data['product_id'][1]
                    product_qty = data['product_qty']
                    received  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',data['id']]]], {'fields': ['qty_done']})
                    qty_received = 0
                    for rc in received:
                        qty_received = rc['qty_done']
                    linesReturn.append(
                        {
                            "productId": product_ids,
                            "productName": product_name,
                            'productqty': product_qty,
                            'productQtyReceived': qty_received,
                        })
                return_product.append({
                    'NoPickingType': x['name'],
                    'SourceLocation': x['location_id'][1],
                    'DestinationLocation':x['location_dest_id'][1],
                    'ScheduleDate': x['scheduled_date'],
                    # 'MRID': x['mr_id'],
                    # 'AssetId': x['asset_id'],
                    'ReturnLine': linesReturn,
                })
        return return_product

    def validate_purchase(self, request):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.authenticate(db, username, password, {})
        date_now = datetime.now()
        now = date_now.strftime('%Y-%m-%d %H:%M:%S')
        
        picking_ids = request.data['pickingId']
        move_line_ids = request.data['moveLineId']
        qty_done = request.data['productQtyDone']
        move_ids = request.data['moveId']
        order_line_ids = request.data['orderLineId']
        order_line = models.execute_kw(db, uid, password, 'purchase.order.line', 'search_read', [[['id','=',order_line_ids]]], {'fields': ['qty_received']})
        
        qty_received = order_line[0]['qty_received']
        
        vals_order_line = {
            "qty_received":  qty_done + qty_received
        } 
        
        models.execute_kw(db, uid, password, 'purchase.order.line', 'write', [[order_line_ids], vals_order_line])
        
        vals_stock_move_line = {
            "product_uom_qty":0,
            "qty_done": qty_done,
            "state": 'done'
        }

        #update State & date done di stock Picking
        models.execute_kw(db, uid, password, 'stock.picking', 'write', [[picking_ids], {'state': "done",'date_done': now}])
        
        #update Product uom qty 0, qty_done(request), state done
        models.execute_kw(db, uid, password, 'stock.move.line', 'write', [[move_line_ids], vals_stock_move_line])
        
        #update stock move state done
        models.execute_kw(db, uid, password, 'stock.move', 'write', [[move_ids], {'state': "done"}])
        
        return True

    def validate_internal_transfer_out(self, response, request):
        validate = []
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        date_now = datetime.now()
        now = date_now.strftime('%Y-%m-%d %H:%M:%S')
        for x in response:
            pickingid = x['id']
            
            stock_move = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',pickingid]]], {'fields': ['id','company_id','product_id','product_uom','product_qty','product_uom_qty','location_dest_id','reference']})
            for sm in stock_move:
                
                ids_stock_move = sm['id']
                cek_stock_move_line = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',ids_stock_move]]], {'fields': ['id']})
                if not cek_stock_move_line:
                    print("sini")
                    models.execute_kw(db, uid, password, 'stock.move.line', 'create', [
                        {
                            "picking_id" : pickingid,
                            "move_id":ids_stock_move,
                            "company_id": sm['company_id'],
                            "product_id": sm['product_id'],
                            "product_uom_id": sm['product_uom_id'],
                            "product_qty": sm['product_qty'],
                            "product_uom_qty": sm['product_uom_qty'],
                            "qty_done": 0,
                            "date": now,
                            "location_id": sm['location_id'],
                            "product_uom_qty": sm['product_uom'],
                            "location_dest_id": sm['location_dest_id'],
                            "reference": sm['reference'],
                            'state': "assigned",
                            "reservation_date":date_now
                        }
                    ])
                    print("dc")
                models.execute_kw(db, uid, password, 'stock.move', 'write', [[ids_stock_move], {'state': "assigned","reservation_date":date_now}])
            models.execute_kw(db, uid, password, 'stock.picking', 'write', [[pickingid], {'state': "assigned"}])
            
            return True
    
    def validate_internal_transfer_in(self, response, request):
        validate = []
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        product = request.data['product']
        date_now = datetime.now()
        now = date_now.strftime('%Y-%m-%d %H:%M:%S')
        for x in response:
            picking_ids = x['id']
            location_id = x['location_id']
            location_dest_id = x['location_dest_id']
            company_id = x['company_id']
            
            for pd in product:
                idprod = pd['productId']
                qty_done = pd['qty_done']
                stock_move  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['picking_id','=',picking_ids],['product_id','=',idprod]]], {'fields': ['product_qty','id','product_uom_qty','qty_done','state','move_id']})
                for move in stock_move:
                    move_ids = move['id']
                    move = move['move_id']
                    
                    # uom_qty = qty_done - move['product_uom_qty']
                    vals = {
                        "qty_done": qty_done,
                        "state": 'done'
                    }
                    models.execute_kw(db, uid, password, 'stock.move.line', 'write', [[move_ids], vals])

                    models.execute_kw(db, uid, password, 'stock.move', 'write', [[move], {'state': "done"}])
           
                    models.execute_kw(db, uid, password, 'product.quant', 'create', [
                                {
                                'product_id': idprod,
                                'company_id' : company_id,
                                'location_id' : location_dest_id,
                                'in_date'    : now,
                                'quantity'   : qty_done,
                                }
                                ])
                    models.execute_kw(db, uid, password, 'product.quant', 'create', [
                                {
                                'product_id': idprod,
                                'company_id' : company_id,
                                'location_id' : location_id,
                                'in_date'    : now,
                                'quantity'   : qty_done-(qty_done*2),
                                }
                                ])
            models.execute_kw(db, uid, password, 'stock.picking', 'write', [[picking_ids], {'state': "done",'date_done': now}])
                        
            return True           
    
    def validate_return(self, response, request):
        validate = []
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        qty_done = request.data['qty_done'] 
        date_now = datetime.now()
        
        now = date_now.strftime('%Y-%m-%d %H:%M:%S')
        for x in response:
            purchaseId = x['id']
            purchaseName = x['name']
            product = request.data['product']
            stock_picking_obj  = models.execute_kw(db, uid, password, 'stock.picking', 'search_read', [[['origin','=',purchaseName],['state','=','assigned']]], {'fields': ['location_id','location_dest_id','picking_type_id','partner_id','company_id']})
            for x in stock_picking_obj:
                create_stock_picking = models.execute_kw(db, uid, password, 'stock.picking', 'create', [
                                    {
                                        "move_type":"direct",
                                        "state":"done",
                                        "scheduled_date": now,
                                        "date" :now,
                                        "date_done" : now,
                                        "location_id": x["location_id"][0],
                                        "location_dest_id": x["location_dest_id"][0],
                                        "picking_type_id": x["picking_type_id"][0],
                                        "partner_id": x["partner_id"][0],
                                        "company_id": x["company_id"][0]
                                    }
                                    ])
                

                # stock_move  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['picking_id','=',picking_ids]]], {'fields': ['product_id','product_qty','id','product_uom_qty','qty_done','state']})
                for pd in product:
                    idprod = pd['productId']
                    qty_done = pd['qty_done']
                    vals = {
                            "name"      : "sss",
                            "picking_id" : create_stock_picking['id'],
                            "product_id" : idprod,
                            "product_uom_qty": qty_done,
                            "product_qty": qty_done,
                            "company_id": x["company_id"][0],
                            "date" :now,
                            "location_id": x["location_id"][0],
                            "state": 'done'
                    }
                    create_stock_move = models.execute_kw(db, uid, password, 'stock.move', 'create', [vals])
                    vals = {
                            "move_id" : create_stock_move['id'],
                            "picking_id" : create_stock_picking['id'],
                            "reference" : create_stock_picking['name'],
                            "product_id" : idprod,
                            "product_uom_qty": 0,
                            "product_qty": 0,
                            "qty_done": qty_done,
                            "company_id": x["company_id"][0],
                            "date" :now,
                            "location_id": x["location_id"][0],
                            "state": 'done'
                    }
                    models.execute_kw(db, uid, password, 'stock.move_line', 'create', [vals])
                    models.execute_kw(db, uid, password, 'product.quant', 'create', [
                                    {
                                    'product_id': idprod,
                                    'company_id' : x["company_id"][0],
                                    "location_id": x["location_id"][0],
                                    'in_date'    : now,
                                    'quantity'   : qty_done,
                                    }
                                    ])
                        
            return True        
                