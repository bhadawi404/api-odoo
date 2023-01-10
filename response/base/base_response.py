import xmlrpc.client
from datetime import datetime

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
    
    def purchase_order(self, response, serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        purchase = []
        print("masuk response")
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
                        'purchaseOrderLocationSourceId': x['location_id'][0],
                        'purchaseOrderLocationDestinationId': x['location_dest_id'][0],
                        'purchaseOrderCompanyId': x['company_id'][0]
                    })
        return purchase
        
    def internal_transfer_in(self, response,serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        internal = []
        # print(response)
       
        for x in response:
            id =x['id']
            type_id = x['picking_type_id'][0]
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            cek_inter = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['sequence_code','=','INT']]], {'fields': ['name']})
            print(cek_inter)
            print(x['state'])
            print(id)
            print(type_id)
            if cek_inter and x['state']=='assigned':
                stock_move  = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',id]]], {'fields': ['product_id','product_qty','id']})
                linesIT=[]
                for data in stock_move:
                    move_ids = data['id']
                    move_line_ids = data['id']
                    product_ids = data['product_id'][0]
                    product_qty = data['product_qty']
                    product_name = data['product_id'][1]
                    received  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',data['id']]]], {'fields': ['product_id','qty_done','product_qty']})
                    qty_done = 0
                    for rc in received:
                        qty_done = rc['qty_done']
                    barcode_obj  = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['id','=',product_ids]]], {'fields': ['barcode']})
                    barcode = barcode_obj[0]['barcode']
                    linesIT.append(
                        {
                            "moveId": move_ids,
                            "moveLineId": move_line_ids,
                            "productId": product_ids,
                            "productBarcode": barcode,
                            "productName": product_name,
                            "productQtyReceived": product_qty,
                            "productQtyDemand": product_qty,
                            "productQtyDone": qty_done,
                        })
                internal.append({
                    'PickingId' : x['id'],
                    'NoPickingType': x['name'],
                    'SourceLocation': x['location_id'][1],
                    'DestinationLocation':x['location_dest_id'][1],
                    'ScheduleDate': x['scheduled_date'],
                    # 'MRID': x['mr_id'],
                    # 'AssetId': x['asset_id'],
                    'MRID':"",
                    'AssetId': "",
                    'LocationSourceId': x['location_id'][0],
                    'LocationDestinationId': x['location_dest_id'][0],
                    'CompanyId': x['company_id'][0],
                    'InternalTransferLine': linesIT,
                })
        return internal
    
    def internal_transfer_out(self, response,serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        internal = []
        
        for x in response:
            id =x['id']
            type_id = x['picking_type_id'][0]
            
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            cek_inter = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['sequence_code','=','INT']]], {'fields': ['name']})
            if cek_inter and x['state']=='draft':
                stock_move  = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',id]]], {'fields': ['product_id','product_qty','id']})
                linesIT=[]
                
                for data in stock_move:
                    move_ids = data['id']
                    move_line_ids = data['id']
                    product_ids = data['product_id'][0]
                    product_qty = data['product_qty']
                    product_name = data['product_id'][1]
                    received  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',data['id']]]], {'fields': ['product_id','qty_done','product_qty']})
                    qty_done = 0
                    print(stock_move)
                    for rc in received:
                        qty_done = rc['qty_done']
                    barcode_obj  = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['id','=',product_ids]]], {'fields': ['barcode']})
                    barcode = barcode_obj[0]['barcode']
                    print("BISA")
                    print(barcode_obj)
                    linesIT.append(
                        {
                            "moveId": move_ids,
                            "moveLineId": move_line_ids,
                            "productId": product_ids,
                            "productBarcode": barcode,
                            "productName": product_name,
                            "productQtyReceived": product_qty,
                            "productQtyDemand": product_qty,
                            "productQtyDone": qty_done,
                        })
                internal.append({
                    'PickingId' : x['id'],
                    'NoPickingType': x['name'],
                    'SourceLocation': x['location_id'][1],
                    'DestinationLocation':x['location_dest_id'][1],
                    'ScheduleDate': x['scheduled_date'],
                    'LocationSourceId': x['location_id'][0],
                    'LocationDestinationId': x['location_dest_id'][0],
                    'CompanyId': x['company_id'][0],
                    # 'MRID': x['mr_id'],
                    # 'AssetId': x['asset_id'],
                    'MRID':"",
                    'AssetId': "",
                    'InternalTransferLine': linesIT,
                })
        
        return internal

    def consume(self, response,serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        consume = []
        
        # print(response)
        for x in response:
            id =x['id']
            type_id = x['picking_type_id'][0]
            
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            consume_cek = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['name','=','Consume']]], {'fields': ['name']})
            
            # if len(consume_cek) > 0 & x['state']=='assigned':
            if len(consume_cek) > 0:
               
                stock_move  = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',id]]], {'fields': ['product_id','product_qty','id']})
                linesConsume=[]
                print("bisa")
                for data in stock_move:
                    move_ids = data['id']
                    move_line_ids = data['id']
                    product_ids = data['product_id'][0]
                    product_qty = data['product_qty']
                    product_name = data['product_id'][1]
                    qty_done = 0
                    received  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',data['id']]]], {'fields': ['product_id','qty_done','product_qty','picking_id']})
                    qty_received = 0
                    for rc in received:
                        qty_received = rc['qty_done']
                    barcode_obj  = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['id','=',product_ids]]], {'fields': ['barcode']})
                    barcode = barcode_obj[0]['barcode']
                    linesConsume.append(
                        {
                            "moveId": move_ids,
                            "moveLineId": move_line_ids,
                            "productId": product_ids,
                            "productBarcode": barcode,
                            "productName": product_name,
                            "productQtyReceived": qty_received,
                            "productQtyDemand": product_qty,
                            "productQtyDone": qty_done,
                        })
                consume.append({
                    'NoPickingType': x['name'],
                    'SourceLocation': x['location_id'][1],
                    'DestinationLocation':x['location_dest_id'][1],
                    'ScheduleDate': x['scheduled_date'],
                    'LocationSourceId': x['location_id'][0],
                    'LocationDestinationId': x['location_dest_id'][0],
                    'CompanyId': x['company_id'][0],
                    # 'MRID': x['mr_id'],
                    # 'AssetId': x['asset_id'],
                    'MRID':"",
                    'AssetId': "",
                    'ConsumeLine': linesConsume,
                })
        return consume
    
    def return_product(self, response,serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        return_product = []
        # print(response)
        for x in response:
            id =x['id']
            type_id = x['picking_type_id'][0]
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            cek_inter = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['name','!=','Returns']]], {'fields': ['name']})
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
                    linesReturn.append(
                        {
                            "productId": product_ids,
                            "productName": product_name,
                            'productqty': product_qty,
                            'productQtyReceived': 0,
                        })
                return_product.append({
                    'NoPickingType': x['name'],
                    'SourceLocation': x['location_id'][1],
                    'DestinationLocation':x['location_dest_id'][1],
                    'ScheduleDate': x['scheduled_date'],
                    'LocationSourceId': x['location_id'][0],
                    'LocationDestinationId': x['location_dest_id'][0],
                    'CompanyId': x['company_id'][0],
                    # 'MRID': x['mr_id'],
                    # 'AssetId': x['asset_id'],
                    'ReturnLine': linesReturn,
                })
        return return_product

    def validate_purchase(self, request, serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.authenticate(db, username, password, {})
        date_now = datetime.now()
        now = date_now.strftime('%Y-%m-%d %H:%M:%S')
        
        product = request.data['product']
        picking_ids = request.data['pickingId']
        location_ids = request.data['purchaseOrderLocationSourceId']
        destination_ids = request.data['purchaseOrderLocationDestinationId']
        company_ids = request.data['purchaseOrderCompanyId']
        picking_new_id = None
        for pd in product:
            product_id = pd['productId']
            order_line_ids = pd['orderLineId']
            order_line = models.execute_kw(db, uid, password, 'purchase.order.line', 'search_read', [[['id','=',order_line_ids]]], {'fields': ['qty_received','product_qty']})
            move_line_ids = pd['moveLineId']
            qty_done = pd['productQtyDone']
            move_ids = pd['moveId']
            
            qty_received = order_line[0]['qty_received']
            all_qty = qty_done + qty_received
            
            vals_order_line = {
                "qty_received":  all_qty
            } 
            models.execute_kw(db, uid, password, 'purchase.order.line', 'write', [[order_line_ids], vals_order_line])
            
            vals_stock_move_line = {
                "product_uom_qty":0,
                "qty_done": qty_done,
                "state": 'done'
            }
            #update Product uom qty 0, qty_done(request), state done
            models.execute_kw(db, uid, password, 'stock.move.line', 'write', [[move_line_ids], vals_stock_move_line])
            
            #update stock move state done
            models.execute_kw(db, uid, password, 'stock.move', 'write', [[move_ids], {'state': "done"}])

            cek_product = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',product_id]]], {'fields': ['id']})
            
            if cek_product:
                cek_product_location = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',product_id],['company_id','=',company_ids],['location_id','=',destination_ids]]], {'fields': ['id','quantity']})
                cek_product_vendor = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',product_id],['location_id','=',location_ids]]], {'fields': ['id','quantity']})
                stock_quant_vendor_ids = cek_product_vendor[0]['id']
                quantity_stock_vendor = cek_product_vendor[0]['quantity'] - qty_done
                stock_quant_ids = cek_product_location[0]['id']
                quantity_stock = cek_product_location[0]['quantity'] + qty_done
                if cek_product_location:
                    models.execute_kw(db, uid, password, 'stock.quant', 'write', [[stock_quant_ids], {'quantity': quantity_stock}])
                if cek_product_vendor:
                    models.execute_kw(db, uid, password, 'stock.quant', 'write', [[stock_quant_vendor_ids], {'quantity': quantity_stock_vendor}])
            elif not cek_product:
                models.execute_kw(db, uid, password, 'stock.quant', 'create', [
                                    {
                                    'product_id': product_id,
                                    'company_id' : company_ids,
                                    'location_id' : destination_ids,
                                    'in_date'    : now,
                                    'quantity'   : qty_done,
                                    }
                                    ])
                models.execute_kw(db, uid, password, 'stock.quant', 'create', [
                            {
                            'product_id': product_id,
                            'location_id' : location_ids,
                            'in_date'    : now,
                            'quantity'   : qty_done-(qty_done*2),
                            }
                            ])
            #create backorder
            if all_qty < order_line[0]['product_qty']:
                if not picking_new_id:
                    #create stock Picking
                    picking_old = models.execute_kw(db, uid, password, 'stock.picking', 'search_read', [[['id','=',picking_ids]]], 
                    {'fields': 
                    ['message_main_attachment_id','origin','note','move_type','group_id','priority',
                    'scheduled_date','date_deadline','has_deadline_issue','location_id',
                    'location_dest_id','picking_type_id','partner_id','company_id','mr_id',
                    'asset_id','assignment_id','sale_id','amtiss_material_request_id',
                    'batch_id','picking_group']}) 
                    if picking_old['picking_group']:
                        create_picking = models.execute_kw(db, uid, password, 'stock.picking', 'create', [
                                    {
                                    'message_main_attachment_id': picking_old[0]['message_main_attachment_id'],
                                    'origin': picking_old[0]['origin'],
                                    'note': picking_old[0]['note'],
                                    'backorder_id' : picking_ids,
                                    'move_type': picking_old['move_type'],
                                    'state': 'assigned',
                                    'group_id': picking_old[0]['group_id'],
                                    'priority': picking_old['priority'],
                                    'scheduled_date': picking_old[0]['scheduled_date'],
                                    'date_deadline': picking_old[0]['date_deadline'],
                                    'date': now,
                                    'has_deadline_issue': picking_old[0]['has_deadline_issue'],
                                    'location_id': picking_old[0]['location_id'],
                                    'location_dest_id': picking_old[0]['location_dest_id'],
                                    'picking_type_id': picking_old[0]['picking_type_id'],
                                    'partner_id': picking_old[0]['partner_id'],
                                    'company_id': picking_old[0]['company_id'],
                                    'mr_id': picking_old[0]['mr_id'],
                                    'asset_id': picking_old[0]['asset_id'],
                                    'assignment_id': picking_old[0]['assignment_id'],
                                    'amtiss_material_request_id': picking_old[0]['amtiss_material_request_id'],
                                    'batch_id': picking_old[0]['batch_id'],
                                    'picking_group': picking_old[0]['picking_group'],
                                    
                                    }
                                    ])
                    else:
                        create_picking = models.execute_kw(db, uid, password, 'stock.picking', 'create', [
                                    {
                                    'message_main_attachment_id': picking_old[0]['message_main_attachment_id'],
                                    'origin': picking_old[0]['origin'],
                                    'note': picking_old[0]['note'],
                                    'backorder_id' : picking_ids,
                                    'move_type': picking_old['move_type'],
                                    'state': 'assigned',
                                    'group_id': picking_old[0]['group_id'],
                                    'priority': picking_old['priority'],
                                    'scheduled_date': picking_old[0]['scheduled_date'],
                                    'date_deadline': picking_old[0]['date_deadline'],
                                    'date': now,
                                    'has_deadline_issue': picking_old[0]['has_deadline_issue'],
                                    'location_id': picking_old[0]['location_id'],
                                    'location_dest_id': picking_old[0]['location_dest_id'],
                                    'picking_type_id': picking_old[0]['picking_type_id'],
                                    'partner_id': picking_old[0]['partner_id'],
                                    'company_id': picking_old[0]['company_id'],
                                    'mr_id': picking_old[0]['mr_id'],
                                    'asset_id': picking_old[0]['asset_id'],
                                    'assignment_id': picking_old[0]['assignment_id'],
                                    'amtiss_material_request_id': picking_old[0]['amtiss_material_request_id'],
                                    'batch_id': picking_old[0]['batch_id'],
                                    'picking_group': picking_ids,
                                    }
                                    ])
                    picking_new_id =  create_picking.id 
                    print("pic")
                    print(picking_new_id) 

                    #create stock move
                    move_old = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['id','=',move_ids]]], 
                    {'fields': 
                    ['name','sequence','priority','company_id','product_id','description_picking',
                    'product_qty','product_uom_qty','product_uom','location_id',
                    'location_dest_id','partner_id','price_unit','origin','procure_method','scrapped','group_id','rule_id'
                    'propagate_cancel','delay_alert_date','picking_type_id','is_inventory','origin_returned_move_id','restrict_partner_id',
                    'warehouse_id'
                    ]}) 
                    models.execute_kw(db, uid, password, 'stock.move', 'create', [
                                    {
                                    'name': move_old['name'],
                                    'sequence': move_old['sequence'],
                                    'priority': move_old['priority'],
                                    'company_id': move_old[0]['company_id'],
                                    'product_id': move_old[0]['product_id'],
                                    'description_picking': move_old['description_picking'],
                                    'product_qty': move_old['product_qty'],
                                    'product_uom_qty': move_old['product_uom_qty'],
                                    'product_uom': move_old[0]['product_uom'],
                                    'location_id': move_old[0]['location_id'],
                                    'location_dest_id': move_old[0]['location_dest_id'],
                                    'partner_id': move_old[0]['partner_id'],
                                    'picking_id': picking_new_id,
                                    'state' : 'assigned',
                                    'price_unit': move_old['price_unit'],
                                    'origin': move_old['origin'],
                                    'procure_method': move_old['procure_method'],
                                    'scrapped': move_old['scrapped'],
                                    'group_id': move_old[0]['group_id'],
                                    'rule_id': move_old[0]['rule_id'],
                                    'propagate_cancel': move_old['propagate_cancel'],
                                    'delay_alert_date': move_old['delay_alert_date'],
                                    'picking_type_id': move_old[0]['picking_type_id'],
                                    'is_inventory': move_old['is_inventory'],
                                    'origin_returned_move_id': move_old[0]['origin_returned_move_id'],
                                    'restrict_partner_id': move_old[0]['restrict_partner_id'],
                                    'warehouse_id': move_old[0]['warehouse_id'],
                                    }
                                    ])
                else:
                    #create stock move
                    print("pic")
                    print(picking_new_id)
                    move_old = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['id','=',move_ids]]], 
                    {'fields': 
                    ['name','sequence','priority','company_id','product_id','description_picking',
                    'product_qty','product_uom_qty','product_uom','location_id',
                    'location_dest_id','partner_id','price_unit','origin','procure_method','scrapped','group_id','rule_id'
                    'propagate_cancel','delay_alert_date','picking_type_id','is_inventory','origin_returned_move_id','restrict_partner_id',
                    'warehouse_id'
                    ]}) 
                    models.execute_kw(db, uid, password, 'stock.move', 'create', [
                                    {
                                    'name': move_old['name'],
                                    'sequence': move_old['sequence'],
                                    'priority': move_old['priority'],
                                    'company_id': move_old[0]['company_id'],
                                    'product_id': move_old[0]['product_id'],
                                    'description_picking': move_old['description_picking'],
                                    'product_qty': move_old['product_qty'],
                                    'product_uom_qty': move_old['product_uom_qty'],
                                    'product_uom': move_old[0]['product_uom'],
                                    'location_id': move_old[0]['location_id'],
                                    'location_dest_id': move_old[0]['location_dest_id'],
                                    'partner_id': move_old[0]['partner_id'],
                                    'picking_id': picking_new_id,
                                    'state' : 'assigned',
                                    'price_unit': move_old['price_unit'],
                                    'origin': move_old['origin'],
                                    'procure_method': move_old['procure_method'],
                                    'scrapped': move_old['scrapped'],
                                    'group_id': move_old[0]['group_id'],
                                    'rule_id': move_old[0]['rule_id'],
                                    'propagate_cancel': move_old['propagate_cancel'],
                                    'delay_alert_date': move_old['delay_alert_date'],
                                    'picking_type_id': move_old[0]['picking_type_id'],
                                    'is_inventory': move_old['is_inventory'],
                                    'origin_returned_move_id': move_old[0]['origin_returned_move_id'],
                                    'restrict_partner_id': move_old[0]['restrict_partner_id'],
                                    'warehouse_id': move_old[0]['warehouse_id'],
                                    }
                                    ]) 

        #update State & date done di stock Picking
        models.execute_kw(db, uid, password, 'stock.picking', 'write', [[picking_ids], {'state': "done",'date_done': now}])
        
        return True

    def validate_internal_transfer_out(self, request, serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        date_now = datetime.now()
        now = date_now.strftime('%Y-%m-%d %H:%M:%S')
        product = request.data['product']
        picking_ids = request.data['pickingId']
        for pd in product:
            moveids = pd['moveId']
            vals_stock_move = {
                "reservation_date":now,
                "state": 'assigned'
            } 
            models.execute_kw(db, uid, password, 'stock.move', 'write', [[moveids], vals_stock_move])
        return True
    
    def validate_internal_transfer_in(self, response, request, serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        product = request.data['product']
        date_now = datetime.now()
        now = date_now.strftime('%Y-%m-%d %H:%M:%S')
        picking_ids = request.data['PickingId']
        location_ids = request.data['LocationSourceId']
        destination_ids = request.data['LocationDestinationId']
        company_ids = request.data['CompanyId']
        
        for pd in product:
            moveids = pd['moveId']
            product_id = pd['productId']
            qty_done = pd['productQtyDone']
            stock_move  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',moveids]]], {'fields': ['product_qty','id','product_uom_qty','qty_done','state','move_id']})
            print(len(stock_move))
            if len(stock_move)>0 :
                for move in stock_move:
                    move_ids = move['id']
                    move = move['move_id']
                    # uom_qty = qty_done - move['product_uom_qty']
                    vals = {
                        "qty_done": qty_done,
                        "state": 'done'
                    }
                    models.execute_kw(db, uid, password, 'stock.move.line', 'write', [[move_ids], vals])
                    print("line 1")
            else:
                print("create line 1")
                # stock_move = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['id','=',moveids]]], {'fields': ['id','company_id','product_id','location_id','product_qty','product_uom_qty','location_dest_id','reference','product_uom']})
                # for sm in stock_move:
                #     print("create line 2")
                #     ids_stock_move = sm['id']
                #     vals = {
                #             'picking_id' : picking_ids,
                #             'move_id':      ids_stock_move,
                #             'company_id': sm['company_id'][0],
                #             'product_id': sm['product_id'][0],
                #             'product_uom_id': sm['product_uom'][0],
                #             'product_qty': sm['product_qty'],
                #             'product_uom_qty': sm['product_uom_qty'],
                #             'qty_done': qty_done,
                #             'location_id': sm['location_id'][0],
                #             'location_dest_id': sm['location_dest_id'][0],
                #             'reference': sm['reference'],
                #             'state': "done",
                #             'date' : now
                #             }
                #     print("create line 3")
                #     print(vals)
                #     m = models.execute_kw(db, uid, password, 'stock.move.line', 'create', [vals])
                #     print(m)
                    # models.execute_kw(db, uid, password, 'stock.move.line', 'create', [
                    #             {
                    #             'picking_id' : picking_ids,
                    #             'move_id':      ids_stock_move,
                    #             'company_id': sm['company_id'][0],
                    #             'product_id': sm['product_id'][0],
                    #             'product_uom_id': sm['product_uom'][0],
                    #             'product_qty': sm['product_qty'],
                    #             'product_uom_qty': sm['product_uom_qty'],
                    #             'qty_done': qty_done,
                    #             'location_id': sm['location_id'][0],
                    #             'location_dest_id': sm['location_dest_id'][0],
                    #             'reference': sm['reference'],
                    #             'state': "done",
                    #             'date' : now
                    #             }
                    #             ])
                    # print("line 2")
           

        cek_product_dest = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',product_id],['company_id','=',company_ids],['location_id','=',destination_ids]]], {'fields': ['id','quantity']})
        if cek_product_dest:
            stock_quant_ids = cek_product_dest[0]['id']
            quantity_stock = cek_product_dest[0]['quantity'] + qty_done
            models.execute_kw(db, uid, password, 'stock.quant', 'write', [[stock_quant_ids], {'quantity': quantity_stock}])
        else :
            models.execute_kw(db, uid, password, 'stock.quant', 'create', [
                                {
                                'product_id': product_id,
                                'company_id' : company_ids,
                                'location_id' : destination_ids,
                                'in_date'    : now,
                                'quantity'   : qty_done,
                                }
                                ])
        cek_product_lock = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',product_id],['company_id','=',company_ids],['location_id','=',location_ids]]], {'fields': ['id','quantity']})
        if cek_product_lock:
            stock_quant_lock_ids = cek_product_lock[0]['id']
            quantity_stock_lock = cek_product_lock[0]['quantity'] - qty_done
            models.execute_kw(db, uid, password, 'stock.quant', 'write', [[stock_quant_lock_ids], {'quantity': quantity_stock_lock}])
        else:
            models.execute_kw(db, uid, password, 'stock.quant', 'create', [
                        {
                        'product_id': product_id,
                        'company_id' : company_ids,
                        'location_id' : location_ids,
                        'in_date'    : now,
                        'quantity'   : qty_done-(qty_done*2),
                        }
                        ])  
        models.execute_kw(db, uid, password, 'stock.move', 'write', [[moveids], {'state': "done"}]) 
        models.execute_kw(db, uid, password, 'stock.picking', 'write', [[picking_ids], {'state': "done",'date_done': now}])
        
        return True  

    def validate_consume(self, response, request, serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        product = request.data['product']
        date_now = datetime.now()
        now = date_now.strftime('%Y-%m-%d %H:%M:%S')
        picking_ids = request.data['PickingId']
        location_ids = request.data['LocationSourceId']
        destination_ids = request.data['LocationDestinationId']
        company_ids = request.data['CompanyId']
        
        for pd in product:
            moveids = pd['moveId']
            product_id = pd['productId']
            qty_done = pd['productQtyDone']
            stock_move  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',moveids]]], {'fields': ['product_qty','id','product_uom_qty','qty_done','state','move_id']})
            print(len(stock_move))
            if len(stock_move)>0 :
                for move in stock_move:
                    move_ids = move['id']
                    move = move['move_id']
                    # uom_qty = qty_done - move['product_uom_qty']
                    vals = {
                        "qty_done": qty_done,
                        "state": 'done'
                    }
                    models.execute_kw(db, uid, password, 'stock.move.line', 'write', [[move_ids], vals])
                    print("line 1")
            else:
                print("create line 1")
                # stock_move = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['id','=',moveids]]], {'fields': ['id','company_id','product_id','location_id','product_qty','product_uom_qty','location_dest_id','reference','product_uom']})
                # for sm in stock_move:
                #     print("create line 2")
                #     ids_stock_move = sm['id']
                #     vals = {
                #             'picking_id' : picking_ids,
                #             'move_id':      ids_stock_move,
                #             'company_id': sm['company_id'][0],
                #             'product_id': sm['product_id'][0],
                #             'product_uom_id': sm['product_uom'][0],
                #             'product_qty': sm['product_qty'],
                #             'product_uom_qty': sm['product_uom_qty'],
                #             'qty_done': qty_done,
                #             'location_id': sm['location_id'][0],
                #             'location_dest_id': sm['location_dest_id'][0],
                #             'reference': sm['reference'],
                #             'state': "done",
                #             'date' : now
                #             }
                #     print("create line 3")
                #     print(vals)
                #     m = models.execute_kw(db, uid, password, 'stock.move.line', 'create', [vals])
                #     print(m)
                    # models.execute_kw(db, uid, password, 'stock.move.line', 'create', [
                    #             {
                    #             'picking_id' : picking_ids,
                    #             'move_id':      ids_stock_move,
                    #             'company_id': sm['company_id'][0],
                    #             'product_id': sm['product_id'][0],
                    #             'product_uom_id': sm['product_uom'][0],
                    #             'product_qty': sm['product_qty'],
                    #             'product_uom_qty': sm['product_uom_qty'],
                    #             'qty_done': qty_done,
                    #             'location_id': sm['location_id'][0],
                    #             'location_dest_id': sm['location_dest_id'][0],
                    #             'reference': sm['reference'],
                    #             'state': "done",
                    #             'date' : now
                    #             }
                    #             ])
                    # print("line 2")
           

        cek_product_dest = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',product_id],['company_id','=',company_ids],['location_id','=',destination_ids]]], {'fields': ['id','quantity']})
        if cek_product_dest:
            stock_quant_ids = cek_product_dest[0]['id']
            quantity_stock = cek_product_dest[0]['quantity'] + qty_done
            models.execute_kw(db, uid, password, 'stock.quant', 'write', [[stock_quant_ids], {'quantity': quantity_stock}])
        else :
            models.execute_kw(db, uid, password, 'stock.quant', 'create', [
                                {
                                'product_id': product_id,
                                'company_id' : company_ids,
                                'location_id' : destination_ids,
                                'in_date'    : now,
                                'quantity'   : qty_done,
                                }
                                ])
        cek_product_lock = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',product_id],['company_id','=',company_ids],['location_id','=',location_ids]]], {'fields': ['id','quantity']})
        if cek_product_lock:
            stock_quant_lock_ids = cek_product_lock[0]['id']
            quantity_stock_lock = cek_product_lock[0]['quantity'] - qty_done
            models.execute_kw(db, uid, password, 'stock.quant', 'write', [[stock_quant_lock_ids], {'quantity': quantity_stock_lock}])
        else:
            models.execute_kw(db, uid, password, 'stock.quant', 'create', [
                        {
                        'product_id': product_id,
                        'company_id' : company_ids,
                        'location_id' : location_ids,
                        'in_date'    : now,
                        'quantity'   : qty_done-(qty_done*2),
                        }
                        ])  
        models.execute_kw(db, uid, password, 'stock.move', 'write', [[moveids], {'state': "done"}]) 
        models.execute_kw(db, uid, password, 'stock.picking', 'write', [[picking_ids], {'state': "done",'date_done': now}])
        
        return True        
    
    def validate_return(self, response, request, serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        qty_done = request.data['qty_done'] 
        date_now = datetime.now()
        destination_ids = request.data['LocationDestinationId']
        company_ids = request.data['CompanyId']
        now = date_now.strftime('%Y-%m-%d %H:%M:%S')
        for x in response:
            pickingid = x['id']
            product = request.data['product']
            stock_picking_obj  = models.execute_kw(db, uid, password, 'stock.picking', 'search_read', [[['id','=',pickingid],['state','=','assigned']]], {'fields': ['location_id','location_dest_id','picking_type_id','partner_id','company_id']})
            for x in stock_picking_obj:
                create_stock_picking = models.execute_kw(db, uid, password, 'stock.picking', 'create', [
                                    {
                                        "move_type":"direct",
                                        "state":"done",
                                        "scheduled_date": now,
                                        "date" :now,
                                        "date_done" : now,
                                        "location_id": x["location_id"][0],
                                        # "location_dest_id": x["location_dest_id"][0],
                                        "picking_type_id": x["picking_type_id"][0],
                                        "partner_id": x["partner_id"][0],
                                        "company_id": x["company_id"][0]
                                    }
                                    ])
                

                # stock_move  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['picking_id','=',picking_ids]]], {'fields': ['product_id','product_qty','id','product_uom_qty','qty_done','state']})
                for pd in product:
                    idprod = pd['productId']
                    qty_done = pd['qty_done']
                    vals_move = {
                            # "name"      : "sss",
                            "picking_id" : create_stock_picking['id'],
                            "product_id" : idprod,
                            "product_uom_qty": qty_done,
                            "product_qty": qty_done,
                            "company_id": x["company_id"][0],
                            "date" :now,
                            "location_id": x["location_id"][0],
                            "state": 'done'
                    }
                    create_stock_move = models.execute_kw(db, uid, password, 'stock.move', 'create', [vals_move])
                    vals_move_line = {
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
                    models.execute_kw(db, uid, password, 'stock.move_line', 'create', [vals_move_line])

                    cek_product_dest = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',idprod],['company_id','=',x["company_id"][0]],['location_id','=',x["location_id"][0]]]], {'fields': ['id','quantity']})
                    if cek_product_dest:
                        stock_quant_ids = cek_product_dest[0]['id']
                        quantity_stock = cek_product_dest[0]['quantity'] + qty_done
                        models.execute_kw(db, uid, password, 'stock.quant', 'write', [[stock_quant_ids], {'quantity': quantity_stock}])
                    else :
                        models.execute_kw(db, uid, password, 'stock.quant', 'create', [
                                            {
                                            'product_id': idprod,
                                            'company_id' : x["company_id"][0],
                                            'location_id' : x["location_id"][0],
                                            'in_date'    : now,
                                            'quantity'   : qty_done,
                                            }
                                            ])
                        
            return True             
                
                