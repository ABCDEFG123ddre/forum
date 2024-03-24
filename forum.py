# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 12:28:09 2021

@author: Andrea
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import time

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"),name="static")
class theme(BaseModel):
    themeName:str
    content:str
    
class response(BaseModel):
    title:str
    details:str
    themeid:int

def createTable():
    conn = sqlite3.connect('e:\\forum.db') 
    cursor = conn.cursor() 
    sql="""CREATE TABLE IF NOT EXISTS theme (
    themeName VARCHAR(100),
    content VARCHAR(300),
    time VARCHAR(50)
    )"""
    cursor.execute(sql)
    conn.commit()
    sql="""CREATE TABLE IF NOT EXISTS response (
      title VARCHAR(100),
      details VARCHAR(300),
      themeid INT,
      time VARCHAR(50)
     )"""
    cursor.execute(sql)
    conn.commit()
    conn.close()
    
def retrieveData():
    conn = sqlite3.connect('e:\\forum.db') 
    cursor = conn.cursor() 
    cursor.execute('select rowid,* from theme')
    result = cursor.fetchall(); 
    results=[]
    c=count()
    for j in range(len(result)):
        a=[]
        for k in range(4):
            a.append(result[j][k])
        results.append(a)
        
    for i in range(len(results)):
        x=0
        for k in range(len(c)):
            if c[k][0]==i+1:
                results[i].append(c[k][1])
                x=x+1
        if x==0:
            results[i].append(0)
    
    conn.commit()
    conn.close()
    return results

def retrievedetails(Id):
    conn = sqlite3.connect('e:\\forum.db') 
    cursor = conn.cursor() 
    cursor.execute('select rowid,* from response where themeid='+str(Id))
    result = cursor.fetchall(); 
    conn.commit()
    conn.close()
    return result

def count():
    conn = sqlite3.connect('e:\\forum.db') 
    cursor = conn.cursor() 
    cursor.execute(' select themeid,count(*) as num from response group by themeid')
    count=cursor.fetchall();
    conn.commit()
    conn.close()
    return count

def gettime():
    localtime = time.localtime()
    nowtime = time.strftime("%Y-%m-%d %I:%M:%S %p", localtime)
    return nowtime

@app.get("/homepage/")
async def root():
    createTable()
    getAll=retrieveData()
    return getAll

@app.get("/counting/")
async def counting():
    num=count()
    return num
    
@app.post("/insert/")
async def insertNewTheme(Theme:theme):
    themeName=Theme.themeName
    content=Theme.content
    conn = sqlite3.connect('e:\\forum.db') 
    cursor = conn.cursor()
    time=gettime()
    cursor.execute("insert into theme ('themeName','content','time') values (?,?,?)",(themeName,content,time))
    sql=" select rowid,* from theme order by rowid desc;"
    cursor.execute(sql)
    result = cursor.fetchone();
    conn.commit()
    conn.close()
    return result
    
@app.get("/",response_class=HTMLResponse)
async def theme(themeid:int): 
    conn = sqlite3.connect('e:\\forum.db') 
    cursor = conn.cursor()
    cursor.execute("select rowid,* from theme where rowid=?",(themeid,))
    themecontent=cursor.fetchone();
    allresponses=retrievedetails(themeid)
    conn.commit()
    conn.close()
    htmlstring=''
    htmlstring=htmlstring+""""<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <html>
    <head><title>"""+themecontent[1]+"""</title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <style>
        .res {background-color: #04AA6D; color: white;padding: 12px 20px;border: none;border-radius: 4px;cursor: pointer;}
        .res:hover { background-color: #45a049;}
        .home:hover { background-color: RoyalBlue;  }   
        .home {float:right; background-color: DodgerBlue;  border: none;  color: white;  padding: 12px 16px;  font-size: 16px;  cursor: pointer;}
        #add-res {width: 510px;border: 3px solid #f1f1f1;z-index: 9;}
		.addform {;max-width: 500px;padding: 10px;background-color: white;}
        input[type=text], textarea {width: 100%;padding: 12px;border: 1px solid #ccc;border-radius: 4px;box-sizing: border-box;margin-top: 6px;margin-bottom: 16px;resize: vertical;}
		input[type=button] {background-color: #04AA6D;color: white;padding: 12px 20px;border: none;border-radius: 4px;cursor: pointer;}
		input[type=button]:hover {background-color: #45a049;}
        .container {  border: 2px solid #dedede; background-color: #f1f1f1; border-radius: 5px; padding: 15px; margin: 10px 0;}
        .footer{margin: 5px; padding: 20px 10px;background-color: #e7f3fe;text-align:center;color:black; border-bottom: 15px solid #2196F3;}  
    </style>
    </head>
    <body>
    <div>
        <h1 style="color:blue; display:inline" >主題："""+themecontent[1]+"""</h1>
        <button type="button" class="home" onclick="back()"><i class="fa fa-home"></i> Home</button>
        <h3 style="border:3px solid #2196F3; padding:10px;"><strong style="font-size:130%">內文:</strong></br>"""+themecontent[2]+"""</h3>
        <button type="button" class="res" onclick="addRes()">回復</button>
    </div>
    <div id="add-res" style="display:none;">
		<table action="/insert-res" class="addform">
		<h2>新增回復</h2>
        <input type='checkbox' id="q" name="q" value="""+themecontent[2]+""">
		<label for="q">引文</label>
        <textarea id='quote' style='font-style: oblique;'>"""+themecontent[2]+"""</textarea>
        </br>
		<label for="subject">內容</label>
		<textarea id="rescontent" name="rescontent" placeholder="回復些東西吧..." style="height:200px"></textarea>
		<input type="button" onclick="insertRes()" value="確定新增" />
        <input style='float:right' type="button" onclick="cancel()" value="取消" />
		</table>
	</div>"""
    htmlstring=htmlstring+'<div id="res">'
    for i in range(len(allresponses)):
        htmlstring=htmlstring+'<div class="container">'
        if allresponses[i][1]=='yes':
            htmlstring=htmlstring+'<h5 style="font-style: oblique;">引文：'+themecontent[2]+'</h3>'
        htmlstring=htmlstring+'<p>回覆：'+allresponses[i][2]+'</p>'
        htmlstring=htmlstring+'<h5 style="text-align:right">回覆時間：'+allresponses[i][4]+'</h5>'
        htmlstring=htmlstring+'</div>'
        
    htmlstring=htmlstring+"""    
    </div>
    <div id="button">
        <button type="button" class="res" onclick="addRes()" style="float:right">回復</button></br></br>
    </div>
    <div class='footer' >
		已經到底囉！
	</div>
    <script>
        function addRes(){
               document.getElementById("add-res").style.display="block";
               document.getElementById("res").style.display="none";
               document.getElementById("button").style.display="none";
        }
        function insertRes(){
            var response=new Object();
            var gettitle=document.getElementById("q");
            if (gettitle.checked){
                response.title='yes';
            }
            else{
                response.title='no';
            }
            var getdetails=document.getElementById("rescontent").value;
            var getid="""+str(themeid)+"""
			response.details=getdetails;
            response.themeid=getid;
			var jsonobj=JSON.stringify(response);
			$.ajax({
				contentType: "application/json", 
				data:jsonobj,
				type: 'POST',
				url: "/insertResponse/",
				success: function(data){
					document.getElementById("add-res").style.display="none";
                    document.getElementById("res").style.display="block";
                    document.getElementById("button").style.display="block";
					document.getElementById("q").value="";
					document.getElementById("rescontent").value="";
                    location.reload()
                },
                error: function(data) {
					console.log(data);
					alert("傳送資料失敗");
				}
			});
        }
        function back(){
            location.replace("/static/forum.html")
        }
        function cancel(){
            document.getElementById("add-res").style.display="none";
            document.getElementById("res").style.display="block";
            document.getElementById("button").style.display="block";
        }
    
    </script>
    </body>
    </html>"""
    return htmlstring
    
@app.post("/insertResponse/")
async def theme(Response:response): 
    resName=Response.title
    rescontent=Response.details
    themeid=Response.themeid
    time=gettime()
    conn = sqlite3.connect('e:\\forum.db') 
    cursor = conn.cursor()
    cursor.execute("insert into response ('title','details','themeid','time') values (?,?,?,?)",(resName,rescontent,themeid,time))
    sql=" select rowid,* from response order by rowid desc;"
    cursor.execute(sql)
    result = cursor.fetchone();
    conn.commit()
    conn.close()
    return result

@app.get("/homepage/search/",response_class=HTMLResponse)
async def search(search:str): 
    conn = sqlite3.connect('e:\\forum.db') 
    cursor = conn.cursor()
    cursor.execute('select rowid,* from theme where themeName like "%'+search+'%";' )
    result = cursor.fetchall(); 
    results=[]
    c=count()
    for j in range(len(result)):
        a=[]
        for k in range(4):
            a.append(result[j][k])
        results.append(a)
        
    for i in range(len(results)):
        x=0
        for k in range(len(c)):
            if c[k][0]==results[i][0]:
                results[i].append(c[k][1])
                x=x+1
        if x==0:
            results[i].append(0)
    conn.commit()
    conn.close()
    htmlstring=''
    htmlstring=htmlstring+""""<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <html>
    <head><title>search</title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <style>
        body {font-family: Arial, Helvetica, sans-serif;}
		* {box-sizing: border-box;}
        .add-button{ background-color: #04AA6D; color: white;padding: 12px 20px;border: none;border-radius: 4px; cursor: pointer;}
		.add-button:hover{background-color: #45a049;}
		.themetitle {margin: 15px;padding: 4px 12px;background-color: #e7f3fe;border-left: 10px solid #2196F3;}
		.home:hover { background-color: RoyalBlue;  }   
        .home { background-color: DodgerBlue;  border: none;  color: white;  padding: 12px 16px;  font-size: 16px;  cursor: pointer;}
        .go{color: green; border:none; background-color: inherit;font-size: 25px;padding: 15px;width: 150px;transition: all 0.5s;}
		.go:hover {background: #eee;}
        .search-container { float: right;}
		.top .search-container button {float: right;padding: 6px 10px;margin-top: 8px;margin-right: 16px;background: #ddd;font-size: 17px;border: none;cursor: pointer;}
		.search-container button:hover {background: #ccc;}
		.top input[type=text] { padding: 6px;margin-top: 8px;font-size: 17px;border: 1px solid #ccc;}
        .footer{margin: 15px; padding: 20px 10px;background-color: #e7f3fe;text-align:center;color:black; border-bottom: 15px solid #2196F3;}
	</style>
</head>
<body >
	<div class='top'>
		<h1 style="border-bottom-style:solid; color:blue; text-align: center;">討論區</h1>
        <button type="button" class="home" onclick="back()"><i class="fa fa-home"></i> Home</button>
		<div class='search-container' >
			<form action="/homepage/search/">
				<input type="text" placeholder="Search..." name="search" >
				<button type="submit"><i class="fa fa-search"></i></button>
			</form>
		</div>
	</div>
    <div id="homepage" >"""
    if len(results)==0:
            htmlstring=htmlstring+"<div style='text-align:center'>"
            htmlstring=htmlstring+"<h1 >查無結果</h1>"
            htmlstring=htmlstring+'<button type="button" class="home" onclick="back()" > 返回</button></div>'
    for q in range(len(results)):
            htmlstring=htmlstring+"<div class='themetitle' ><p id="+str(q)+">"
            htmlstring=htmlstring+"<button type='button' class='go' onclick='gototheme("+str(results[q][0])+")'><span>"+results[q][1]+"</span></button>"
            htmlstring=htmlstring+"<h4>回覆次數："+str(results[q][4])+"</h4>";
            htmlstring=htmlstring+"<h5 style='text-align:right;'>發布時間："+results[q][3]+"</h5>"
            htmlstring=htmlstring+"</p></div>"	
    htmlstring=htmlstring+"""</div>
    <div class='footer' >
		已經到底囉！
	</div>
    <script>
         function back(){
            location.replace("/static/forum.html")
        }
        
       function gototheme(id){
			location.replace("/?themeid="+id)
			$.ajax({
				contentType:"application/json",
				url: "/?themeid="+id,
				type:"GET",
				success: function(a){
					console.log(a);
				},
				error: function(){
					alert('載入失敗，請重新整理後再來');
				}
			});
		} 
    </script>
	</body>
    </html>"""
    return htmlstring

@app.get("/sort/")
async def sort():
    sort=retrieveData()
    for i in range(len(sort)):
        for j in range(len(sort)-1,i,-1):
            if sort[j][4]>sort[i][4]:
                temp=sort[i]
                sort[i]=sort[j] 
                sort[j]=temp  
    return sort

@app.get("/sortbytime/")
async def sortbytime():
    result=retrieveData()
    sortbytime=[]
    for i in range(len(result)):
        sortbytime.append(result[len(result)-1-i])
    return sortbytime

