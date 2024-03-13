
def AI_reply_to_user(request , message_reply):
    
    if request.method == 'POST':

        request_msg = request.get_json()
        #print(request_msg)
        msg = request_msg['msg']
        project_id = request_msg['project_Id']
        print(msg) 
        print(project_id)
        #call the function to generate response
        #response = chatFunc(data, project_id)
        response = message_reply(msg , project_id)
        print(response)
        #return render_template('input.html', response = response , message= data )
        return {'response':response}