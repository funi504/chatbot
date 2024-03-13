import json

def reply_user(request,Project,Workflow,jsonify):

    if request.method == 'POST':
        
        try:
            data = request.get_json()
            project_id = data['projectId']
            reply_id = data['replyId']
            project = Project.query.filter_by(project_id = project_id).first()
            workflow = Workflow.query.filter_by(project_id= project_id).first()
            
            if not project:
                return jsonify({"error":"unauthorized, no project  found"}),401
            
            if not workflow : 
                return jsonify({
                    "nodes":[],
                    "edges":[]
                })
            
            replyNode = []
            json_nodes = json.loads(workflow.nodes)
            json_edges = json.loads(workflow.edges)

            for node in json_nodes :

                if node['id'] == reply_id:
                    connected_button = []
                    button_edges = []
                    parent_node = node

                    for node in json_nodes:
                        if node['type'] == 'buttonNode':
                            if node['parentNode'] == reply_id:
                                connected_button.append(node)
                                node_id = node['id']

                                for edge in json_edges:
                                    if edge['source'] == node_id:
                                        button_edges.append({
                                            'button_id' : node['id'],
                                            'edge_target': edge['target']
                                        })


                    replyNode.append({
                        'node': parent_node,
                        'connected_button': connected_button,
                        'button_edge_target': button_edges
                    })

            #print(replyNode)
            return jsonify({
                'data':replyNode
            })
            

        except Exception as e:
            print(e)
            return jsonify({"error":" something went wrong, try later"})