import pdfplumber
import streamlit as st
import youtube_dl
from get_results import *
import pandas as pd
from transformers import pipeline
import requests

st.markdown(""" 
<style>
.css-19wwds0.egzxvld0
{
visibility:hidden;
}
</style>
""", unsafe_allow_html=True)

st.title('Textvert - Insights that save time.')
st.subheader('Where would you like to derive your insights from?')

st.sidebar.title("🧐 How can Textvert help?")
st.sidebar.header('🥱 It\'s a 3-step process')
st.sidebar.markdown("""<hr style="height:2px;border:none;color:#945D60;background-color:#945D60;" /> """,
                    unsafe_allow_html=True)
st.sidebar.subheader('👇 Step 1: Choose an insight source')
mode = st.sidebar.selectbox("",
                            ('Media - Audio, Video & YouTube', 'Text - PDFs & Text Input'))
st.sidebar.markdown("""<hr style="height:2px;border:none;color:#945D60;background-color:#945D60;" /> """,
                    unsafe_allow_html=True)

if mode == 'Media - Audio, Video & YouTube':
    st.sidebar.subheader('👇 Step 2: Upload content, hit Submit')
    st.sidebar.markdown("""<hr style="height:2px;border:none;color:#945D60;background-color:#945D60;" /> """,
                        unsafe_allow_html=True)
    st.sidebar.subheader('👇 Step 3: Choose an insight')
    st.sidebar.markdown(":point_right:&nbsp;&nbsp;&nbsp;[**View Chapters & Summaries**](#chapters-and-summaries)",
                        unsafe_allow_html=True)
    st.sidebar.markdown(':page_with_curl:&nbsp;&nbsp;&nbsp;Chapters and Summaries automatically separates your content '
                        'into chapters and summarizes each '
                        'chapter to make knowing your content less time consuming.')
    st.sidebar.markdown(":point_right:&nbsp;&nbsp;&nbsp;[**View Transcribed Text**](#transcribed-text)",
                        unsafe_allow_html=True)
    st.sidebar.markdown(
        ':page_with_curl:&nbsp;&nbsp;&nbsp;Automatically convert your media files to text. Go further by '
        'viewing them in paragraphs along '
        'with clickable timestamps for their start point.')
    st.sidebar.markdown(":point_right:&nbsp;&nbsp;&nbsp;[**View Word/Phrase Highlights**](#word-highlights)",
                        unsafe_allow_html=True)
    st.sidebar.markdown(
        ':page_with_curl:&nbsp;&nbsp;&nbsp;Word/Phrase Highlights picks out particular words and phrases '
        'from your content and lets you '
        'know where in the content they are present with clickable timestamps.')

    if 'status' not in st.session_state:
        st.session_state['status'] = 'submitted'

    if 'start_point' not in st.session_state:
        st.session_state['start_point'] = 0


    def update_start(start_t):
        st.session_state['start_point'] = int(start_t / 1000)


    file_type = st.radio(
        "Select your source",
        ('Video', 'Audio', 'YouTube'))

    # Video File
    if file_type == 'Video':
        def update_endpoint(video_file):
            st.session_state['polling_endpoint'] = upload_to_AssemblyAI(video_file)


        uploaded_video_file = st.file_uploader('Upload your video file here')
        placeholder = st.empty()
        placeholder.video(uploaded_video_file, start_time=st.session_state['start_point'])
        st.button('Submit', on_click=update_endpoint, args=(uploaded_video_file,))

        status = 'submitted'
        while status != 'completed':
            try:
                polling_response = requests.get(st.session_state['polling_endpoint'], headers)
            except KeyError:
                st.info('Please upload a file and click Submit')
                st.stop()
            status = polling_response.json()['status']

            if status == 'completed':

                st.subheader('Transcribed Text')
                paragraph_endpoint = st.session_state['polling_endpoint'] + "/paragraphs"
                paragraph_response = requests.get(paragraph_endpoint, headers)

                paragraphs = paragraph_response.json()['paragraphs']
                paragraphs_df = pd.DataFrame(paragraphs)
                paragraphs_df['start_str'] = paragraphs_df['start'].apply(convertMillis)
                paragraphs_df['end_str'] = paragraphs_df['end'].apply(convertMillis)

                for index, row in paragraphs_df.iterrows():
                    x_numbers = 0
                    st.write(row['text'])
                    st.button(row['start_str'], on_click=update_start, args=(row['start'],), key=x_numbers)
                    x_numbers += 1
                    st.markdown(
                        "[After clicking the timestamp, click here to view your media at the desired point]("
                        "#where-would-you-like-to-derive-your-insights-from)",
                        unsafe_allow_html=True)

                st.subheader('Word Highlights')
                st.markdown(
                    "[After clicking the timestamp, click here to view your media at the desired point]("
                    "#where-would-you-like-to-derive-your-insights-from)",
                    unsafe_allow_html=True)
                word_highlights = polling_response.json()['auto_highlights_result']['results']
                cols = st.columns(3)
                n_buttons = 10
                for res_idx, res in enumerate(word_highlights):
                    text = res['text']
                    timestamps = res['timestamps']
                    col_idx = res_idx % 3
                    with cols[col_idx]:
                        st.write(text)
                        for t in timestamps:
                            start_ms = t['start']
                            ms_start = convertMillis(start_ms)
                            st.button(ms_start, on_click=update_start, args=(start_ms,), key=n_buttons)
                            n_buttons += 1

    # Audio file
    if file_type == 'Audio':
        def update_endpoint(audio_file):
            st.session_state['polling_endpoint'] = upload_to_AssemblyAI(audio_file)


        uploaded_audio_file = st.file_uploader('Upload your video file here')
        st.audio(uploaded_audio_file, start_time=st.session_state['start_point'])
        st.button('Submit', on_click=update_endpoint, args=(uploaded_audio_file,))

        status = 'submitted'
        while status != 'completed':
            try:
                polling_response = requests.get(st.session_state['polling_endpoint'], headers)
            except KeyError:
                st.info('Please upload a file and click Submit')
                st.stop()
            status = polling_response.json()['status']

            if status == 'completed':

                st.subheader('Transcribed Text')
                paragraph_endpoint = st.session_state['polling_endpoint'] + "/paragraphs"
                paragraph_response = requests.get(paragraph_endpoint, headers)

                paragraphs = paragraph_response.json()['paragraphs']
                paragraphs_df = pd.DataFrame(paragraphs)
                paragraphs_df['start_str'] = paragraphs_df['start'].apply(convertMillis)
                paragraphs_df['end_str'] = paragraphs_df['end'].apply(convertMillis)

                for index, row in paragraphs_df.iterrows():
                    j_buttons = 20
                    st.write(row['text'])
                    st.button(row['start_str'], on_click=update_start, args=(row['start'],), key=j_buttons)
                    j_buttons += 1
                    st.markdown(
                        "[After clicking the timestamp, click here to view your media at the desired point]("
                        "#where-would-you-like-to-derive-your-insights-from)",
                        unsafe_allow_html=True)

                st.subheader('Word Highlights')
                st.markdown(
                    "[After clicking the timestamp, click here to view your media at the desired point]("
                    "#where-would-you-like-to-derive-your-insights-from)",
                    unsafe_allow_html=True)
                word_highlights = polling_response.json()['auto_highlights_result']['results']
                cols = st.columns(3)
                k_buttons = 30
                for res_idx, res in enumerate(word_highlights):
                    text = res['text']
                    timestamps = res['timestamps']
                    col_idx = res_idx % 3
                    with cols[col_idx]:
                        st.write(text)
                        for t in timestamps:
                            start_ms = t['start']
                            ms_start = convertMillis(start_ms)
                            st.button(ms_start, on_click=update_start, args=(start_ms,), key=k_buttons)
                            k_buttons += 1

    # YouTube Link
    if file_type == 'YouTube':

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': "./%(id)s.%(ext)s"
        }

        CHUNK_SIZE = 5242880


        def transcribe_from_link(link):
            _id = link.strip()

            def get_vid(_id):
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(_id)

            meta = get_vid(_id)
            save_location = meta['id'] + '.mp3'
            return save_location


        def read_file(filename):
            with open(filename, 'rb') as _file:
                while True:
                    data = _file.read(CHUNK_SIZE)
                    if not data:
                        break
                    yield data


        def update_endpoint(url):
            st.session_state['polling_endpoint'] = upload_to_AssemblyAI(read_file(transcribe_from_link(url)))


        link = st.text_input('Enter any YouTube Link and then click Submit')
        st.button('Submit', on_click=update_endpoint, args=(link,))
        if not link:
            st.info('Please click Submit to ensure your file is processed')
            st.stop()
            st.success('Thank you for inputting a name.')
        st.video(link, start_time=st.session_state['start_point'])

        # if 'polling_endpoint' not in st.session_state:
        # st.session_state['polling_endpoint'] = upload_to_AssemblyAI(read_file(transcribe_from_link(link)))

        status = 'submitted'
        while status != 'completed':
            try:
                polling_response = requests.get(st.session_state['polling_endpoint'], headers)
            except KeyError:
                st.stop()

            status = polling_response.json()['status']

            if status == 'completed':

                st.subheader('Transcribed Text')
                paragraph_endpoint = st.session_state['polling_endpoint'] + "/paragraphs"
                paragraph_response = requests.get(paragraph_endpoint, headers)

                paragraphs = paragraph_response.json()['paragraphs']
                paragraphs_df = pd.DataFrame(paragraphs)
                paragraphs_df['start_str'] = paragraphs_df['start'].apply(convertMillis)
                paragraphs_df['end_str'] = paragraphs_df['end'].apply(convertMillis)

                for index, row in paragraphs_df.iterrows():
                    l_buttons = 40
                    st.write(row['text'])
                    st.button(row['start_str'], on_click=update_start, args=(row['start'],), key=l_buttons)
                    l_buttons += 1
                    st.markdown(
                        "[After clicking the timestamp, click here to view your media at the desired point]("
                        "#where-would-you-like-to-derive-your-insights-from)",
                        unsafe_allow_html=True)

                st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """,
                            unsafe_allow_html=True)

                st.subheader('Word Highlights')
                st.markdown(
                    "[After clicking the timestamp, click here to view your media at the desired point]("
                    "#where-would-you-like-to-derive-your-insights-from)",
                    unsafe_allow_html=True)
                word_highlights = polling_response.json()['auto_highlights_result']['results']
                cols = st.columns(5)
                m_buttons = 50
                for res_idx, res in enumerate(word_highlights):
                    text = res['text']
                    timestamps = res['timestamps']
                    col_idx = res_idx % 5
                    with cols[col_idx]:
                        st.write(text)
                        for t in timestamps:
                            start_ms = t['start']
                            ms_start = convertMillis(start_ms)
                            st.button(ms_start, on_click=update_start, args=(start_ms,), key=m_buttons)
                            m_buttons += 1

else:

    st.sidebar.subheader('👇 Step 3: View Summary')
    st.sidebar.markdown(':page_with_curl:&nbsp;&nbsp;&nbsp;View a summarized version of your file or text within the '
                        'word limits you have set.')

    file_type = st.radio(
        "Select your source",
        ('Type Your Text', 'Upload Text File', 'Website Link'))

    if file_type == 'Type Your Text':

        minimum_words = st.number_input('Enter the minimum number of words for your summary', min_value=30, step=5)
        maximum_words = st.number_input('Enter the maximum number of words for your summary', min_value=120, step=5)
        ARTICLE = st.text_area("Type your text below")
        if not ARTICLE:
            st.info('Please click anywhere or hit enter after entering your link')
            st.stop()

        summarizer = pipeline("summarization")
        max_chunk = 500
        ARTICLE = ARTICLE.replace('.', '.<eos>')
        ARTICLE = ARTICLE.replace('?', '?<eos>')
        ARTICLE = ARTICLE.replace('!', '!<eos>')

        sentences = ARTICLE.split('<eos>')
        current_chunk = 0
        chunks = []
        for sentence in sentences:
            if len(chunks) == current_chunk + 1:
                if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                    chunks[current_chunk].extend(sentence.split(' '))
                else:
                    current_chunk += 1
                    chunks.append(sentence.split(' '))
            else:
                print(current_chunk)
                chunks.append(sentence.split(' '))

        for chunk_id in range(len(chunks)):
            chunks[chunk_id] = ' '.join(chunks[chunk_id])

        res = summarizer(chunks, max_length=maximum_words, min_length=minimum_words, do_sample=False)
        text = ' '.join([summ['summary_text'] for summ in res])
        all_text = text.split('.')
        all_text_final = all_text[:-1]
        summary = '.'.join(all_text_final)

        st.subheader('Your Summary')
        st.write(summary)

    if file_type == 'Website Link':

        st.subheader('Summary Length')
        st.info('We are working on supporting all websites. As a result, the summary may contain information at '
                'the end that is irrelevant.')
        minimum_words = st.number_input('Enter the minimum number of words for your summary', min_value=30, step=5)
        maximum_words = st.number_input('Enter the maximum number of words for your summary', min_value=120, step=5)

        URL = st.text_input('Enter a link below')
        if not URL:
            st.info('Please click anywhere or hit enter after entering your link')
            st.stop()

        summarizer = pipeline("summarization")
        r = requests.get(URL)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.find_all(['h1', 'p'])
        text = [result.text for result in results]
        ARTICLE = ' '.join(text)

        max_chunk = 500
        ARTICLE = ARTICLE.replace('.', '.<eos>')
        ARTICLE = ARTICLE.replace('?', '?<eos>')
        ARTICLE = ARTICLE.replace('!', '!<eos>')

        sentences = ARTICLE.split('<eos>')
        current_chunk = 0
        chunks = []
        for sentence in sentences:
            if len(chunks) == current_chunk + 1:
                if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                    chunks[current_chunk].extend(sentence.split(' '))
                else:
                    current_chunk += 1
                    chunks.append(sentence.split(' '))
            else:
                print(current_chunk)
                chunks.append(sentence.split(' '))

        for chunk_id in range(len(chunks)):
            chunks[chunk_id] = ' '.join(chunks[chunk_id])

        res = summarizer(chunks, max_length=maximum_words, min_length=minimum_words, do_sample=False)
        text = ' '.join([summ['summary_text'] for summ in res])
        all_text = text.split('.')
        all_text_final = all_text[:-1]
        summary = '.'.join(all_text_final)

        st.subheader('Your Summary')
        st.write(summary)

    if file_type == 'Upload Text File':

        minimum_words = st.number_input('Enter the minimum number of words for your summary', min_value=30, step=5)
        maximum_words = st.number_input('Enter the maximum number of words for your summary', min_value=120, step=5)
        page_number = st.number_input('Enter the page number you would like a summary from', min_value=0, step=1)

        uploaded_file = st.file_uploader('Upload your file below')
        if not uploaded_file:
            st.stop()
        pdf = pdfplumber.open(uploaded_file)
        page = pdf.pages[page_number]
        ARTICLE = page.extract_text()

        summarizer = pipeline("summarization")
        max_chunk = 500
        ARTICLE = ARTICLE.replace('.', '.<eos>')
        ARTICLE = ARTICLE.replace('?', '?<eos>')
        ARTICLE = ARTICLE.replace('!', '!<eos>')

        sentences = ARTICLE.split('<eos>')
        current_chunk = 0
        chunks = []
        for sentence in sentences:
            if len(chunks) == current_chunk + 1:
                if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                    chunks[current_chunk].extend(sentence.split(' '))
                else:
                    current_chunk += 1
                    chunks.append(sentence.split(' '))
            else:
                print(current_chunk)
                chunks.append(sentence.split(' '))

        for chunk_id in range(len(chunks)):
            chunks[chunk_id] = ' '.join(chunks[chunk_id])

        res = summarizer(chunks, max_length=maximum_words, min_length=minimum_words, do_sample=False)
        text = ' '.join([summ['summary_text'] for summ in res])
        all_text = text.split('.')
        all_text_final = all_text[:-1]
        summary = '.'.join(all_text_final)

        st.subheader('Your Summary')
        st.write(summary)
