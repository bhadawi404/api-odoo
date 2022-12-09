class Dict2Obj(object):
    def __init__(self, dictionary):
        """Constructor"""
        for key in dictionary:
            if str(key).lower() == 'rn':
                continue

            if type(dictionary[key]) is list:
                raw_list_data = dictionary[key]
                list_data = []
                for item in raw_list_data:
                    list_data.append(Dict2Obj(item))
                setattr(self, key, list_data)
            else:
                setattr(self, key, dictionary[key])