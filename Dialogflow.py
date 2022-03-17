#!/usr/bin/env python

import urllib
import json
import os

#iottalk
import time, random, requests
import DAN
ServerURL = 'https://iottalk.tw'      #with non-secure connection
Reg_addr = '3BA8B9017A8E' #if None, Reg_addr = MAC address
DAN.profile['dm_name']='Voicetalk-zhTW'
DAN.profile['df_list']=['Device_Curtain-I', 'Device_Fan-I', 'Device_Fan2-I', 'Device_Light-I', 'Device_Skeleton-I' ,'Device_Agent-O']
DAN.profile['d_name']= 'Dialogflow' 

#iottalk end

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    #askweather的地方是Dialogflow>Intent>Action 取名的內容
    print("json result:", req)
    intent = req.get("queryResult").get("intent").get("displayName")
    print("intent result", intent)
    way = match_intent(intent, req)

    #===================================================================================
    if req.get("queryResult").get("intent").get("displayName") == "Demo-iottalk-Bulb":
        print("previous demo!")
        return {}
    #result = req.get("queryResult")
    #parameters = result.get("parameters")
    #parameters.get("weatherlocation")的weatherlocation是Dialogflow > Entitiy
    #也就是步驟josn格式中parameters>weatherlocation
    #keyword = parameters.get("Device-Action")
    #print("keyword", keyword)
    #先設定一個回應
    #speech就是回應的內容
    speech ='好的, '
    if(way != "input"): #means sensor
        speech =  speech + way
    
    #print("Response:")
    #print(speech)
    
    #回傳
    return {
        "fulfillmentText": speech,
        
        #"data": {},
        #"contextOut": [],
        "source": "agent"
    }


def match_intent(intent,req):
    if(intent == "Curtain-Operation"):
        curtain_No = req.get("queryResult").get("parameters").get("curtain")
        device_onoff = req.get("queryResult").get("parameters").get("device-onoff")
        #curtain have left to right label as 1~3
        print("List of curtain", curtain_No)
        print(type(curtain_No))
        if '左邊窗簾' in curtain_No:
            print("left curtain")
            if(device_onoff == "開啟"):
                DAN.push('Device_Curtain-I', 2)
            else:
                DAN.push('Device_Curtain-I', 1)
        if '中間窗簾' in curtain_No:
            print("center curtain")
            if(device_onoff == "開啟"):
                DAN.push('Device_Curtain-I', 4)
            else:
                DAN.push('Device_Curtain-I', 3)
        if '右邊窗簾' in curtain_No:
            print("right curtain")
            if(device_onoff == "開啟"):
                DAN.push('Device_Curtain-I', 6)
            else:
                DAN.push('Device_Curtain-I', 5)
        if '窗簾' in curtain_No:
            print("all curtain")
            if(device_onoff == "開啟"):
                DAN.push('Device_Curtain-I', 8)
            else:
                DAN.push('Device_Curtain-I', 7)
        return "input"

    elif(intent == "Fan-Operation"):
        device_fan = req.get("queryResult").get("parameters").get("device-fan")
        device_onoff = req.get("queryResult").get("parameters").get("device-onoff")
        device_speed = req.get("queryResult").get("parameters").get("number")
        device_brand = req.get("queryResult").get("parameters").get("device-brand")
        print("brand of fan", device_brand)
        print("fanspeed(not required): ", device_speed, type(device_speed))
        print("onoff: ", device_onoff)
        #need a brand selector to push to different device feature
        if(device_brand == "大同" or "大同" in device_brand):            
            if(device_onoff == "開啟"):
                DAN.push('Device_Fan-I', 1)
            elif(device_onoff == "關閉"):
                DAN.push('Device_Fan-I', 0)           
            if(device_speed != '' and (device_speed<=5 and device_speed>=1)):
                print("legal fanspeed")
                DAN.push('Device_Fan-I', int(device_speed))
        if(device_brand == "奇美" or "奇美" in device_brand):
            if(device_onoff == "開啟"):
                DAN.push('Device_Fan2-I', 1)
            elif(device_onoff == "關閉"):
                DAN.push('Device_Fan2-I', 0)   
            if(device_speed != '' and (device_speed<=8 and device_speed>=1)):
                print("legal fanspeed")
                DAN.push('Device_Fan2-I', int(device_speed))
        return "input"

    elif(intent == "Light-Operation"):
        device_onoff = req.get("queryResult").get("parameters").get("device-onoff")

        if(device_onoff == "開啟"):
            DAN.push("Device_Light-I", 1)
        elif(device_onoff == "關閉"):
            DAN.push("Device_Light-I", 0)
        return "input"

    elif(intent == "Skeleton-Operation"):
        device_size = req.get("queryResult").get("parameters").get("number")
        DAN.push('Device_Skeleton-I', int(device_size))
        
		
	
    #elif(intent == "Sensor-Operation"):
	#    ODF_data = DAN.pull('Device_Agent-O')
    #    return ODF_data
		
    #elif(intent == "Skeleton-Operation"):
	#    device_size = req.get("queryResult").get("parameters").get("number")
	#    DAN.push('Device_Skeleton-I', int(device_size))


if __name__ == "__main__":
    DAN.device_registration_with_retry(ServerURL, Reg_addr)
    app.run(host="0.0.0.0", debug=True,port=9457)
    
