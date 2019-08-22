# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 15:04:07 2019

@author: admin1
"""
from flask import Flask, render_template, request
import sqlite3 as sql
from datetime import datetime
import pandas as pd
from matplotlib import pyplot as plt
import io
import re
import base64

app = Flask(__name__)

def pie_chart():
    con = sql.connect('database_vib3.db')
    df = pd.read_sql_query('SELECT * FROM MOTORVIB ORDER BY DATETIME(date) DESC LIMIT 80',con)
    tags = ['220-PM-1A','220-PM-1B','220-PM-2A','220-PM-2B','220-PM-3A']
    series_list = []
    for tag in tags:
        df1 = df[df['tag']==tag].iloc[0]
        series_list.append(df1)
    df_series = pd.DataFrame(series_list)
    df2 = df_series
    for i in df2.index:
        if df2['NDE_V_VEL'][i]<6 and df2['NDE_H_VEL'][i]<6 and df2['NDE_H_ENV'][i]<5 and df2['NDE_H_ACC'][i]<5 and df2['DE_V_VEL'][i]<6 and df2['DE_H_VEL'][i]<6 and df2['DE_H_ENV'][i]<5 and df2['DE_H_ACC'][i]<5: 
            if df2['NDE_V_VEL'][i]<3.25 and df2['NDE_H_VEL'][i]<3.25 and df2['NDE_H_ENV'][i]<3 and df2['NDE_H_ACC'][i]<3 and df2['DE_V_VEL'][i]<3.25 and df2['DE_H_VEL'][i]<3.25 and df2['DE_H_ENV'][i]<3 and df2['DE_H_ACC'][i]<3:
                df2.at[i,'STATUS'] = 'normal'
            else :
                df2.at[i,'STATUS'] = 'alert high'
        else :
            df2.at[i,'STATUS'] = 'danger high'
        df3 = df2
    
    
    normal = len(df3[df3['STATUS']=='normal'])
    alert_high = len(df3[df3['STATUS']=='alert high'])
    danger_high = len(df3[df3['STATUS']=='danger high'])
    
    labels = ['Normal','Alert High','Danger High']
    sizes = [normal, alert_high, danger_high]
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99']
 
    
    fig1, ax1 = plt.subplots()
    patches, texts, autotexts = ax1.pie(sizes, colors = colors, labels=labels, autopct='%1.1f%%', startangle=90)
    for text in texts:
        text.set_color('grey')
    for autotext in autotexts:
        autotext.set_color('grey')
# Equal aspect ratio ensures that pie is drawn as a circle
    ax1.axis('equal')  
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='jpg')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)


@app.route('/')
def home():
    
    graph1_url = pie_chart();
 
    return render_template('home.html',
    graph1=graph1_url)

@app.route('/student')
def student():
   return render_template('student.html')

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
   if request.method == 'POST':
      try:
         tag = request.form['tag']
         nde_v_vel = request.form['nde_v_vel']
         nde_h_vel = request.form['nde_h_vel']
         nde_h_env = request.form['nde_h_env']
         nde_h_acc = request.form['nde_h_acc']
         de_v_vel  = request.form['de_v_vel']
         de_h_vel  = request.form['de_h_vel']
         de_h_env  = request.form['de_h_env']
         de_h_acc  = request.form['de_h_acc']
         rekom     = request.form['rekom']
         #date = datetime.now().strftime("%B %d, %Y %I:%M%p")
         date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
         
         with sql.connect("database_vib3.db") as con:
            #con.execute('CREATE TABLE motorvib (date TEXT, tag TEXT, NDE_V_VEL REAL, NDE_H_VEL REAL, NDE_H_ENV REAL, NDE_H_ACC REAL, DE_V_VEL REAL, DE_H_VEL REAL, DE_H_ENV REAL, DE_H_ACC REAL, REKOMENDASI TEXT)')
            cur = con.cursor()
            cur.execute("INSERT INTO motorvib (date,tag, NDE_V_VEL, NDE_H_VEL, NDE_H_ENV, NDE_H_ACC, DE_V_VEL, DE_H_VEL, DE_H_ENV, DE_H_ACC, REKOMENDASI) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(date,tag, nde_v_vel, nde_h_vel, nde_h_env, nde_h_acc, de_v_vel, de_h_vel, de_h_env, de_h_acc,rekom) )
            con.commit()
            msg = "Record successfully added"
      except:
         con.rollback()
         msg = "error in insert operation"
      
      finally:
         return render_template("result.html",msg = msg)
         con.close()

@app.route('/list')
def list():
   con = sql.connect("database_vib3.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from motorvib")
   
   rows = cur.fetchall();
   return render_template("list.html",rows = rows)


if __name__ == '__main__':
   app.run(debug = True)