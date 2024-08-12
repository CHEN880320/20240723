# views.py

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import openai
import json
import leafmap
import os
import tempfile
import requests


# 配置 OpenAI API 密鑰
openai.api_key = settings.OPENAI_API_KEY
# 配置 Geocoding API（例如 OpenStreetMap Nominatim）
GEOCODING_API_URL = "https://nominatim.openstreetmap.org/search"

def get_openai_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            max_tokens=128,
            temperature=0.5,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"
    
    
def get_location_from_openai(message):
    prompt = f"Extract the location from this message: '{message}'. Provide the location name only."
    response = get_openai_response(prompt)
    print(f"OpenAI response: {response}")
    return response  


def get_coordinates_from_location(location):
    params = {
        'q': location,
        'format': 'json'
    }
    response = requests.get(GEOCODING_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            lat, lon = float(data[0]['lat']), float(data[0]['lon'])
            print(f"Coordinates for {location}: ({lat}, {lon})")  # 添加调试日志
            return lat, lon

    return None, None

  
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data['message']
            bot_response = get_openai_response(user_message)
            
            # 基于用户输入生成地图
            location = get_location_from_openai(user_message)
            map_type = 'HYBRID'  # 这里可以根据需求解析用户输入的地图类型
            map_path = generate_map(location, map_type)
            
            if map_path:
                return JsonResponse({'response': bot_response, 'map_image_path': map_path})
            else:
                return JsonResponse({'response': bot_response, 'error': 'Could not generate map for the given location'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except KeyError:
            return JsonResponse({'error': 'Missing "message" key'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    
def generate_map(location, map_type):
    lat, lon = get_coordinates_from_location(location)
    if lat is None or lon is None:
        print(f"Could not find coordinates for location: {location}") 
        return None
    
    # 创建地图
    m = leafmap.Map(center=[lat, lon], zoom=10)
    if map_type == 'HYBRID':
        m.add_basemap('HYBRID')
    elif map_type == 'TERRAIN':
        m.add_basemap('TERRAIN')
    else:
        m.add_basemap('ROADMAP')

    # 保存地图为图片
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        map_path = tmpfile.name
        m.to_image(outfile=map_path)
        print(f"Map saved at: {map_path}")
    return map_path
@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data['message']
            bot_response = get_openai_response(user_message)
            
            return JsonResponse({'response': bot_response})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except KeyError:
            return JsonResponse({'error': 'Missing "message" key'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def show_map(request):
    map_path = request.GET.get('path', '')
    if os.path.exists(map_path):
        with open(map_path, 'rb') as f:
            return HttpResponse(f.read(), content_type="image/png")
    return HttpResponse('Map not found', status=404)


def index(request):
    return render(request, 'index.html')
