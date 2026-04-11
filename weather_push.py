import requests
from datetime import datetime, timezone, timedelta
import os

# 配置
QWEATHER_API_KEY = os.environ.get("QWEATHER_API_KEY")
CITY_ID = os.environ.get("CITY_ID", "101300105")  # 南宁西乡塘区
ZECTRIX_API_KEY = os.environ.get("ZECTRIX_API_KEY", "zt_e78f09c7753b6fecb84ceadbcceef149")
DEVICE_ID = os.environ.get("DEVICE_ID")
# 使用用户在和风天气控制台获取的API Host
QWEATHER_API_HOST = os.environ.get("QWEATHER_API_HOST", "https://n37byhem8d.re.qweatherapi.com")

# 天气代码到emoji的映射
WEATHER_EMOJI = {
    # 晴天
    "100": "☀️",  # 晴
    # 多云
    "101": "⛅",  # 多云
    "102": "☁️",  # 少云
    "103": "☁️",  # 晴间多云
    "104": "☁️",  # 阴
    # 阴天
    "150": "☁️",  # 阴
    # 雾
    "300": "🌫️",  # 雾
    "301": "🌫️",  # 霾
    "302": "🌫️",  # 扬沙
    "303": "🌫️",  # 浮尘
    "304": "🌫️",  # 沙尘暴
    "305": "🌫️",  # 强沙尘暴
    "306": "🌫️",  # 浮沉
    "307": "🌫️",  # 扬沙
    "308": "🌫️",  # 浮尘
    "309": "🌫️",  # 沙尘暴
    "310": "🌫️",  # 强沙尘暴
    "311": "🌫️",  # 浮沉
    "312": "🌫️",  # 扬沙
    "313": "🌫️",  # 浮尘
    "314": "🌫️",  # 沙尘暴
    "315": "🌫️",  # 强沙尘暴
    # 雨
    "350": "🌦️",  # 小雨
    "351": "🌧️",  # 中雨
    "352": "⛈️",  # 大雨
    "353": "⛈️",  # 暴雨
    "354": "⛈️",  # 大暴雨
    "355": "⛈️",  # 特大暴雨
    "356": "🌦️",  # 雷阵雨
    "357": "⛈️",  # 雷暴大雨
    "358": "⛈️",  # 雷暴暴雨
    "359": "🌦️",  # 阵雨
    "360": "🌦️",  # 小雨
    "361": "🌧️",  # 中雨
    "362": "⛈️",  # 大雨
    "363": "⛈️",  # 暴雨
    "364": "⛈️",  # 大暴雨
    "365": "⛈️",  # 特大暴雨
    "366": "🌦️",  # 阵雨
    "367": "🌦️",  # 阵雨
    "368": "🌦️",  # 阵雨
    # 雪
    "400": "🌨️",  # 小雪
    "401": "❄️",  # 中雪
    "402": "❄️",  # 大雪
    "403": "❄️",  # 暴雪
    "404": "🌨️",  # 雨夹雪
    "405": "🌨️",  # 雨雪天气
    "406": "🌨️",  # 阵雨夹雪
    "407": "🌨️",  # 阵雪
    "408": "🌨️",  # 小雪
    "409": "❄️",  # 中雪
    "410": "❄️",  # 大雪
    "411": "❄️",  # 暴雪
    "412": "🌨️",  # 雨夹雪
    "413": "🌨️",  # 雨雪天气
    "414": "🌨️",  # 阵雨夹雪
    "415": "🌨️",  # 阵雪
    "416": "🌨️",  # 小雪
    "417": "❄️",  # 中雪
    "418": "❄️",  # 大雪
    # 其他
    "500": "🌡️",  # 热
    "501": "❄️",  # 冷
    "999": "❓"   # 未知
}

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

def get_weather_emoji(icon_code):
    """根据天气代码获取对应的emoji"""
    return WEATHER_EMOJI.get(icon_code, "❓")

def push_weather_to_pages(weather_data):
    """推送7天天气到设备的一个页面"""
    print(f"天气数据: {weather_data}")
    # 检查新的错误格式
    if "error" in weather_data:
        return {"code": 1, "message": f"获取天气失败: {weather_data['error'].get('detail', '未知错误')}"}
    elif weather_data.get("code") == "200":
        daily = weather_data.get("daily", [])
        # 获取中国时区（UTC+8）的当前时间
        china_tz = timezone(timedelta(hours=8))
        current_time = datetime.now(china_tz).strftime("%Y-%m-%d %H:%M")
        today = datetime.now(china_tz).strftime("%Y-%m-%d")
        
        # 构建7天天气的文本
        weather_text = f"上一次推送天气时间: {current_time}\n{'=' * 61}\n　　　　　　　　　南宁西乡塘区7天天气预报\n\n"
        
        for i, day in enumerate(daily[:7]):  # 确保只推送7天
            date = day["fxDate"]
            temp_max = day["tempMax"]
            temp_min = day["tempMin"]
            text_day = day["textDay"]
            text_night = day["textNight"]
            humidity = day["humidity"]
            uv_index = day["uvIndex"]
            
            # 格式化日期
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_of_week = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"][date_obj.weekday()]
            
            # 统一天气文本长度为2个字
            if len(text_day) == 1:
                text_day = text_day + "天"
            if len(text_night) == 1:
                text_night = text_night + "天"
            
            # 区分当天和后续日期
            if date == today:
                weather_text += f"今天\n"
                weather_text += f"{date_obj.month}月{date_obj.day}日 {day_of_week}  白:{text_day}  夜:{text_night}  温:{temp_min:>2}°-{temp_max:>2}°  湿:{humidity:>3}%  紫外线:{uv_index:>2}\n\n"
            else:
                friendly_date = f"{date_obj.month}月{date_obj.day}日 {day_of_week}"
                weather_text += f"{friendly_date}  白:{text_day}  夜:{text_night}  温:{temp_min:>2}°-{temp_max:>2}°  湿:{humidity:>3}%  紫外线:{uv_index:>2}\n"
        
        # 推送到第1页
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