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

# Настройка стиля страницы
st.set_page_config(page_title="AI Composer", layout="wide", initial_sidebar_state="collapsed")

# Добавление кастомного CSS для полностью неонового стиля
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

    .stApp {
        background-color: #000000;
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
    }
    
    h1, h2, h3 {
        color: #0ff;
        text-shadow: 0 0 5px #0ff, 0 0 10px #0ff, 0 0 15px #0ff, 0 0 20px #0ff;
    }
    
    p, label, .stMarkdown, .stSelectbox>div>div>div {
        color: #f0f;
        text-shadow: 0 0 5px #f0f, 0 0 10px #f0f;
    }
    
    .stButton>button {
        background-color: #000;
        color: #0f0;
        font-weight: bold;
        border: 2px solid #0f0;
        border-radius: 20px;
        padding: 10px 20px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        box-shadow: 0 0 5px #0f0, 0 0 10px #0f0;
    }
    
    .stButton>button:hover {
        background-color: #0f0;
        color: #000;
        box-shadow: 0 0 10px #0f0, 0 0 20px #0f0, 0 0 30px #0f0;
    }
    
    .stTextInput > label, .stSelectbox > label, .stSlider > label {
        font-size: 120%;
        font-weight: bold;
        color: #0ff;
        text-shadow: 0 0 5px #0ff, 0 0 10px #0ff;
        background: none;
        border: none;
        padding: 5px 10px;
    }
    
    [data-baseweb="base-input"], [data-baseweb="select"], .stSlider > div > div > div {
        background: linear-gradient(to bottom, #000 0%, #111 100%);
        border: 2px solid #ff0;
        border-radius: 5px;
    }
    
    .stTextInput > div > div > input, .stSelectbox > div > div > select, .stSlider > div > div > div > div {
        color: #ff0;
        text-shadow: 0 0 5px #ff0, 0 0 10px #ff0;
        font-weight: bold;
        font-size: 110%;
    }
    
    .stTextInput > div > div > input:focus, .stSelectbox > div > div > select:focus {
        box-shadow: 0 0 10px #ff0, 0 0 20px #ff0;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #ff0;
        opacity: 0.5;
        text-shadow: 0 0 5px #ff0;
    }
    
    .stExpander {
        background-color: #111;
        border: 2px solid #0ff;
        border-radius: 10px;
        box-shadow: 0 0 10px #0ff;
    }
    
    .stAudio {
        background-color: #111;
        border: 2px solid #f0f;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 0 10px #f0f;
    }
    
    .stCheckbox > label > span {
        color: #0f0;
        text-shadow: 0 0 5px #0f0, 0 0 10px #0f0;
    }
    
    /* Неоновая анимация для заголовка */
    @keyframes neon-flicker {
        0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {
            text-shadow: 0 0 5px #0ff, 0 0 10px #0ff, 0 0 15px #0ff, 0 0 20px #0ff;
        }
        20%, 24%, 55% {
            text-shadow: none;
        }
    }
    
    h1 {
        animation: neon-flicker 2s infinite alternate;
    }

    /* Стиль для ползунка */
    .stSlider input[type="range"] {
        background-color: #f0f;
    }
    .stSlider .stSlider > div > div > div > div:first-child {
        background-color: #0ff;
    }
</style>
""", unsafe_allow_html=True)

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
        with st.spinner("Создаем вашу уникальную музыку..."):
            response = requests.post(url, json=payload, headers=headers)
        
        response.raise_for_status()
        st.success("Ваша музыка готова!")
        result = response.json()
        with st.expander("Просмотреть ответ API"):
            st.json(result)
        return result
    except requests.exceptions.RequestException as e:
        st.error(f"Упс! Что-то пошло не так: {str(e)}")
    
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
        st.markdown(f"**ID:** {track.get('id', 'Не указан')}")
        st.markdown(f"**Статус:** {track.get('status', 'Не указан')}")
        st.markdown(f"**Модель:** {track.get('model_name', 'Не указана')}")
        st.markdown(f"**Создано:** {track.get('created_at', 'Не указано')}")
        
        lyrics = track.get('lyric')
        if lyrics:
            with st.expander("Показать текст песни"):
                st.markdown(lyrics)
        
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
    st.title("AI Composer")
    st.markdown("Создайте уникальную музыку с помощью искусственного интеллекта!")

    base_prompt = st.text_area(
        "Опишите музыку вашей мечты:", 
        value="", 
        height=100,
        placeholder="Например: Создай футуристическую электронную композицию с элементами синтвейва"
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
    
    generate_button = st.button("Создать музыку", type="primary")

    if generate_button:
        if not base_prompt.strip():
            st.error("Пожалуйста, опишите желаемую музыку.")
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
            st.error("Не удалось создать музыку. Попробуйте изменить параметры и попробовать снова.")

    if 'tracks' in st.session_state:
        st.subheader("Ваши уникальные треки:")
        
        for i, track in enumerate(st.session_state['tracks']):
            display_track_info(track, i)

if __name__ == "__main__":
    main()