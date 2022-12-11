import xmlrpc.client

# url = 'http://localhost:8015'
# db = 'v4'
# username = 'admin' #username odoo
# password = '4mti55'

url = 'http://localhost:8015'
db = 'demo-warehouse'
username = 'admin' #username odoo
password = 'admin'

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
        print(response)

        purchase = []
        for x in response:
            name = x['name']
            state = x['state']
            date_order = x['date_order']
            partner_ref = x['partner_ref']
            date_plan = x['date_planned']
            po_id = x['id']
            
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            lines_obj  = models.execute_kw(db, uid, password, 'purchase.order.line', 'search_read', [[['order_id','=',po_id]]], {'fields': ['product_id','product_qty','qty_received']})
            picking_ids = models.execute_kw(db, uid, password, 'stock.picking', 'search_read', [[['origin','=',name],['state','=','assigned']]], {'fields': ['name']})
            
            
            picking_list=[]
            for picking in picking_ids:
                picking_ids = picking['id']
                picking_name = picking['name']
                move_ids = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['picking_id','=',picking_ids]]], {'fields': ['name']})
                for move in move_ids:
                    move_id = move['id']
                    move_line_ids = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [[['move_id','=',move_id]]], {'fields': ['product_id','product_qty','qty_done']})
                    move_line_list = []
                    for move_line in move_line_ids:
                        move_product_id = move_line['product_id'][0]
                        move_product_name = move_line['product_id'][1]
                        qty_done = move_line['qty_done']
                        qty_demand = move_line['product_qty']
                        move_line_list.append({
                            'moveProductId': move_product_id,
                            'moveProductName': move_product_name,
                            'moveProductQtyDemand': qty_demand,
                            'moveProductQtyDone': qty_done
                        })
                    
                    picking_list.append(
                        {
                            "pickingId": picking_ids,
                            "pickingName": picking_name,
                            'pickingMove': move_line_list
                        })
            
            
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
                'purchaseOrderName': name,
                'purhcaseOrderState':state,
                'purchaseOrderDateOrder': date_order,
                'purchaseOrderReceiptDate': date_plan,
                'purchaseOrderLine': lines_po,
                'purchaseStockPicking': picking_list,
                
                
                
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