import xmlrpc.client

url = 'https://v4.amtiss.com'
db = 'v4'
username = 'admin' 
password = '4mti55'

# url = 'http://localhost:8015'
# db = 'demo-warehouse'
# username = 'admin' #username odoo
# password = 'admin'

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
    
    def stock_picking(self, response):
        purchase = []
        for x in response:
            origin = x['origin']
            
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            purchase_data  = models.execute_kw(db, uid, password, 'purchase.order', 'search_read', [[['name','=',origin]]], {'fields': []})
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