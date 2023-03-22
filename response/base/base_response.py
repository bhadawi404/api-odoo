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
        
        #untuk validasi location user yang login
        location_destination = serializer.data['location_name']
        #end 
        purchase = []
        for x in response:
            if not x['consume_id'] and not x['transfer_id']:
                if x['state'] == 'assigned':
                    origin = x['origin']
                    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
                    uid = common.authenticate(db, username, password, {})
                    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                    purchase_data  = models.execute_kw(db, uid, password, 'purchase.order', 'search_read', [[['purchase_number','=',origin]]], {'fields': []})
                    if purchase_data:
                        for data in purchase_data:
                            purchase_ids = data['id']
                            name = data['name']
                            purchase_number = data['purchase_number']
                            state = data['state']
                            date_order = data['date_order']
                            date_plan = data['date_planned']
                            vendor_name = data['partner_id'][1]
                            po_id = data['id']
                            picking_ids = x['id']
                            move_data = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',picking_ids]]], {'fields': ['id','purchase_line_id']})
                            move_line_list = []
                            total_qty_request = []
                            for move in move_data:
                                move_ids = move['id']
                                purchase_line = move['purchase_line_id'][0]
                                order_line = models.execute_kw(db, uid, password, 'purchase.order.line', 'search_read', [[['id','=',purchase_line]]], {'fields': ['qty_received','product_qty','brand']})
                                qty_received = order_line[0]['qty_received']
                                brand = order_line[0]['brand']
                                product_qty_request = order_line[0]['product_qty']
                                move_line_data = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',move['id']]]], {'fields': ['product_id','qty_done','product_qty','picking_id','product_uom_id']})
                                total_qty_request.append(product_qty_request)
                                for move_line in move_line_data:
                                    move_line_ids = move_line['id']
                                    product_ids = move_line['product_id'][0]
                                    product_qty = move_line['product_qty']
                                    product_name = move_line['product_id'][1]
                                    product_uom = move_line['product_uom_id'][1]
                                    qty_done = move_line['qty_done']
                                    barcode_obj  = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['id','=',product_ids]]], {'fields': ['barcode']})
                                    barcode = barcode_obj[0]['barcode']
                                    move_line_list.append({
                                        
                                        "orderLineId": purchase_line,
                                        "moveId": move_ids,
                                        "moveLineId": move_line_ids,
                                        "productId": product_ids,
                                        "productBarcode": barcode,
                                        "productName": product_name,
                                        "productBrand": brand,
                                        "productUom": product_uom,
                                        "productQtyRequestPO": product_qty_request,
                                        "productQtyReceived": qty_received,
                                        "productQtyDemand": product_qty,
                                        "productQtyDone": qty_done,
                                        
                                    })   
                        purchase.append({
                            'purchaseOrderVendor': vendor_name,
                            'purchaseOrderId': purchase_ids,
                            'purchaseOrderName': purchase_number,
                            'purhcaseOrderState':state,
                            'purchaseOrderDateOrder': date_order,
                            'purchaseOrderReceiptDate': date_plan,
                            'purchaseOrderLine': move_line_list,
                            'purchaseOrderLocationSourceId': x['location_id'][0],
                            'purchaseOrderLocationDestinationId': x['location_dest_id'][0],
                            'purchaseOrderCompanyId': x['company_id'][0],
                            "purchaseOrderTotalQtyRequest": sum(total_qty_request),
                            "pickingId": picking_ids,
                        })
        return purchase
        
    def internal_transfer_in(self, response,serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        internal = []
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        # print(response)
        for x in response:
            if x['transfer_id']:
                transfer_id = x['transfer_id'][0]
                cek_state_transfer = models.execute_kw(db, uid, password, 'amtiss.part.transfer', 'search_read', [[['id','=',transfer_id]]], {'fields': ['state','material_req','description']})
                if cek_state_transfer[0]['state'] in ('transfered','partially_received'):
                    material_req = ''
                    if cek_state_transfer[0]['material_req']!=False:
                        material_req = cek_state_transfer[0]['material_req'][1]
                    
                    description = ''
                    if cek_state_transfer[0]['description']!=False:
                        description = cek_state_transfer[0]['description']
                    id =x['id']
                    type_id = x['picking_type_id'][0]
                    cek_inter = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['sequence_code','=','INT']]], {'fields': ['name']})
                    if cek_inter and x['state']=='assigned':
                        stock_move  = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',id]]], {'fields': ['product_id','product_qty','id','product_uom']})
                        linesIT=[]
                        for data in stock_move:
                            move_ids = data['id']
                            move_line_ids = None
                            product_ids = data['product_id'][0]
                            product_qty = data['product_qty']
                            product_name = data['product_id'][1]
                            product_uom = data['product_uom'][1]
                            received  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',data['id']]]], {'fields': ['product_id','qty_done','product_qty']})
                            qty_done = 0
                            for rc in received:
                                qty_done = rc['qty_done']
                                move_line_ids = rc['id']
                            barcode_obj  = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['id','=',product_ids]]], {'fields': ['barcode']})
                            barcode = barcode_obj[0]['barcode']
                            linesIT.append(
                                {
                                    "moveId": move_ids,
                                    "moveLineId": move_line_ids,
                                    "productId": product_ids,
                                    "productBarcode": barcode,
                                    "productName": product_name,
                                    "productUom": product_uom,
                                    "productQtyReceived": product_qty,
                                    "productQtyDemand": product_qty,
                                    "productQtyDone": qty_done,
                                })
                        internal.append({
                            'TransferId': x['transfer_id'][0],
                            'PickingId' : x['id'],
                            'NoPickingType': x['name'],
                            'SourceLocation': x['location_id'][1],
                            'DestinationLocation':x['location_dest_id'][1],
                            'ScheduleDate': x['scheduled_date'],
                            # 'MRID': x['mr_id'],
                            # 'AssetId': x['asset_id'],
                            'MRID': material_req,
                            'Description': description,
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
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        for x in response:
            if x['transfer_id']:
                transfer_id = x['transfer_id'][0]
                cek_state_transfer = models.execute_kw(db, uid, password, 'amtiss.part.transfer', 'search_read', [[['id','=',transfer_id]]], {'fields': ['state','material_req','description']})
                if cek_state_transfer[0]['state'] in ('approved','partially_transfered'):
                    
                    material_req = ''
                    if cek_state_transfer[0]['material_req']!=False:
                        material_req = cek_state_transfer[0]['material_req'][1]
                    
                    description = ''
                    if cek_state_transfer[0]['description']!=False:
                        description = cek_state_transfer[0]['description']

                    id =x['id']
                    type_id = x['picking_type_id'][0]
                    cek_inter = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['sequence_code','=','INT']]], {'fields': ['name']})
                    if cek_inter and x['state']=='assigned':
                        stock_move  = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',id]]], {'fields': ['product_id','product_qty','id','product_uom']})
                        linesIT=[]
                        for data in stock_move:
                            move_ids = data['id']
                            move_line_ids = None
                            product_ids = data['product_id'][0]
                            product_qty = data['product_qty']
                            product_name = data['product_id'][1]
                            product_uom = data['product_uom'][1]
                            received  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',data['id']]]], {'fields': ['product_id','qty_done','product_qty']})
                            qty_done = 0
                            print(stock_move)
                            for rc in received:
                                qty_done = rc['qty_done']
                                move_line_ids = rc['id']
                            barcode_obj  = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['id','=',product_ids]]], {'fields': ['barcode']})
                            barcode = barcode_obj[0]['barcode']
                            linesIT.append(
                                {
                                    "moveId": move_ids,
                                    "moveLineId": move_line_ids,
                                    "productId": product_ids,
                                    "productBarcode": barcode,
                                    "productName": product_name,
                                    "productUom": product_uom,
                                    "productQtyReceived": product_qty,
                                    "productQtyDemand": product_qty,
                                    "productQtyDone": qty_done,
                                })
                        internal.append({
                            'TransferId': x['transfer_id'][0],
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
                            'MRID': material_req,
                            'Description': description,
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
            if x['consume_id']:
                if x['state'] == 'assigned':
                    id =x['id']
                    type_id = x['picking_type_id'][0]
                    consume_ids = x['consume_id'][0]
                    material_request_id = False
                    asset_ids = False
                    mr_ids = x['amtiss_material_request_id']
                    asset = x['asset_id']
                    if mr_ids:
                        material_request_id = mr_ids[1]
                    if asset:
                        asset_ids = asset[1]
                    
                    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
                    uid = common.authenticate(db, username, password, {})
                    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                    consume_cek = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['name','=','Consume']]], {'fields': ['name']})
                    
                    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
                    uid = common.authenticate(db, username, password, {})
                    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                    consume_data = models.execute_kw(db, uid, password, 'amtiss.consume', 'search_read', [[['id','=',consume_ids]]], {'fields': ['report_date','consume_number']})
                    # if len(consume_cek) > 0 & x['state']=='assigned':
                    report_date = consume_data[0]['report_date']
                    consume_name = consume_data[0]['consume_number']
                    if len(consume_cek) > 0:
                    
                        stock_move  = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',id]]], {'fields': ['product_id','product_qty','id','product_uom','consume_line_id']})
                        linesConsume=[]
                        print("bisa")
                        for data in stock_move:
                            move_ids = data['id']
                            move_line_ids = data['id']
                            product_ids = data['product_id'][0]
                            product_qty = data['product_qty']
                            product_name = data['product_id'][1]
                            product_uom = data['product_uom'][1]
                            consume_line = data['consume_line_id'][0]
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
                                    "consumeLineId": consume_line,
                                    "productId": product_ids,
                                    "productBarcode": barcode,
                                    "productUom": product_uom,
                                    "productName": product_name,
                                    "productQtyReceived": qty_received,
                                    "productQtyDemand": product_qty,
                                    "productQtyDone": qty_done,
                                })
                        consume.append({
                            'consumeNumber': consume_name,
                            'reportDate': report_date,
                            'pickingId': x['id'],
                            'SourceLocation': x['location_id'][1],
                            'DestinationLocation':x['location_dest_id'][1],
                            'ScheduleDate': x['scheduled_date'],
                            'LocationSourceId': x['location_id'][0],
                            'LocationDestinationId': x['location_dest_id'][0],
                            'CompanyId': x['company_id'][0],
                            'MRID': material_request_id or '',
                            'AssetId': asset_ids or '',
                            'ConsumeLine': linesConsume,
                        })
        return consume
    
    def return_product(self, response,serializer=False):
        url = serializer.data['url']
        db = serializer.data['db']
        username = serializer.data['email']
        password = serializer.data['key']
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        return_product = []
        # print(response)
        for x in response:
            if x['return_id']:
                return_id = x['return_id'][0]
                cek_state_return = models.execute_kw(db, uid, password, 'amtiss.return.requisition', 'search_read', [[['id','=',return_id]]], {'fields': ['consume_number','work_order','state']})
                
                if cek_state_return[0]['state'] == 'approved' :
                    consume_number = ''
                    if cek_state_return[0]['consume_number']!=False:
                        consume_number = cek_state_return[0]['consume_number'][1]
                    
                    work_order = ''
                    if cek_state_return[0]['work_order']!=False:
                        work_order = cek_state_return[0]['work_order']
                   
                    id =x['id']
                    type_id = x['picking_type_id'][0]
                    print(type_id)
                    cek_inter = models.execute_kw(db, uid, password, 'stock.picking.type', 'search_read', [[['id','=',type_id],['name','=','Returns']]], {'fields': ['name']})
                    print(cek_inter)
                    if len(cek_inter) > 0 :
                        stock_move  = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',id]]], {'fields': ['product_id','product_qty','id','product_uom']})
                        linesReturn=[]
                        for data in stock_move:
                            move_ids = data['id']
                            move_line_ids = None
                            product_ids = data['product_id'][0]
                            product_qty = data['product_qty']
                            product_name = data['product_id'][1]
                            product_uom = data['product_uom'][1]
                            received  = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',data['id']]]], {'fields': ['product_id','qty_done','product_qty']})
                            qty_done = 0
                            for rc in received:
                                qty_done = rc['qty_done']
                                move_line_ids = rc['id']
                            barcode_obj  = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['id','=',product_ids]]], {'fields': ['barcode']})
                            barcode = barcode_obj[0]['barcode']
                            linesReturn.append(
                                {
                                    "moveId": move_ids,
                                    "moveLineId": move_line_ids,
                                    "productId": product_ids,
                                    "productBarcode": barcode,
                                    "productName": product_name,
                                    "productUom": product_uom,
                                    "productQtyReceived": product_qty,
                                    "productQtyDemand": product_qty,
                                    "productQtyDone": qty_done,
                                })
                        return_product.append({
                            'ReturnId': x['return_id'][0],
                            'NoPickingType': x['name'],
                            'SourceLocation': x['location_id'][1],
                            'DestinationLocation':x['location_dest_id'][1],
                            'ScheduleDate': x['scheduled_date'],
                            'LocationSourceId': x['location_id'][0],
                            'LocationDestinationId': x['location_dest_id'][0],
                            'CompanyId': x['company_id'][0],
                            'ConsumeNumber': consume_number,
                            'WorkOrder': work_order,
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
        
        product = request.data['purchaseOrderLine']
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
                "qty_done": qty_done,
                "state": 'done'
            }
            #update Product uom qty 0, qty_done(request), state done
            models.execute_kw(db, uid, password, 'stock.move.line', 'write', [[move_line_ids], vals_stock_move_line])
            #update stock move state done
            # models.execute_kw(db, uid, password, 'stock.move', 'write', [[move_ids], {'state': "done"}])

            cek_product = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',product_id]]], {'fields': ['id']})
            
            if cek_product:
                cek_product_location = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',product_id],['company_id','=',company_ids],['location_id','=',destination_ids]]], {'fields': ['id','quantity']})
                cek_product_vendor = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',product_id],['location_id','=',location_ids]]], {'fields': ['id','quantity']})
                stock_quant_vendor_ids = cek_product_vendor[0]['id']
                quantity_stock_vendor = cek_product_vendor[0]['quantity'] - qty_done
                #issue disini
                # stock_quant_ids = cek_product_location[0]['id']
                #end issue
                # quantity_stock = cek_product_location[0]['quantity'] + qty_done
                if cek_product_location:
                    stock_quant_ids = cek_product_location[0]['id']
                    quantity_stock = cek_product_location[0]['quantity'] + qty_done
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
                    
                    for x in picking_old:
                        # print(x['amtiss_material_request_id'][0])
                        picking_group = x['picking_group']
                        message_main_attachment_id = x['message_main_attachment_id']
                        origin = x['origin']
                        backorder_id = picking_ids
                        move_type = x['move_type']
                        group_id = x['group_id'][0]
                        priority = x['priority']
                        scheduled_date = x['scheduled_date']
                        date_deadline = x['date_deadline']
                        has_deadline_issue = x['has_deadline_issue']
                        location_id = x['location_id'][0]
                        location_dest_id = x['location_dest_id'][0]
                        picking_type_id = x['picking_type_id'][0]
                        partner_id = x['partner_id'][0]
                        company_id = x['company_id'][0]
                        # mr_id = x['mr_id'][0]
                        # asset_id = x['asset_id'][0]
                        # assignment_id = x['assignment_id'][0]
                        # amtiss_material_request_id = x['amtiss_material_request_id'][0]
                        # batch_id = x['batch_id'][0]
                        picking_group = picking_ids
                        note = x['note']
                        
                        if x['picking_group']:
                            create_picking = models.execute_kw(db, uid, password, 'stock.picking', 'create', [
                                        {
                                        'message_main_attachment_id': message_main_attachment_id,
                                        'origin': origin,
                                        'note': note,
                                        'backorder_id' : picking_ids,
                                        'move_type': move_type,
                                        'state': 'assigned',
                                        'group_id': group_id,
                                        'priority': priority,
                                        'scheduled_date': scheduled_date,
                                        'date_deadline': date_deadline,
                                        'date': now,
                                        'has_deadline_issue': has_deadline_issue,
                                        'location_id': location_id,
                                        'location_dest_id': location_dest_id,
                                        'picking_type_id': picking_type_id,
                                        'partner_id': partner_id,
                                        'company_id': company_id,
                                        # 'mr_id': mr_id,
                                        # 'asset_id': asset_id,
                                        # 'assignment_id': assignment_id,
                                        # 'amtiss_material_request_id': amtiss_material_request_id,
                                        # 'batch_id': batch_id,
                                        'picking_group': x['picking_group'][0],
                                        
                                        }
                                        ])
                        else:
                            vals_p = {
                                        'message_main_attachment_id': x['message_main_attachment_id'],
                                        'origin': origin,
                                        'note': note,
                                        'backorder_id' : picking_ids,
                                        'move_type': move_type,
                                        'state': 'assigned',
                                        'group_id': group_id,
                                        'priority': priority,
                                        'scheduled_date': scheduled_date,
                                        'date_deadline': date_deadline,
                                        'date': now,
                                        'has_deadline_issue': has_deadline_issue,
                                        'location_id': location_id,
                                        'location_dest_id': location_dest_id,
                                        'picking_type_id': picking_type_id,
                                        'partner_id': partner_id,
                                        'company_id': company_id,
                                        # 'mr_id': mr_id,
                                        # 'asset_id': asset_id,
                                        # 'assignment_id': assignment_id,
                                        # 'amtiss_material_request_id': amtiss_material_request_id,
                                        # 'batch_id': batch_id,
                                        'picking_group': picking_ids,
                                        }
                            create_picking = models.execute_kw(db, uid, password, 'stock.picking', 'create', [vals_p])
                    
                    picking_new_id =  create_picking

                    #create stock move
                    move_old = models.execute_kw(db, uid, password, 'stock.move', 'read', [move_ids], {'fields': ['product_qty','name','product_id','product_qty','product_uom_qty','product_uom','location_id','location_dest_id','partner_id','picking_id','price_unit','state','origin','group_id','picking_type_id','warehouse_id','to_refund','reservation_date','next_serial_count','is_inventory','description_picking','date_deadline']})
                    for mv in move_old:
                        name = mv['name']
                        product_id = mv['product_id'][0]
                        product_uom_qty = qty_done
                        # product_qty = mv['product_qty'] - qty_done
                        product_uom = mv['product_uom'][0]
                        location_id = mv['location_id'][0]
                        location_dest_id = mv['location_dest_id'][0]
                        if mv['partner_id']:
                            partner_id = mv['partner_id'][0]
                        else:
                            partner_id = False
                        picking_id = picking_new_id
                        price_unit = mv['price_unit']
                        origin = mv['origin']
                        group_id = mv['group_id'][0]
                        picking_type_id = mv['picking_type_id'][0]
                        warehouse_id = mv['warehouse_id'][0]
                        purchase_order_line = order_line_ids
                        to_refund = mv['to_refund']
                        reservation_date = mv['reservation_date']
                        next_serial_count = mv['next_serial_count']
                        is_inventory = mv['is_inventory']
                        description_picking = mv['description_picking']
                        date_deadline = mv['date_deadline']
                        vals = {
                                'name':name,
                                'product_id':product_id,
                                'product_uom_qty': product_uom_qty,
                                # 'product_qty': product_qty,
                                'product_uom': product_uom,
                                'location_id': location_id,
                                'location_dest_id': location_dest_id,
                                'partner_id': partner_id,
                                'picking_id': picking_id,
                                'state' : 'assigned',
                                'price_unit': price_unit,
                                'origin': origin,
                                'group_id': group_id,
                                'picking_type_id': picking_type_id,
                                'warehouse_id': warehouse_id,
                                'purchase_line_id': purchase_order_line,
                                'to_refund':to_refund,
                                'reservation_date':reservation_date,
                                'next_serial_count': next_serial_count,
                                'is_inventory': is_inventory,
                                'description_picking': description_picking
                        }
                        move_id_new = models.execute_kw(db, uid, password, 'stock.move', 'create', [vals])
                        vals_line = {
                                'picking_id': picking_id,
                                'move_id':move_id_new,
                                'company_id': company_ids,
                                'product_id':product_id,
                                'product_uom_id': product_uom,
                                'product_uom_qty': product_uom_qty,
                                # 'product_qty': product_qty,
                                'qty_done': 0,
                                'location_id': location_id,
                                'location_dest_id': location_dest_id,
                                'state' : 'assigned',
                        }
                        models.execute_kw(db, uid, password, 'stock.move.line', 'create', [vals_line])
                        
                else:
                    move_old = models.execute_kw(db, uid, password, 'stock.move', 'read', [move_ids], {'fields': ['product_qty','name','product_id','product_qty','product_uom_qty','product_uom','location_id','location_dest_id','partner_id','picking_id','price_unit','state','origin','group_id','picking_type_id','warehouse_id','to_refund','reservation_date','next_serial_count','is_inventory','description_picking','date_deadline']})
                    for mv in move_old:
                        name = mv['name']
                        product_id = mv['product_id'][0]
                        product_uom_qty = mv['product_uom_qty'] - qty_done
                        # product_qty = mv['product_qty'] - qty_done
                        product_uom = mv['product_uom'][0]
                        location_id = mv['location_id'][0]
                        location_dest_id = mv['location_dest_id'][0]
                        if mv['partner_id']:
                            partner_id = mv['partner_id'][0]
                        else:
                            partner_id = False
                        picking_id = picking_new_id
                        price_unit = mv['price_unit']
                        origin = mv['origin']
                        group_id = mv['group_id'][0]
                        picking_type_id = mv['picking_type_id'][0]
                        warehouse_id = mv['warehouse_id'][0]
                        purchase_order_line = order_line_ids
                        to_refund = mv['to_refund']
                        reservation_date = mv['reservation_date']
                        next_serial_count = mv['next_serial_count']
                        is_inventory = mv['is_inventory']
                        description_picking = mv['description_picking']
                        date_deadline = mv['date_deadline']
                        vals = {
                                'name':name,
                                'product_id':product_id,
                                'product_uom_qty': product_uom_qty,
                                # 'product_qty': product_qty,
                                'product_uom': product_uom,
                                'location_id': location_id,
                                'location_dest_id': location_dest_id,
                                'partner_id': partner_id,
                                'picking_id': picking_id,
                                'state' : 'assigned',
                                'price_unit': price_unit,
                                'origin': origin,
                                'group_id': group_id,
                                'picking_type_id': picking_type_id,
                                'warehouse_id': warehouse_id,
                                'purchase_line_id': purchase_order_line,
                                'to_refund':to_refund,
                                'reservation_date':reservation_date,
                                'next_serial_count': next_serial_count,
                                'is_inventory': is_inventory,
                                'description_picking': description_picking
                        }
                        move_id_new = models.execute_kw(db, uid, password, 'stock.move', 'create', [vals])
                        # create stock move line
                        vals_line = {
                                'picking_id': picking_id,
                                'move_id':move_id_new,
                                'company_id': company_ids,
                                'product_id':product_id,
                                'product_uom_id': product_uom,
                                'product_uom_qty': product_uom_qty,
                                # 'product_qty': product_qty,
                                'qty_done': 0,
                                'location_id': location_id,
                                'location_dest_id': location_dest_id,
                                'state' : 'assigned',
                        } 
                        models.execute_kw(db, uid, password, 'stock.move.line', 'create', [vals_line])

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
        picking_ids = request.data['PickingId']
        location_ids = request.data['LocationSourceId']
        destination_ids = request.data['LocationDestinationId']
        company_ids = request.data['CompanyId']
        TransferId = request.data['TransferId']
        for pd in product:
            moveids = pd['moveId']
            movelineids = pd['moveLineId']
            product_id = pd['productId']
            qty_done = pd['productQtyDone']
            product_qty = pd['productQtyReceived']

            print("MASUK DONG 1")
            vals_stock_move_line = {
                "product_uom_qty":0,
                "qty_done": qty_done,
                "state": 'done'
            }
           
            print("MASUK DONG 2")
            print(movelineids)
            models.execute_kw(db, uid, password, 'stock.move.line', 'write', [[movelineids], vals_stock_move_line])
            print("MASUK DONG 3")
            # print(moveids)
            # models.execute_kw(db, uid, password, 'stock.move', 'write', [[moveids], {'state': "done"}]) 
            print("MASUK DONG 4")

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
           
            
            cek_product_lock = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',product_id],['company_id','=',company_ids],['location_id','=',location_ids]]], {'fields': ['id','quantity','reserved_quantity']})
            if cek_product_lock:
                stock_quant_lock_ids = cek_product_lock[0]['id']
                quantity_stock_lock = cek_product_lock[0]['quantity'] - qty_done
                models.execute_kw(db, uid, password, 'stock.quant', 'write', [[stock_quant_lock_ids], {'quantity': quantity_stock_lock,'reserved_quantity': cek_product_lock[0]['reserved_quantity']-qty_done}])
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
           
        models.execute_kw(db, uid, password, 'stock.picking', 'write', [[picking_ids], {'state': "done",'date_done': now}])
        print("MASUK DONG 5")
        models.execute_kw(db, uid, password, 'amtiss.part.transfer', 'write', [[TransferId], {'state': "transfered"}]) 
        print("MASUK DONG ")
        return True
    
    def validate_internal_transfer_in(self, request, serializer=False):
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
        picking_new_id = None
        for pd in product:
            moveids = pd['moveId']
            movelineids = pd['moveLineId']
            product_id = pd['productId']
            qty_done = pd['productQtyDone']
            product_qty = pd['productQtyReceived']

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

            vals_stock_move_line = {
                "product_uom_qty":0,
                "qty_done": qty_done,
                "state": 'done'
            }
            
            
            models.execute_kw(db, uid, password, 'stock.move.line', 'write', [[movelineids], vals_stock_move_line])

            models.execute_kw(db, uid, password, 'stock.move', 'write', [[moveids], {'state': "done"}]) 
           
            # print(qty_done)
            # print(product_qty)
            # # create backorder
            # if qty_done < product_qty:
                
            #     if not picking_new_id:
            #         #create stock Picking
            #         picking_old = models.execute_kw(db, uid, password, 'stock.picking', 'search_read', [[['id','=',picking_ids]]], 
            #         {'fields': 
            #         ['message_main_attachment_id','origin','note','move_type','group_id','priority',
            #         'scheduled_date','date_deadline','has_deadline_issue','location_id',
            #         'location_dest_id','picking_type_id','partner_id','company_id','mr_id',
            #         'asset_id','assignment_id','sale_id','amtiss_material_request_id',
            #         'batch_id','picking_group']}) 
            #         for x in picking_old:
            #             # print(x['amtiss_material_request_id'][0])
            #             picking_group = x['picking_group']
            #             message_main_attachment_id = x['message_main_attachment_id']
            #             origin = x['origin']
            #             backorder_id = picking_ids
            #             move_type = x['move_type']
                        
            #             if x['group_id']:
            #                 group_id = x['group_id'][0]
            #             else:
            #                 group_id = x['group_id']
            #             priority = x['priority']
                       
            #             scheduled_date = x['scheduled_date']
            #             date_deadline = x['date_deadline']
            #             has_deadline_issue = x['has_deadline_issue']
            #             location_id = x['location_id'][0]
            #             location_dest_id = x['location_dest_id'][0]
            #             picking_type_id = x['picking_type_id'][0]
                        
            #             if x['partner_id']:
            #                 partner_id = x['partner_id'][0]
            #             else:
            #                 partner_id = x['partner_id']
                            
            #             priority = x['priority']
            #             company_id = x['company_id'][0]
                        
            #             # mr_id = x['mr_id'][0]
            #             # asset_id = x['asset_id'][0]
            #             # assignment_id = x['assignment_id'][0]
            #             # amtiss_material_request_id = x['amtiss_material_request_id'][0]
            #             # batch_id = x['batch_id'][0]
            #             picking_group = picking_ids
            #             note = x['note']
                        
            #             if x['picking_group']:
            #                 create_picking = models.execute_kw(db, uid, password, 'stock.picking', 'create', [
            #                             {
            #                             'message_main_attachment_id': message_main_attachment_id,
            #                             'origin': origin,
            #                             'note': note,
            #                             'backorder_id' : picking_ids,
            #                             'move_type': move_type,
            #                             'state': 'assigned',
            #                             'group_id': group_id,
            #                             'priority': priority,
            #                             'scheduled_date': scheduled_date,
            #                             'date_deadline': date_deadline,
            #                             'date': now,
            #                             'has_deadline_issue': has_deadline_issue,
            #                             'location_id': location_id,
            #                             'location_dest_id': location_dest_id,
            #                             'picking_type_id': picking_type_id,
            #                             'partner_id': partner_id,
            #                             'company_id': company_id,
            #                             # 'mr_id': mr_id,
            #                             # 'asset_id': asset_id,
            #                             # 'assignment_id': assignment_id,
            #                             # 'amtiss_material_request_id': amtiss_material_request_id,
            #                             # 'batch_id': batch_id,
            #                             'picking_group': x['picking_group'][0],
                                        
            #                             }
            #                             ])
            #             else:
            #                 vals_p = {
            #                             'message_main_attachment_id': x['message_main_attachment_id'],
            #                             'origin': origin,
            #                             'note': note,
            #                             'backorder_id' : picking_ids,
            #                             'move_type': move_type,
            #                             'state': 'assigned',
            #                             'group_id': group_id,
            #                             'priority': priority,
            #                             'scheduled_date': scheduled_date,
            #                             'date_deadline': date_deadline,
            #                             'date': now,
            #                             'has_deadline_issue': has_deadline_issue,
            #                             'location_id': location_id,
            #                             'location_dest_id': location_dest_id,
            #                             'picking_type_id': picking_type_id,
            #                             'partner_id': partner_id,
            #                             'company_id': company_id,
            #                             # 'mr_id': mr_id,
            #                             # 'asset_id': asset_id,
            #                             # 'assignment_id': assignment_id,
            #                             # 'amtiss_material_request_id': amtiss_material_request_id,
            #                             # 'batch_id': batch_id,
            #                             'picking_group': picking_ids,
            #                             }
            #                 create_picking = models.execute_kw(db, uid, password, 'stock.picking', 'create', [vals_p])
                           
            #         picking_new_id =  create_picking
            #         #create stock move
            #         move_old = models.execute_kw(db, uid, password, 'stock.move', 'read', [moveids], {'fields': ['product_qty','name','product_id','product_qty','product_uom_qty','product_uom','location_id','location_dest_id','partner_id','picking_id','price_unit','state','origin','group_id','picking_type_id','warehouse_id','to_refund','reservation_date','next_serial_count','is_inventory','description_picking','date_deadline']})
                    
            #         for mv in move_old:
            #             name = mv['name']
            #             product_id = mv['product_id'][0]
            #             product_uom_qty = mv['product_uom_qty'] - qty_done
            #             # product_qty = mv['product_qty'] - qty_done
            #             product_uom = mv['product_uom'][0]
            #             location_id = mv['location_id'][0]
            #             location_dest_id = mv['location_dest_id'][0]
            #             if mv['partner_id']:
            #                 partner_id = mv['partner_id'][0]
            #             else:
            #                 partner_id = False
            #             picking_id = picking_new_id
            #             price_unit = mv['price_unit']
            #             origin = mv['origin']

            #             if mv['group_id']:
            #                 group_id = mv['group_id'][0]
            #             else:
            #                 group_id = mv['group_id']

            #             priority = x['priority']
            #             picking_type_id = mv['picking_type_id'][0]

            #             if mv['warehouse_id']:
            #                 warehouse_id = mv['warehouse_id'][0]
            #             else:
            #                 warehouse_id = mv['warehouse_id']
                        
            #             to_refund = mv['to_refund']
            #             reservation_date = mv['reservation_date']
            #             next_serial_count = mv['next_serial_count']
            #             is_inventory = mv['is_inventory']
            #             description_picking = mv['description_picking']
            #             date_deadline = mv['date_deadline']
            #             vals = {
            #                     'name':name,
            #                     'product_id':product_id,
            #                     'product_uom_qty': product_uom_qty,
            #                     # 'product_qty': product_qty,
            #                     'product_uom': product_uom,
            #                     'location_id': location_id,
            #                     'location_dest_id': location_dest_id,
            #                     'partner_id': partner_id,
            #                     'picking_id': picking_id,
            #                     'state' : 'assigned',
            #                     'price_unit': price_unit,
            #                     'origin': origin,
            #                     'group_id': group_id,
            #                     'picking_type_id': picking_type_id,
            #                     'warehouse_id': warehouse_id,
            #                     'to_refund':to_refund,
            #                     'reservation_date':reservation_date,
            #                     'next_serial_count': next_serial_count,
            #                     'is_inventory': is_inventory,
            #                     'description_picking': description_picking
            #             }
            #             move_id_new = models.execute_kw(db, uid, password, 'stock.move', 'create', [vals])
            #             vals_line = {
            #                     'picking_id': picking_id,
            #                     'move_id':move_id_new,
            #                     'company_id': company_ids,
            #                     'product_id':product_id,
            #                     'product_uom_id': product_uom,
            #                     'product_uom_qty': product_uom_qty,
            #                     # 'product_qty': product_qty,
            #                     'qty_done': 0,
            #                     'location_id': location_id,
            #                     'location_dest_id': location_dest_id,
            #                     'state' : 'assigned',
            #             }
            #             models.execute_kw(db, uid, password, 'stock.move.line', 'create', [vals_line])
                        
                # else:
                #     move_old = models.execute_kw(db, uid, password, 'stock.move', 'read', [moveids], {'fields': ['product_qty','name','product_id','product_qty','product_uom_qty','product_uom','location_id','location_dest_id','partner_id','picking_id','price_unit','state','origin','group_id','picking_type_id','warehouse_id','to_refund','reservation_date','next_serial_count','is_inventory','description_picking','date_deadline']})
                #     for mv in move_old:
                #         name = mv['name']
                #         product_id = mv['product_id'][0]
                #         product_uom_qty = mv['product_uom_qty'] - qty_done
                #         # product_qty = mv['product_qty'] - qty_done
                #         product_uom = mv['product_uom'][0]
                #         location_id = mv['location_id'][0]
                #         location_dest_id = mv['location_dest_id'][0]
                #         if mv['partner_id']:
                #             partner_id = mv['partner_id'][0]
                #         else:
                #             partner_id = False
                #         picking_id = picking_new_id
                #         price_unit = mv['price_unit']
                #         origin = mv['origin']

                #         if mv['group_id']:
                #             group_id = mv['group_id'][0]
                #         else:
                #             group_id = mv['group_id']

                #         picking_type_id = mv['picking_type_id'][0]

                #         if mv['warehouse_id']:
                #             warehouse_id = mv['warehouse_id'][0]
                #         else:
                #             warehouse_id = mv['warehouse_id']

                #         to_refund = mv['to_refund']
                #         reservation_date = mv['reservation_date']
                #         next_serial_count = mv['next_serial_count']
                #         is_inventory = mv['is_inventory']
                #         description_picking = mv['description_picking']
                #         date_deadline = mv['date_deadline']
                #         vals = {
                #                 'name':name,
                #                 'product_id':product_id,
                #                 'product_uom_qty': product_uom_qty,
                #                 # 'product_qty': product_qty,
                #                 'product_uom': product_uom,
                #                 'location_id': location_id,
                #                 'location_dest_id': location_dest_id,
                #                 'partner_id': partner_id,
                #                 'picking_id': picking_id,
                #                 'state' : 'assigned',
                #                 'price_unit': price_unit,
                #                 'origin': origin,
                #                 'group_id': group_id,
                #                 'picking_type_id': picking_type_id,
                #                 'warehouse_id': warehouse_id,
                #                 'to_refund':to_refund,
                #                 'reservation_date':reservation_date,
                #                 'next_serial_count': next_serial_count,
                #                 'is_inventory': is_inventory,
                #                 'description_picking': description_picking
                #         }
                #         move_id_new = models.execute_kw(db, uid, password, 'stock.move', 'create', [vals])
                #         # create stock move line
                #         vals_line = {
                #                 'picking_id': picking_id,
                #                 'move_id':move_id_new,
                #                 'company_id': company_ids,
                #                 'product_id':product_id,
                #                 'product_uom_id': product_uom,
                #                 'product_uom_qty': product_uom_qty,
                #                 # 'product_qty': product_qty,
                #                 'qty_done': 0,
                #                 'location_id': location_id,
                #                 'location_dest_id': location_dest_id,
                #                 'state' : 'assigned',
                #         } 
                #         models.execute_kw(db, uid, password, 'stock.move.line', 'create', [vals_line])

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
        date_now = datetime.now()
        
        now = date_now.strftime('%Y-%m-%d %H:%M:%S')
        product = request.data['product']
        picking_ids = request.data['PickingId']
        location_ids = request.data['LocationSourceId']
        destination_ids = request.data['LocationDestinationId']
        company_ids = request.data['CompanyId']
        ReturnId = request.data['ReturnId']
        for pd in product:
            moveids = pd['moveId']
            movelineids = pd['moveLineId']
            product_id = pd['productId']
            qty_done = pd['productQtyDone']
            product_qty = pd['productQtyReceived']

            print("MASUK DONG 1")
            vals_stock_move_line = {
                "product_uom_qty":0,
                "qty_done": qty_done,
                "state": 'done'
            }
           
            print("MASUK DONG 2")
            print(movelineids)
            models.execute_kw(db, uid, password, 'stock.move.line', 'write', [[movelineids], vals_stock_move_line])
            print("MASUK DONG 3")
            print(moveids)
            models.execute_kw(db, uid, password, 'stock.move', 'write', [[moveids], {'state': "done"}]) 
            print("MASUK DONG 4")

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
           
            
            cek_product_lock = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [[['product_id','=',product_id],['company_id','=',company_ids],['location_id','=',location_ids]]], {'fields': ['id','quantity','reserved_quantity']})
            if cek_product_lock:
                stock_quant_lock_ids = cek_product_lock[0]['id']
                quantity_stock_lock = cek_product_lock[0]['quantity'] - qty_done
                models.execute_kw(db, uid, password, 'stock.quant', 'write', [[stock_quant_lock_ids], {'quantity': quantity_stock_lock,'reserved_quantity': cek_product_lock[0]['reserved_quantity']-qty_done}])
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
           
        models.execute_kw(db, uid, password, 'stock.picking', 'write', [[picking_ids], {'state': "done",'date_done': now}])
        print("MASUK DONG 5")
        models.execute_kw(db, uid, password, 'amtiss.return.requisition', 'write', [[ReturnId], {'state': "done"}]) 
        print("MASUK DONG ")
        return True        
                
                