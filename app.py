import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение API ключа из переменных окружения
SUNO_API_KEY = os.getenv('SUNO_API_KEY')

BASE_URL = "https://api.aimlapi.com"

def generate_music(prompt, tags=None, title=None, make_instrumental=False, wait_audio=True):
    """Generate music using the Suno v3.5 API"""
    headers = {
        "Authorization": f"Bearer {SUNO_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "make_instrumental": make_instrumental,
        "wait_audio": wait_audio
    }

    if tags:
        payload["tags"] = tags
    if title:
        payload["title"] = title

    url = f"{BASE_URL}/generate/custom-mode"

    st.write("Отправка запроса к API...")
    st.json(payload)

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        st.write(f"Статус ответа: {response.status_code}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Превышено время ожидания при подключении к API.")
    except requests.exceptions.ConnectionError:
        st.error("Ошибка подключения к API. Пожалуйста, проверьте ваше интернет-соединение.")
    except requests.exceptions.RequestException as e:
        st.error(f"Произошла ошибка при запросе к API: {str(e)}")
    
    st.error("Не удалось получить ответ от API.")
    return None

def fetch_music_details(music_id):
    """Fetch details of generated music using its ID"""
    headers = {
        "Authorization": f"Bearer {SUNO_API_KEY}",
        "Content-Type": "application/json"
    }

    url = f"{BASE_URL}/?ids[0]={music_id}"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error in fetch_music_details: {str(e)}")
        return None

def main():
    st.title("AI Music Generator")
    st.write("Опишите музыку, которую вы хотите сгенерировать, и наш ИИ создаст ее для вас!")

    prompt = st.text_area("Введите ваш промпт для генерации музыки:", 
                          value="Create a cheerful, upbeat song about a sunny day")
    tags = st.text_input("Теги (через запятую):", value="cheerful, upbeat, sunny")
    title = st.text_input("Название трека:", value="Sunny Day Song")
    make_instrumental = st.checkbox("Сделать инструментальной")
    wait_audio = st.checkbox("Ждать генерации аудио", value=True)

    if st.button("Сгенерировать музыку"):
        with st.spinner("Генерация музыки..."):
            result = generate_music(prompt, tags, title, make_instrumental, wait_audio)
            if result:
                st.success("Запрос на генерацию музыки успешно отправлен!")
                st.json(result)

                if wait_audio:
                    if isinstance(result, list) and len(result) > 0:
                        for track in result:
                            st.subheader(f"Трек: {track.get('title', 'Без названия')}")
                            
                            audio_url = track.get('audio_url')
                            if audio_url:
                                st.audio(audio_url, format='audio/wav')
                            else:
                                st.warning("URL аудио не найден для этого трека.")
                            
                            image_url = track.get('image_url')
                            if image_url:
                                st.image(image_url, caption="Обложка трека")
                            
                            lyric = track.get('lyric')
                            if lyric:
                                with st.expander("Показать текст песни"):
                                    st.text(lyric)
                            
                            st.write(f"Модель: {track.get('model_name', 'Не указана')}")
                            st.write(f"Статус: {track.get('status', 'Не указан')}")
                            st.write(f"Создано: {track.get('created_at', 'Не указано')}")
                            
                            st.divider()
                    else:
                        st.warning("Неожиданный формат ответа от API.")
                else:
                    st.info("Музыка генерируется в фоновом режиме. Используйте ID задачи для получения результатов позже.")
                    task_id = result.get('id')
                    if task_id:
                        st.write(f"ID задачи: {task_id}")
                        if st.button("Получить детали генерации"):
                            details = fetch_music_details(task_id)
                            if details:
                                st.json(details)
                            else:
                                st.error("Не удалось получить детали генерации.")
                    else:
                        st.warning("ID задачи не найден в ответе API.")
            else:
                st.error("Не удалось отправить запрос на генерацию музыки. Пожалуйста, попробуйте еще раз позже.")

if __name__ == "__main__":
    main()