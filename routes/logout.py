
def logout_user(session):
    session.pop("user_id")
    return "200"