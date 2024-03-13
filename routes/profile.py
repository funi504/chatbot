

def get_current_user(session, User , request , jsonify):
    try:
        user_id = session.get("user_id")
        print(user_id)
    except:
        return jsonify({ "error": "account not found"}),401

    if request.method =="GET":
        try:
            user = User.query.filter_by(id=user_id).first()

            return jsonify({
            "id": user.id,
            "email": user.email,
            "domain" : user.domain
        })
        except:
            return jsonify({ "error": "account not found"}),401


    if request.method == "PUT":
        try:

            user = User.query.filter_by(id=user_id).first()

            email = request.json["email"]
            domain = request.json["domain"]

            user.email = email
            user.domain = domain
            user.confirmed = False

            db.session.commit()

            return jsonify({
                "new_email": user.email,
                "new_domain": user.domain
            })
        except:
            return jsonify({ "error": "account not found"}),401

    if request.method == "DELETE":
        try:

            user = User.query.filter_by(id=user_id).first()
            password = request.json["password"]

            if not bcrypt.check_password_hash(user.password, password):
                return jsonify({"error": "unauthorized"}), 401
                
            db.session.delete(user)
            db.session.commit()

            return jsonify({"message": "the account has been deleted"})
        except:
            return jsonify({"error":"account not found"}), 401
            