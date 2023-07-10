import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import ImageTk, Image
from io import BytesIO
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(dotenv_path="./spotify_keys.env")

album_info = []  # Global variable to store album information

def search_artist_albums(event=None):
    global album_info  # Declare album_info as global

    artist_name = artist_entry.get()

    # Authenticate your application (replace with your own credentials)
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    try:
        # Search for the artist
        results = sp.search(q='artist:' + artist_name, type='artist')
        artist_id = results['artists']['items'][0]['id']  # Assuming the first result is the desired artist

        # Get the artist's albums
        albums = sp.artist_albums(artist_id, album_type='album')
        album_info = []
        for album in albums['items']:
            album_name = album['name']
            album_release_date = album['release_date']
            album_artwork_url = album['images'][0]['url'] if album['images'] else None
            album_tracks = []
            tracks = sp.album_tracks(album['id'])
            for track in tracks['items']:
                album_tracks.append(track['name'])

            album_info.append({'name': album_name, 'release_date': album_release_date, 'artwork_url': album_artwork_url, 'tracks': album_tracks})

        if len(album_info) > 0:
            # Clear previous album display
            for child in album_info_frame.winfo_children():
                child.destroy()

            # Display album information
            for i, album in enumerate(album_info):
                album_frame = ttk.Frame(album_info_frame)
                album_frame.pack(pady=5)

                album_label = ttk.Label(album_frame, text=f'Album: {album["name"]}')
                album_label.pack(side=tk.LEFT, padx=5)
                album_label.bind('<Button-1>', lambda e, album=album, sp=sp: show_album_info(album, sp))

                ttk.Label(album_frame, text=f'Release Date: {album["release_date"]}').pack(side=tk.LEFT)

        else:
            messagebox.showinfo('No Albums', 'No albums found for the given artist.')

    except IndexError:
        messagebox.showinfo('Invalid Artist', 'Artist not found. Please enter a valid artist name.')



def show_album_info(album, sp):
    album_window = tk.Toplevel(window)
    album_window.title(f'Album: {album["name"]}')
    
    # Set the default size of the window
    album_window.geometry("400x400")    

    ttk.Label(album_window, text=f'Album: {album["name"]}').pack(pady=35)
    ttk.Label(album_window, text=f'Release Date: {album["release_date"]}').pack()

    if album["artwork_url"]:
        response = sp._get(album["artwork_url"])
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((200, 200), Image.ANTIALIAS)
        photo_image = ImageTk.PhotoImage(img)
        album_artwork_label = ttk.Label(album_window, image=photo_image)
        album_artwork_label.image = photo_image
        album_artwork_label.pack(pady=10)

    tracklist_label = ttk.Label(album_window, text='Tracklist:')
    tracklist_label.pack()

    # Determine the height of the tracklist text widget based on the number of tracks
    tracklist_height = min(10, len(album["tracks"]))

    tracklist_text = tk.Text(album_window, height=tracklist_height, width=40)
    tracklist_text.pack()
    tracklist_text.insert(tk.END, '\n'.join(album["tracks"]))
    tracklist_text.configure(state='disabled')


# Create the Tkinter window
window = tk.Tk()
window.title('Spotify Album Scraper')

# Set the window size
window.geometry('500x500')

# Artist search label and entry
artist_label = ttk.Label(window, text='Artist Name:')
artist_label.pack(pady=10)
artist_entry = ttk.Entry(window, width=30)
artist_entry.pack()

# Bind the <Return> key event to the search function
artist_entry.bind('<Return>', search_artist_albums)

# Search button
search_button = ttk.Button(window, text='Search', command=search_artist_albums)
search_button.pack(pady=5)

# Album info frame
album_info_frame = ttk.Frame(window)
album_info_frame.pack(pady=10)

# Scrollbar for album info frame
scrollbar = ttk.Scrollbar(album_info_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Album info canvas
album_info_canvas = tk.Canvas(album_info_frame, yscrollcommand=scrollbar.set)
album_info_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=album_info_canvas.yview)

# Configure the album info canvas to scroll with the mouse wheel
album_info_canvas.bind_all('<MouseWheel>', lambda event: album_info_canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units'))

# Create a frame inside the canvas to hold the album info widgets
album_info_inner_frame = ttk.Frame(album_info_canvas)
album_info_canvas.create_window(0, 0, window=album_info_inner_frame, anchor=tk.NW)

# Configure the album info frame to expand with the window
album_info_inner_frame.bind('<Configure>', lambda event: album_info_canvas.configure(scrollregion=album_info_canvas.bbox('all')))

# Set a minimum size for the album info frame
album_info_inner_frame.bind('<Configure>', lambda event: album_info_canvas.itemconfigure(album_info_canvas.create_rectangle(album_info_canvas.winfo_width(), album_info_canvas.winfo_height()), width=0))

# Run the Tkinter event loop
window.mainloop()

