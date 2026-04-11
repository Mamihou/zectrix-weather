import requests
from datetime import datetime, timezone, timedelta
import os

# 配置
QWEATHER_API_KEY = os.environ.get("QWEATHER_API_KEY")
CITY_ID = os.environ.get("CITY_ID")
CITY_NAME = os.environ.get("CITY_NAME")
ZECTRIX_API_KEY = os.environ.get("ZECTRIX_API_KEY")
DEVICE_ID = os.environ.get("DEVICE_ID")
QWEATHER_API_HOST = os.environ.get("QWEATHER_API_HOST")

def get_7day_weather():
    """获取7天天气预报"""
    url = f"{QWEATHER_API_HOST}/v7/weather/7d?key={QWEATHER_API_KEY}&location={CITY_ID}"
    print(f"请求天气API: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text}")
        return response.json()
    except Exception as e:
        print(f"API请求异常: {str(e)}")
        return {"code": 500, "message": str(e)}

def push_weather_to_pages(weather_data):
    """推送7天天气到设备的一个页面"""
    print(f"天气数据: {weather_data}")
    if "error" in weather_data:
        return {"code": 1, "message": f"获取天气失败: {weather_data['error'].get('detail', '未知错误')}"}
    elif weather_data.get("code") == "200":
        daily = weather_data.get("daily", [])
        china_tz = timezone(timedelta(hours=8))
        current_time = datetime.now(china_tz).strftime("%Y-%m-%d %H:%M")
        today = datetime.now(china_tz).strftime("%Y-%m-%d")
        
        weather_text = f"上一次推送天气时间: {current_time}\n{'=' * 61}\n　　　　　　　　　{CITY_NAME}7天天气预报\n\n"
        
        for i, day in enumerate(daily[:7]):
            date = day["fxDate"]
            temp_max = day["tempMax"]
            temp_min = day["tempMin"]
            text_day = day["textDay"]
            text_night = day["textNight"]
            humidity = day["humidity"]
            uv_index = day["uvIndex"]
            
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_of_week = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"][date_obj.weekday()]
            
            if len(text_day) == 1:
                text_day = text_day + "天"
            if len(text_night) == 1:
                text_night = text_night + "天"
            
            if date == today:
                weather_text += f"今天\n"
                weather_text += f"{date_obj.month}月{date_obj.day}日 {day_of_week}  白:{text_day}  夜:{text_night}  温:{temp_min:>2}°-{temp_max:>2}°  湿:{humidity:>3}%  紫外线:{uv_index:>2}\n\n"
            else:
                friendly_date = f"{date_obj.month}月{date_obj.day}日 {day_of_week}"
                weather_text += f"{friendly_date}  白:{text_day}  夜:{text_night}  温:{temp_min:>2}°-{temp_max:>2}°  湿:{humidity:>3}%  紫外线:{uv_index:>2}\n"
        
        push_to_device(weather_text, "1")
        
        return {"code": 0, "message": "成功推送7天天气到一页"}
    return {"code": 1, "message": f"获取天气失败: {weather_data.get('message', '未知错误')}"}

def push_to_device(text, page_id):
    """推送内容到设备的指定页面"""
    if not DEVICE_ID:
        print("错误: 设备ID未设置")
        return
    
    url = f"https://cloud.zectrix.com/open/v1/devices/{DEVICE_ID}/display/text"
    headers = {
        "X-API-Key": ZECTRIX_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "fontSize": 11,
        "pageId": page_id
    }
    print(f"推送页面 {page_id} 到设备 {DEVICE_ID}")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"推送响应: {response.status_code} - {response.text}")
        return response.json()
    except Exception as e:
        print(f"推送异常: {str(e)}")
        return {"code": 500, "message": str(e)}

if __name__ == "__main__":
    print(f"设备ID: {DEVICE_ID}")
    weather_data = get_7day_weather()
    result = push_weather_to_pages(weather_data)
    print("总推送结果:", result)