from webscrapper import upload_data_to_vectordb 

def upload_url_webscrapping(session , Project , jsonify , request):

    user_id = session.get("user_id")
    project = Project.query.filter_by(user_id=user_id).first()
    project_id = project.project_id

    if not user_id:
        return jsonify({"error":"unauthorized"}),401

    if not project_id:
        return jsonify({"error":"project does not exist"}),401

    if request.method == "POST":
        request_url = request.get_json()
        #print(request_msg)
        web_url = request_url['url'] 

        upload_data_to_vectordb(web_url , project_id)

        return jsonify({"message":"uploaded"})