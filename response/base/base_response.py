import xmlrpc.client

url = 'https://v4.amtiss.com'
db = 'v4'
username = 'admin' 
password = '4mti55'

# url = 'http://localhost:8015'
# db = 'v4'
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
                print(purchase_data,"====")
                if purchase_data:
                    for data in purchase_data:
                        purchase_ids = data['id']
                        name = data['name']
                        state = data['state']
                        date_order = data['date_order']
                        date_plan = data['date_planned']
                        po_id = data['id']
                        lines_obj  = models.execute_kw(db, uid, password, 'purchase.order.line', 'search_read', [[['order_id','=',po_id]]], {'fields': ['product_id','product_qty','qty_received']})
                        lines_po=[]
                        for line in lines_obj:
                            product_ids = line['product_id'][0]
                            product_name = line['product_id'][1]
                            product_qty = line['product_qty']
                            qty_received = line['qty_received']
                            lines_po.append(
                                {
                                    "productId": product_ids,
                                    "productName": product_name,
                                    'productqty': product_qty,
                                    'productQtyReceived': qty_received,
                                })
                    purchase.append({
                        'purchaseOrderId': purchase_ids,
                        'purchaseOrderName': name,
                        'purhcaseOrderState':state,
                        'purchaseOrderDateOrder': date_order,
                        'purchaseOrderReceiptDate': date_plan,
                        'purchaseOrderLine': lines_po,
                    })
            
            ### update stock di sini ###
            
            # ===== purchase order ===== #
            #efektive date jadi terisi

            # ===== purchase order line =====#
            #qty received berubah jadi 1



            #======= stockpicking ======#
            #state jadi berubah
            #date done jadi berubah


            #=======stock move =======#
            #state jadi berubah

            #======== stock move line ===== #
            #product qty jadi 0
            #product_uom_qty jadi 0
            #qty done jadi 1
            #state jadi done


            #=========== insert stock quant ========== #
            #product_id
            #location_id
            #quantity
            #in_date

            ############################
        return purchase
        
    def internal_transfer(self, response):
        internal = []
        # print(response)
        for x in response:
            id =x['id']
            type_id = x['picking_type_id'][0]
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            cek_inter = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['name','=','Internal Transfers']]], {'fields': ['name']})

            if len(cek_inter) > 0 :
                
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