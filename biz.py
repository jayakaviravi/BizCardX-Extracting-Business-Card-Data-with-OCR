import easyocr
from PIL import Image,ImageDraw
import pandas as pd
import numpy as np
import re
import io
import mysql.connector as sql
import streamlit as st
from streamlit_option_menu import option_menu
import base64

#SQL connection to create database
    
mydb=sql.connect(host='127.0.0.1',
                user='root',
                password='test',
                port='3306'
                )
cur=mydb.cursor(buffered=True)
cur.execute('create database if not exists bizcard_data')


#setting page configuration
imge=Image.open("C:\\Users\\JAYAKAVI\\Downloads\\biz.png")
st.set_page_config(page_title="Bussiness card", 
                    page_icon=imge, 
                    layout="wide",
                    initial_sidebar_state="expanded")

st.title(':blue[BizCardX: Extracting Business Card Data with OCR]')
st.divider()



#creating opyion menu

with st.sidebar:
    selected = option_menu(None, ["Application details","Uploading image","Modify","Delete"], 
                           icons=["house-door-fill", "cloud-upload","vector-pen","eraser"],
                           default_index=0,
                           orientation="horizontal",
                           styles={"nav-link": {"font-size": "20px", "text-align": "centre", "margin": "0px", 
                                                "--hover-color": "white"},
                                   "icon": {"font-size": "20px"},
                                   "container" : {"max-width": "3000px"},
                                   "nav-link-selected": {"background-color": "violet"}})


def image_to_text(path):
    input_img= Image.open(path)

    #converting image to array format
    image_arr= np.array(input_img)

    reader= easyocr.Reader(['en'])
    res= reader.readtext(image_arr,detail= 0)
    return res,input_img


        
def card_data_extraction(text):
    extrd_data={"card_holdername":[],
                "Designation" :[],
                "Company_name":[],
                "Contact":[],
                "Email":[],
                "Website":[],
                "Area": [],
                "City": [],
                "State": [],
                "Pincode":[]
                }
    city = ""  
    for j, i in enumerate(text):
        
        # To get CARD HOLDER NAME
        if j == 0:
            extrd_data["card_holdername"].append(i)
        
        # To get DESIGNATION
        elif j == 1:
            extrd_data["Designation"].append(i)
        
        # To get COMPANY NAME
        elif j == len(text) - 1:
            extrd_data["Company_name"].append(i)
        
        # To get MOBILE NUMBER
        elif "-" in i:
            extrd_data["Contact"].append(i)
            if len(extrd_data["Contact"]) == 2:
                extrd_data["Contact"] = " , ".join(extrd_data["Contact"])

        # To get EMAIL ID
        elif "@" in i:
            extrd_data["Email"].append(i)
        
        # To get WEBSITE_URL
        if "www " in i.lower() or "www." in i.lower():
            extrd_data["Website"].append(i)
        elif "WWW" in i:
            extrd_data["Website"].append(text[j-1] + "." + text[j])

        # To get AREA
        if re.findall("^[0-9].+, [a-zA-Z]+", i):
            extrd_data["Area"].append(i.split(",")[0])
        elif re.findall("[0-9] [a-zA-Z]+", i):
            extrd_data["Area"].append(i)
        # To get CITY NAME
        City1 = re.findall(".+St , ([a-zA-Z]+).+", i)
        City2 = re.findall(".+St,, ([a-zA-Z]+).+", i)
        City3 = re.findall("^[E].*", i)
        if City1:
            city = City1[0]  
        elif City2:
            city = City2[0]  
        elif City3:
            city = City3[0]  
        
        # To get STATE
        state_m = re.findall("[a-zA-Z]{9} +[0-9]", i)
        if state_m:
            extrd_data["State"].append(i[:9])
        elif re.findall("^[0-9].+, ([a-zA-Z]+);", i):
            extrd_data["State"].append(i.split()[-1])
        if len(extrd_data["State"]) == 2:
            extrd_data["State"].pop(0)

        # To get PINCODE
        if len(i) >= 6 and i.isdigit():
            extrd_data["Pincode"].append(i)
        elif re.findall("[a-zA-Z]{9} +[0-9]", i):
            extrd_data["Pincode"].append(i[10:])


    extrd_data["City"].append(city)
    return extrd_data


if selected=='Application details':

    col1,col2,col3=st.columns([2,3,2],gap='small')    
    
    with col2:
        file_ = open("C:/Users/JAYAKAVI/Downloads/Blue_Business_Card_Front_AE_Ready-ezgif.com-webp-to-gif-converter.gif", "rb")
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        file_.close()

        st.markdown(
            f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
            unsafe_allow_html=True,
        )
    
    st.subheader(":red[Technologies used]")
    st.markdown("#####  OCR,streamlit GUI, SQL,Data Extraction")
    st.subheader(":red[EasyOCR]")
    st.markdown("##### EasyOCR is an open-source Optical Character Recognition (OCR) Python package that is easy to use and versatile.It is used to extract text from images or scanned documents using computers")
    st.subheader(":red[Overview]")
    st.markdown("##### In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR.This app would also allow users to save the extracted information into a database along with the uploaded business card image")


if selected=='Uploading image':
    st.subheader(":red[Business Card]")
    img = st.file_uploader(label="Upload the image", type=['png', 'jpg', 'jpeg'], label_visibility="hidden")   
 
    if img != None:
        st.image(img,width= 500)

        text_image,input_img= image_to_text(img)
        text_dict= card_data_extraction(text_image)

        if text_dict:
            st.success(":green[TEXT IS EXTRACTED SUCCESSFULLY]")
        
        df=pd.DataFrame(text_dict)
        st.dataframe(df)

        # Converting image into bytes
        img_bytes = io.BytesIO()
        input_img.save(img_bytes, format='PNG')
        b_img_data= img_bytes.getvalue()

        #Creating dictionary
        data= {"Image":[b_img_data]}
        df1= pd.DataFrame(data)
        df2= pd.concat([df,df1],axis=1)


        button1= st.button("Save and upload to database",use_container_width= True)
        
        if button1:
            
            mydb=sql.connect(host='127.0.0.1',
                user='root',
                password='test',
                port='3306',
                database='bizcard_data'
                )
            cur=mydb.cursor(buffered=True)
            create_table='''create table if not exists card_details (card_holdername text,
                                                         Designation text,
                                                         Company_name varchar(100),
                                                         Contact varchar(100),
                                                         Email varchar(100),
                                                         Website varchar(100),
                                                         Area varchar(50),
                                                         City varchar(50),
                                                         State varchar(50),                                                        
                                                         Pincode varchar(50),
                                                         Image LONGBLOB
                                                         )'''
            cur.execute(create_table)
            mydb.commit()

            for index,row in df2.iterrows():
                query='''insert into card_details (card_holdername,Designation,Company_name,Contact,Email,Website,Area,City,State,Pincode,Image)
                                       values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                cur.execute(query,tuple(row))
                mydb.commit()
                query1='''select card_holdername,Designation,Company_name,Contact,Email,Website,Area,City,State,Pincode from card_details'''
                cur.execute(query1)
                mydb.commit()
                df3=pd.DataFrame(cur.fetchall(),columns=['card_holder_name','Designation','Company_name','Contact','Email','Website','Area','City','State','Pin_code'])
                st.dataframe(df3)
                st.success(":green[Datas uploaded sucessfully]")
                st.balloons()

if selected=="Modify":
    st.markdown("### :red[Modify the card datas here]")
    mydb=sql.connect(host='127.0.0.1',
                user='root',
                password='test',
                port='3306',
                database='bizcard_data'
                )
    cur=mydb.cursor(buffered=True)
   
    cur.execute('''select card_holdername from card_details''' )
    result=cur.fetchall()
    cards={}
    for i in result:
        cards[i[0]]=i[0]
    options=['select card name'] + list(cards.keys())
    select_card=st.selectbox(":violet[select card name]",options)
    if select_card=='select card name':
        st.warning('Card is not selected please select', icon="⚠️")
    else:
        cur.execute(''' select card_holdername,Designation,Company_name,Contact,Email,Website,Area,City,State,Pincode from card_details where card_holdername=%s''',
                (select_card,))
        result=cur.fetchone()
        col1,col2=st.columns(2)
        with col1:
            m_Holdername=st.text_input("Holder_name",result[0])
            m_Designation=st.text_input("Designation",result[1])
            m_company_name = st.text_input("Company_Name", result[2])
            m_contact=st.text_input("contact",result[3])
            m_Email=st.text_input("Email",result[4])
        
        with col2:
            m_website=st.text_input("website",result[5])
            m_area=st.text_input("Area",result[6])
            m_city=st.text_input("City",result[7])
            m_state=st.text_input("State",result[8])
            m_pincode=st.text_input("pincode",result[9])
        
    #commiting changes to database
        if st.button(":red[Upload changes to database]"):
            cur.execute('''update card_details set card_holdername=%s,Designation=%s,Company_name=%s,Contact=%s,Email=%s,Website=%s,Area=%s,City=%s,State=%s,Pincode=%s where card_holdername=%s''',
                        (m_Holdername,m_Designation,m_company_name,m_contact,m_Email,m_website,m_area,m_city,m_state,m_pincode,select_card))
            mydb.commit()
            st.success('SUCCESSFULLY UPLOADED', icon="✅")
            st.balloons()

    #view data
    if st.button(":red[View database after altered]"):
        cur.execute(''' select card_holdername,Designation,Company_name,Contact,Email,Website,Area,City,State,Pincode from card_details''')
        df4=pd.DataFrame(cur.fetchall(),columns=['card_holder_name','Designation','Company_name','Contact','Email','Website','Area','City','State','Pin_code'])
        st.dataframe(df4)

if selected=="Delete":
    st.markdown("### :red[Delete the card datas here]")
    mydb=sql.connect(host='127.0.0.1',
                user='root',
                password='test',
                port='3306',
                database='bizcard_data'
                )
    cur=mydb.cursor(buffered=True)
    col1,col2=st.columns(2)
    with col1:
        cur.execute('''select card_holdername from card_details''' )
        result=cur.fetchall()
        cards={}
        for i in result:
            cards[i[0]]=i[0]
        options=['None'] + list(cards.keys())
        select_card=st.selectbox("select card name",options)
        
    with col2:
        cur.execute('''select Designation from card_details''' )
        result=cur.fetchall()
        cards={}
        for i in result:
            cards[i[0]]=i[0]
        options=['None'] + list(cards.keys())
        select_designation=st.selectbox("select Designation name",options)
        
    cola, colb, colc = st.columns([5, 3, 3])
    with colb:
        remove = st.button("Click here to delete")
        if select_card and select_designation and remove:
            cur.execute(f"delete from card_details where card_holdername='{select_card}' and Designation='{select_designation}' ")
            mydb.commit()

            if remove:
                st.warning('DELETED', icon='🚨')
        
    #view data after deletion
    if st.button(":red[View database after card datas are deleted]"):
        cur.execute(''' select card_holdername,Designation,Company_name,Contact,Email,Website,Area,City,State,Pincode  from card_details''')
        df5=pd.DataFrame(cur.fetchall(),columns=['card_holder_name','Designation','Company_name','Contact','Email','Website','Area','City','State','Pin_code'])
        st.dataframe(df5)
    


        

        




