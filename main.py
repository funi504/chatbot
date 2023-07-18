
from flask import *
from chat import chatFunc

app = Flask(__name__)
 

@app.route('/')
def home():

    return render_template("chat.html")
 
@app.route('/success', methods = ['POST','GET'])
def success():
    try:
        if request.method == 'GET':
            data = request.args.get('msg')
            print(data)
            #call the function to generate response
            response = chatFunc(data)
            #return render_template('input.html', response = response , message= data )
            return str(response)
    except :

        return "sorry ,something went wrong..., my creator will fix it very soon"


# main driver function
if __name__ == '__main__':
 

    app.run(debug=True)