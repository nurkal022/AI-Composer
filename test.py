import streamlit as st
import requests
import os
from dotenv import load_dotenv
from io import BytesIO

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение API ключа из переменных окружения
SUNO_API_KEY = os.getenv('SUNO_API_KEY')

BASE_URL = "https://api.aimlapi.com"

def generate_music_and_text(prompt, make_instrumental=False, wait_audio=True):
    """Генерация музыки и текста с использованием API Suno v3.5"""
    url = f"{BASE_URL}/generate"
    headers = {
        "Authorization": f"Bearer {SUNO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "make_instrumental": make_instrumental,
        "wait_audio": wait_audio
    }

    with st.expander("Просмотреть детали запроса"):
        st.json(payload)

    try:
        with st.spinner("Генерация музыки и текста..."):
            response = requests.post(url, json=payload, headers=headers)
        
        response.raise_for_status()
        st.success("Запрос на генерацию музыки и текста успешно выполнен!")
        result = response.json()
        with st.expander("Просмотреть ответ API"):
            st.json(result)
        return result
    except requests.exceptions.RequestException as e:
        st.error(f"Произошла ошибка при запросе к API: {str(e)}")
    
    return None

@st.cache_data
def download_audio(url):
    """Скачивание аудио файла с кэшированием"""
    response = requests.get(url)
    return BytesIO(response.content)

def display_track_info(track, index):
    """Отображение информации о треке"""
    st.subheader(f"Трек {index+1}: {track.get('title', 'Без названия')}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        image_url = track.get('image_url')
        if image_url:
            st.image(image_url, caption="Обложка трека", use_column_width=True)
    
    with col2:
        st.write(f"ID: {track.get('id', 'Не указан')}")
        st.write(f"Статус: {track.get('status', 'Не указан')}")
        st.write(f"Модель: {track.get('model_name', 'Не указана')}")
        st.write(f"Создано: {track.get('created_at', 'Не указано')}")
        
        lyrics = track.get('lyric')
        if lyrics:
            with st.expander("Показать текст песни"):
                st.text(lyrics)
        
        audio_url = track.get('audio_url')
        if audio_url:
            st.audio(audio_url, format='audio/wav')
            
            audio_filename = f"generated_track_{index+1}.wav"
            audio_file = download_audio(audio_url)
            st.download_button(
                label="Скачать трек",
                data=audio_file,
                file_name=audio_filename,
                mime="audio/wav"
            )
        else:
            st.warning("URL аудио не найден для этого трека.")
        
        if track.get('error_message'):
            st.error(f"Ошибка: {track['error_message']}")
    
    st.markdown("---")  # Разделитель между треками

def generate_prompt(base_prompt, genre, mood, voice_gender, additional_params):
    """Генерация полного промпта на основе параметров"""
    prompt_parts = [base_prompt.strip()]
    
    if genre:
        prompt_parts.append(f"Genre: {genre}")
    if mood:
        prompt_parts.append(f"Mood: {mood}")
    if voice_gender:
        prompt_parts.append(f"Voice: {voice_gender}")
    
    for param, value in additional_params.items():
        if value:
            prompt_parts.append(f"{param}: {value}")
    
    return ". ".join(prompt_parts)

def main():
    st.set_page_config(page_title="AI Music Generator", layout="wide")
    
    st.title("AI Music Generator")
    st.write("Опишите музыку, которую вы хотите сгенерировать, и наш ИИ создаст ее для вас!")

    base_prompt = st.text_area(
        "Введите базовое описание желаемой музыки:", 
        value="", 
        height=100,
        placeholder="Например: Create a relaxing ambient music track with piano and strings"
    )
    
    with st.expander("Дополнительные параметры"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            genre = st.selectbox("Жанр", ["", "Pop", "Rock", "Classical", "Jazz", "Electronic", "Hip Hop", "Country", "R&B", "Folk", "Reggae", "Blues"])
            mood = st.selectbox("Настроение", ["", "Happy", "Sad", "Energetic", "Calm", "Romantic", "Angry", "Mysterious", "Nostalgic", "Uplifting"])
            voice_gender = st.selectbox("Пол голоса", ["", "Male", "Female", "Neutral"])
        
        with col2:
            tempo = st.slider("Темп (BPM)", 60, 200, 120)
            instruments = st.text_input("Дополнительные инструменты")
            era = st.selectbox("Эра", ["", "60s", "70s", "80s", "90s", "2000s", "2010s", "Modern", "Futuristic"])
        
        with col3:
            language = st.selectbox("Язык текста", ["", "English", "Spanish", "French", "German", "Italian", "Japanese", "Korean", "Russian", "Chinese", "Arabic"])
            duration = st.slider("Длительность (секунды)", 30, 300, 180)
            key = st.selectbox("Тональность", ["", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])
    
    make_instrumental = st.checkbox("Сделать инструментальной", value=False)
    wait_audio = st.checkbox("Ждать генерации аудио", value=True)
    
    additional_params = {
        "Instruments": instruments,
        "Era": era,
        "Language": language,
        "Duration": f"{duration} seconds",
        "Key": key,
        "Tempo": f"{tempo} BPM"
    }
    
    full_prompt = generate_prompt(base_prompt, genre, mood, voice_gender, additional_params)
    
    generate_button = st.button("Сгенерировать музыку", type="primary")

    if generate_button:
        if not base_prompt.strip():
            st.error("Базовое описание не может быть пустым. Пожалуйста, введите описание желаемой музыки.")
            return
        
        result = generate_music_and_text(full_prompt, make_instrumental, wait_audio)
        
        if result:
            if isinstance(result, list):
                st.session_state['tracks'] = result
            elif isinstance(result, dict):
                st.session_state['tracks'] = [result]
            else:
                st.warning("Неожиданный формат ответа от API.")
                return
        else:
            st.error("Не удалось получить результаты генерации музыки. Пожалуйста, проверьте введенные данные и попробуйте еще раз.")

    if 'tracks' in st.session_state:
        st.subheader("Сгенерированные треки:")
        
        for i, track in enumerate(st.session_state['tracks']):
            display_track_info(track, i)

if __name__ == "__main__":
    main()