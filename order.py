def system(order):
    try:
        orderlist = order.split(ORDER)
        if orderlist[1] == 'ALL':
            target_list =
        else:
            target_list = json.loads('[{}]'.format(orderlist[1]))
    except Exception as e:
        print e
    return