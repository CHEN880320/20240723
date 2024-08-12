
# 1. 網頁設計
網頁設計是用Django開發，將聊天機器人與OpenAI API連接，作為運作核心。

目前OpenAI已成功串接，可以像ChatGPT那樣做答覆。(OpenAi API要錢QQ


#### 設計邏輯是openai透過使用者輸入的文字內容，分析解讀並在後端進行leafmap繪圖，最後再傳送至前端。
我在20240723\chatbot_project\chat\views.py中，定義get_openai_response，進行聊天機器人的回覆；

在get_location_from_openai，抓取使用者輸入的地點，並且get_coordinates_fron_location，獲取地點的坐標(這部分不確定後續是否會用到)
# 2. leafmap
20240723\chatbot_project\chat\views.py中，定義chat，根據地點坐標，加上使用者需要的地圖類型，

最後經由generate_map創建地圖，show_map將地圖呈現出來。


我從終端機在項目中活化虛擬環境

        venv\Scripts\activate
        
再cd 20240723到這個資料夾。
        python manage.py runserver
![image](https://github.com/CHEN880320/20240723/blob/main/1723453907255.jpg)

chatbot_project\chatbot_project\api_urls.json，有從研究資料寄存所-台江，抓下來的各種圖資API。
