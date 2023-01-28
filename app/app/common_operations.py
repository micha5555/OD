def ids_to_ids_string(ids):
    idsString = "("
    for elem in ids:
        idsString = idsString + str(elem[0]) + ","
    if len(idsString) > 1:
        idsString = idsString[:len(idsString)-1]
    idsString = idsString + ")"