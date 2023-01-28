def ids_to_ids_string(ids):
    idsString = "("
    for elem in ids:
        idsString = idsString + str(elem[0]) + ","
    if len(idsString) > 1:
        idsString = idsString[:len(idsString)-1]
    idsString = idsString + ")"

def check_if_owner(noteOwner, currentUser):
    if currentUser == None or (noteOwner != currentUser):
        return 0
    else:
        return 1