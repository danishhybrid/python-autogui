import requests
from bs4 import BeautifulSoup
import moviepy.editor as mp
from flask import Flask, request, redirect, render_template
from pytube import YouTube

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'search' in request.form:
            query = request.form['query']
            videos = search_videos(query)
            return render_template('search_results.html', videos=videos)
        elif 'url_1' in request.form:
            url_1 = request.form['url_1']
            url_2 = request.form['url_2']
            save_path = request.form['save_path']
            file_type = request.form['file_type']
            quality = request.form['quality']
            download_and_combine_videos(url_1, url_2, save_path, file_type, quality)
            return redirect('/')
    return render_template('index.html')

def search_videos(query):
    results = []
    response = requests.get(f'https://www.youtube.com/results?search_query={query}')
    soup = BeautifulSoup(response.text, 'html.parser')
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        results.append({'title': vid['title'], 'url': f'https://www.youtube.com{vid["href"]}'})
    return results

def download_and_combine_videos(url_1, url_2, save_path, file_type, quality):
    video_1 = YouTube(url_1)
    video_2 = YouTube(url_2)

    video_1.streams.filter(file_extension=file_type, res=quality).first().download(save_path)
    video_2.streams.filter(file_extension=file_type, res=quality).first().download(save_path)

    video_1_clip = mp.VideoFileClip(f'{save_path}/{video_1.title}.{file_type}')
    video_2_clip = mp.VideoFileClip(f'{save_path}/{video_2.title}.{file_type}')

    final_video = mp.CompositeVideoClip([video_1_clip.set_pos(('left', 'top')), video_2_clip.set_pos(('left', 'bottom'))])
    final_video.write_videofile(f'{save_path}/{video_1.title}_and_{video_2.title}.{file_type}')

if __name__ == '__main__':
    app.run(debug=True)
