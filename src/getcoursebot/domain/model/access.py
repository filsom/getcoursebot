class Group(object):
    ADMIN = 1
    FOOD = 2315673
    TRAINING = 3088338


class AccessGC:
    def __init__(self, groups: list[Group]):
        self.groups = groups

    def check_group(self, value: Group) -> bool:
        if not self.groups:
            return False
        
        for group in self.groups:
            if group == value or value == Group.ADMIN:
                return True
        return False
    
    def groups_empty(self) -> bool:
        if not self.groups:
            return True
        
        return False