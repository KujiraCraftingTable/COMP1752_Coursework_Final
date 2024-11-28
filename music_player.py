import os
import googleapiclient.discovery
import vlc
import yt_dlp
import time

class MusicPlayer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = self.api_key)
        self.instance = vlc.Instance("--no-video")
        self.player = self.instance.media_player_new()
        self.current_index = 0
        self.video_list = []
    
    #load the Youtube playlist through provided Youtube playlist ID 
    def load_playlist(self, playlist_id):
        self.video_list = self.get_video_info(playlist_id)
    
    #start playing the first song in playlist
    def play_current_video(self):
        if self.video_list:
            title, video_id = self.video_list[self.current_index]
            stream_url = self.get_stream_url(video_id)
            print(f"Playing: {title}")
            self.play_video(stream_url)

    #get needed info of the song 
    def get_video_info(self, playlist_id):
        request = self.youtube.playlistItems().list(
            part="snippet",
            playlistId = playlist_id,
            maxResults = 300
        )
        response = request.execute()
        video_info = [(item["snippet"]["title"], item["snippet"]["resourceId"]["videoId"]) 
                  for item in response["items"]]        
        return video_info

    #get video url
    def get_stream_url(self, video_id):
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'format': 'bestaudio/best',  
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download = False)
            return info_dict['url']

    #play video
    def play_video(self, video_url):
        media = self.instance.media_new(video_url)
        self.player.set_media(media)
        self.player.play()
    
    #play/pause current song  
    def pause(self):
        if self.player.is_playing():
            self.player.pause()  
        else:
            self.player.play()
    
    #move to the next song
    def next_song(self):
        if self.video_list:
            self.current_index = (self.current_index + 1) % len(self.video_list)
            title, video_id = self.video_list[self.current_index]
            stream_url = self.get_stream_url(video_id)
            print(f"Playing Next Song: {title}")
            self.play_video(stream_url)
    
    #back to the previous song
    def previous_song(self):
        if self.video_list:
            self.current_index = (self.current_index - 1) % len(self.video_list)
            title, video_id = self.video_list[self.current_index]
            stream_url = self.get_stream_url(video_id)
            print(f"Playing Previous Song: {title}")
            self.play_video(stream_url)

    #run 
    def run(self, playlist_id):
        self.load_playlist(playlist_id)
        self.play_current_video()
        global current_title
        current_title = self.video_list[self.current_index][0]  

        while True:
            state = self.player.get_state()
            #skip to the next song if the player is not playing
            if state in [vlc.State.Ended, vlc.State.Stopped, vlc.State.Error]:
                time.sleep(1)     
                self.current_index = (self.current_index + 1) % len(self.video_list)
                current_title = self.video_list[self.current_index][0] 
                self.play_current_video()
            elif state == vlc.State.Playing:
                time.sleep(1)