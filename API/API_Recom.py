
# coding: utf-8

# In[55]:


import os,json,MySQLdb,pandas as pd
from flask import Flask, request, redirect, url_for, flash,send_from_directory,render_template
from werkzeug.utils import secure_filename
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.utils import secure_filename

# In[54]:


app = Flask(__name__)


@app.route('/upload')
def upload_file():
    with open ('ui_recom.html')as f:
        return f.read()
    
    
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        f = request.files['file']
        f.save('user_uploaded_file.csv')
    return 'file uploaded successfully'

  
@app.route("/train", methods=['GET', 'POST'])
def train():
    global base_threshold,user_matrix,item_matrix,u2u,i2i
    ratings = pd.read_csv('user_uploaded_file.csv')
    ratings.columns = ["uId", "iId", "rating"]
    user_matrix = ratings.pivot(index='uId', columns='iId', values='rating')
    #user_matrix = user_matrix.apply(lambda v: v.apply(lambda x:x if x!=0.2 else 0) )
    suggested_items = pd.DataFrame(0,index=user_matrix.columns.tolist(),columns=['similarity'])
    base_threshold =0.5
    user_matrix = user_matrix.fillna(0)
    item_matrix = user_matrix.T 
    u2u = pd.DataFrame(cosine_similarity(user_matrix),index=user_matrix.index.tolist(),columns=user_matrix.index.tolist())
    i2i = pd.DataFrame(cosine_similarity(item_matrix),index=item_matrix.index.tolist(),columns=item_matrix.index.tolist())
    return "training successful"


# use this url to generate the results : http://localhost:5000/result?username=<user_id>
@app.route("/result")
def result():
    u_temp = int(request.args.get('username'))
    threshold = base_threshold**2
    rated_by_u_temp = item_matrix[u_temp][item_matrix[u_temp]!=0].index.tolist()
    result = user_matrix.T.mul(u2u[u_temp]).T
    suggested_items = result.max(axis=0)
    suggested_items = suggested_items.drop(labels=rated_by_u_temp)
    suggested_items = suggested_items[suggested_items>=threshold]
    suggested_items = suggested_items.to_json(orient='index')
    return suggested_items


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
