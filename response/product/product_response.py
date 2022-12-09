class ProductResponse(object):
    def detail(self, response):
        result = []
        for x in response:
            uom_id = x['uom_id']
            categ_id = x['categ_id']
            c =categ_id[1]
            u = uom_id[1]
            print(u)
            result.append({
                'productId': x['id'],
                'productName': x['name'],
                'productNumber': x['default_code'],
                'productBarcode': x['barcode'],
                'productType':x['detailed_type'],
                'productUom': u,
                'productCategory':c,
                'productCost':x['standard_price'],
                'productStatus':x['active'],   
            })
        return result