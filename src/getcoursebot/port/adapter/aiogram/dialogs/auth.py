from getcoursebot.domain.model.user import Role, NameRole


def authorize(user_roles: list[Role], scope: NameRole) -> bool:
    for role in user_roles:
        if role.name == scope:
            return True
        
    return False