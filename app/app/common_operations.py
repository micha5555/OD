def check_if_owner(noteOwner, currentUser):
    if currentUser == None or (noteOwner != currentUser):
        return 0
    else:
        return 1
    
    