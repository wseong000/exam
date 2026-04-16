# %%
import requests
import pandas as pd
import matplotlib.pyplot as plt

# 中文字型設定
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False

# 台南座標
LATITUDE = 22.9999
LONGITUDE = 120.2270

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}"
    f"&longitude={LONGITUDE}"
    "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
    "&timezone=Asia%2FTaipei"
    "&forecast_days=7"
)

def weather_code_to_text(code):
    weather_dict = {
        0: "晴天",
        1: "大致晴朗",
        2: "局部多雲",
        3: "陰天",
        45: "霧",
        48: "霧淞",
        51: "小毛雨",
        53: "毛雨",
        55: "大毛雨",
        61: "小雨",
        63: "中雨",
        65: "大雨",
        80: "短暫小雨",
        81: "短暫中雨",
        82: "短暫大雨",
        95: "雷雨"
    }
    return weather_dict.get(code, "未知天氣")

def get_advice(max_temp, min_temp, rain_prob):
    advice_list = []

    # 穿搭提醒
    if max_temp >= 32:
        advice_list.append("今天天氣很熱，建議穿短袖！外出要注意防曬和補水呦")
    elif max_temp >= 28:
        advice_list.append("今天天氣偏熱，建議穿短袖或輕便衣物")
    elif max_temp >= 22:
        advice_list.append("今天天氣溫和，短袖或薄長袖都可以，不用穿太厚啦")
    else:
        advice_list.append("今天稍微偏涼，建議穿薄外套或長袖，才不會著涼")

    # 溫差提醒
    if max_temp - min_temp >= 8:
        advice_list.append("早晚溫差較大，建議多帶一件外套，小心感冒==")

    # 降雨提醒
    if rain_prob >= 70:
        advice_list.append("降雨機率高，出門記得帶雨傘喔！才不會變落湯雞")
    elif rain_prob >= 40:
        advice_list.append("可能會下雨，建議帶摺疊傘比較安心，以防萬一")
    else:
        advice_list.append("降雨機率低，通常不用特別帶傘，免驚啦")

    return "；".join(advice_list)

def fetch_weather():
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()

    daily = data["daily"]

    weather_data = pd.DataFrame({
        "日期": daily["time"],
        "天氣代碼": daily["weather_code"],
        "最高溫": daily["temperature_2m_max"],
        "最低溫": daily["temperature_2m_min"],
        "降雨機率": daily["precipitation_probability_max"]
    })

    weather_data["最高溫"] = weather_data["最高溫"].round(1)
    weather_data["最低溫"] = weather_data["最低溫"].round(1)

    weather_data["天氣狀況"] = weather_data["天氣代碼"].apply(weather_code_to_text)

    weather_data["提醒"] = weather_data.apply(
        lambda row: get_advice(row["最高溫"], row["最低溫"], row["降雨機率"]),
        axis=1
    )

    return weather_data

def show_weather(weather_data):
    print("台南未來一週天氣與穿搭提醒系統")
    print("=" * 70)

    for _, row in weather_data.iterrows():
        print(f"日期：{row['日期']}")
        print(f"天氣：{row['天氣狀況']}")
        print(f"最高溫：{row['最高溫']}°C")
        print(f"最低溫：{row['最低溫']}°C")
        print(f"降雨機率：{row['降雨機率']}%")
        print(f"提醒：{row['提醒']}")
        print("-" * 70)

def plot_weather(weather_data):
    plt.figure(figsize=(10, 5))
    plt.plot(weather_data["日期"], weather_data["最高溫"], marker="o", label="最高溫")
    plt.plot(weather_data["日期"], weather_data["最低溫"], marker="o", label="最低溫")

    plt.title("台南未來一週高低溫變化")
    plt.xlabel("日期")
    plt.ylabel("溫度 (°C)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig("tainan_weather_chart.png")
    plt.show()

def main():
    try:
        weather_data = fetch_weather()

        print("一週天氣表格：")
        print(weather_data[["日期", "天氣狀況", "最高溫", "最低溫", "降雨機率", "提醒"]])

        print()
        show_weather(weather_data)

        weather_data.to_csv("tainan_weather_report.csv", index=False, encoding="utf-8-sig")
        print("已輸出 tainan_weather_report.csv")

        plot_weather(weather_data)
        print("已輸出 tainan_weather_chart.png")

    except Exception as e:
        print("程式執行失敗")
        print("錯誤原因：", e)

if __name__ == "__main__":
    main()


