from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.models import FlexSendMessage, TextSendMessage, MessageEvent, ImageSendMessage
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from pymongo import MongoClient
from linebot.exceptions import LineBotApiError

#點擊廣告、熱搜、查詢並輸出biggo資料
def Biggo(name_1,l_price,h_price):
    driver = webdriver.Chrome("/kinslersi/chromedriver")
    driver.get("https://biggo.com.tw/")
    time.sleep(1)
    # 商品搜尋
    driver.find_element(By.XPATH,('/html/body/div[1]/div[2]/form/div/div[1]/input')).send_keys(name_1)
    webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
    time.sleep(1)
    # 最低價
    driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[2]/div[1]/div/div/div[1]/div[1]/div[2]/input[1]')).send_keys(l_price)
    # 最高價
    driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[2]/div[1]/div/div/div[1]/div[1]/div[2]/input[2]')).send_keys(h_price)
    # 價格搜尋
    driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[2]/div[1]/div/div/div[1]/div[1]/div[2]/div')).click()
    # 價格排序
    driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[1]/div[1]/div/div/div[2]/a[2]')).click()
    item=1
    page=1
    search_data=[]
    while True:
        if page==2:
            break
        try:
            #商品名稱
            name=driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[1]/div[2]/div['+str(item)+']/div/div[2]/div[1]/div[1]/div[1]/a')).text
            #價格
            price=driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[1]/div[2]/div['+str(item)+']/div/div[2]/div[2]/div[1]/a/span')).text
            #連結
            url=driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[1]/div[2]/div['+str(item)+']/div/div[2]/div[1]/div[1]/div[1]/a')).get_attribute('href')
            #照片
            photo=driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[1]/div[2]/div['+str(item)+']/div/div[1]/div/a/img')).get_attribute('src')
            item+=1
        except:
            try:
                name=driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[1]/div[2]/div['+str(item+1)+']/div/div[2]/div[1]/div[1]/div[1]/a')).text
                price=driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[1]/div[2]/div['+str(item+1)+']/div/div[2]/div[2]/div[1]/a/span')).text
                url=driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[1]/div[2]/div['+str(item+1)+']/div/div[2]/div[1]/div[1]/div[1]/a')).get_attribute('href')
                photo=driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[1]/div[2]/div['+str(item+1)+']/div/div[1]/div/a/img')).get_attribute('src')                                                                                                                        
                item+=1
            except:
                page+=1
                driver.find_element(By.XPATH,('/html/body/div[6]/div/div/div/div[1]/div[2]/div[35]/nav/ul/li['+str(page)+']/a')).click()
                item=1
        finally:
            row_data={"name":name,"price":price,"url":url,"photo":photo}
            search_data.append(row_data)
    driver.close()
    return search_data

# 確認project database是否存在
def check_database_exist():
    client=MongoClient(mongoclient)
    dblist = client.list_database_names()
    if "project" not in dblist:
        client.project

# 確認輸入商品名稱的collection是否存在
def check_collection_exist(num1):
    client=MongoClient(mongoclient)
    db=client.project
    collist = db.list_collection_names()
    if num1 not in collist:
        db[num1]

# 上傳至pymongo atlas
def pymongo(data,num1):
    check_database_exist()
    check_collection_exist(num1)
    client=MongoClient(mongoclient)
    db=client.project
    col=db[num1]
    col.insert_many(data)

# line回傳 flex messages
def response(user_id,search_name):
    client=MongoClient(mongoclient)
    db=client.project
    col=db[search_name]
    item=col.find_one()
    print("user id: ",user_id)
    try:
        line_bot_api.push_message(user_id,FlexSendMessage(
            alt_text='hello',
            contents={
                    "type": "carousel",
                    "contents": [
                        {
                        "type": "bubble",
                        "hero": {
                            "type": "image",
                            "size": "full",
                            "aspectRatio": "20:13",
                            "aspectMode": "cover",
                            "url": item['photo']
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                            {
                                "type": "text",
                                "text": item['name'],
                                "wrap": True,
                                "weight": "bold",
                                "size": "xl"
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": item['price'],
                                    "wrap": True,
                                    "weight": "bold",
                                    "size": "xl",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": ".99",
                                    "wrap": True,
                                    "weight": "bold",
                                    "size": "sm",
                                    "flex": 0
                                }
                                ]
                            }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                            {
                                "type": "button",
                                "style": "primary",
                                "action": {
                                "type": "uri",
                                "label": "前往連結",
                                "uri": item['url']
                                }
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "uri",
                                "label": "Add to wishlist",
                                "uri": "https://linecorp.com"
                                }
                            }
                            ]
                        }
                        },
                    ]
                    }
        ))
    except LineBotApiError as e:
        print('e.status_code:', e.status_code)
        print('e.error.message:',e.error.message)
        print('e.error.details:',e.error.details)


menu=[]
app = Flask(__name__)
line_bot_api = LineBotApi("7MrQIcAMdMP6HImReXET8k8aJ8XxdrbBCOcKs6X4TSf8fUG9GZ1VrfVtq6nzjyTUhx1ZzvebUihqqcIHii17lMNX/hWAAeevTYhhhuWpn4nYyEnnoGNZ6B3a31NCbhT7DV116jAX3vLQJKGiJGsRQwdB04t89/1O/w1cDnyilFU=")
@app.route("/verify", methods=['POST'])
def verify():    
    data = request.get_json()
    print(data)
    if len(menu)==0:
        line_bot_api.reply_message(
            data['events'][0]['replyToken'],
            TextSendMessage("你想找什麼貨?")
        )
        menu.append(data['events'][0]['message']['text'])
    elif len(menu)==1:
        menu.append(data['events'][0]['message']['text'])
        line_bot_api.reply_message(
            data['events'][0]['replyToken'],
            TextSendMessage("那輸入你的最低價.")
        )
    elif len(menu)==2:
        menu.append(data['events'][0]['message']['text'])
        line_bot_api.reply_message(
            data['events'][0]['replyToken'],
            TextSendMessage("你的最高價勒?")
        )
    elif len(menu)==3:
        menu.append(data['events'][0]['message']['text'])
        line_bot_api.reply_message(
            data['events'][0]['replyToken'],
            TextSendMessage("等我去找一下市面上符合你的連結")
        )
    else:
        menu.append(data['events'][0]['message']['text'])
        line_bot_api.reply_message(
            data['events'][0]['replyToken'],
            TextSendMessage("年輕人有沒有耐性?")
        )
    data=Biggo(menu[1],menu[2],menu[3])
    pymongo(data,menu[1])
    response(data["events"][0]["source"]['userId'],menu[1])
    return "ok",200


if __name__=="__main__":
    mongoclient="mongodb+srv://test:aqswde123@cluster0.n89m6ep.mongodb.net/?retryWrites=true&w=majority"
    app.run(port=3203)
    