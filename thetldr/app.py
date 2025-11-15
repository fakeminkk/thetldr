from flask import Flask, render_template, jsonify, request
import os
import re
from pathlib import Path

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

BASE_DIR = Path(__file__).parent

@app.route('/')
def index():
    """Main page - displays photos from fav_photo folder"""
    return render_template('index.html', page='photos', folder_path='fav_photo', is_home=True)

@app.route('/photos')
@app.route('/photos/<path:subfolder>')
def photos(subfolder=None):
    """Photos page - displays photos from photos folder or subfolder"""
    if subfolder:
        folder_path = f'photos/{subfolder}'
        # Extract folder name for breadcrumb (last part of path)
        folder_name = subfolder.split('/')[-1] if '/' in subfolder else subfolder
    else:
        folder_path = 'photos'
        folder_name = ''
    
    # Get source photo name from query parameter
    source_photo = request.args.get('source', '')
    
    return render_template('photos.html', page='photos', folder_path=folder_path, subfolder=subfolder or '', folder_name=folder_name, source_photo=source_photo)

@app.route('/videos')
def videos():
    """Videos page"""
    return render_template('videos.html', page='videos')

@app.route('/music')
def music():
    """Music page"""
    return render_template('music.html', page='music')

@app.route('/bio')
def bio():
    """Bio page"""
    bio_path = BASE_DIR / 'bio.html'
    bio_content = ''
    if bio_path.exists():
        with open(bio_path, 'r', encoding='utf-8') as f:
            bio_content = f.read()
    return render_template('bio.html', page='bio', bio_content=bio_content)

@app.route('/api/photos/<path:folder_path>')
def get_photos(folder_path):
    """API endpoint to get list of photos from a folder"""
    folder = BASE_DIR / 'static' / folder_path
    
    if not folder.exists() or not folder.is_dir():
        return jsonify({'photos': []})
    
    # Supported image formats
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    
    photos = []
    for file in sorted(folder.iterdir()):
        if file.is_file() and file.suffix.lower() in image_extensions:
            photos.append({
                'filename': file.name,
                'path': f'/static/{folder_path}/{file.name}',
                'full_path': str(file)
            })
    
    return jsonify({'photos': photos})

@app.route('/api/videos')
def get_videos():
    """API endpoint to get list of videos with covers and YouTube links"""
    videos_folder = BASE_DIR / 'static' / 'videos'
    
    if not videos_folder.exists():
        return jsonify({'videos': []})
    
    def extract_video_id(url):
        """Extract YouTube video ID from various URL formats"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_youtube_thumbnail(video_id):
        """Get YouTube thumbnail URL with fallback"""
        if not video_id:
            return ''
        # Try maxresdefault first, fallback to hqdefault
        return {
            'primary': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
            'fallback': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
        }
    
    videos = []
    # Look for .youtube files
    for item in sorted(videos_folder.iterdir()):
        if item.is_file() and item.suffix.lower() == '.youtube':
            with open(item, 'r', encoding='utf-8') as f:
                youtube_url = f.read().strip()
            
            if youtube_url:
                video_id = extract_video_id(youtube_url)
                thumbnails = get_youtube_thumbnail(video_id)
                
                videos.append({
                    'cover': thumbnails['primary'],
                    'cover_fallback': thumbnails['fallback'],
                    'youtube_url': youtube_url,
                    'title': item.stem
                })
    
    return jsonify({'videos': videos})

@app.route('/api/music')
def get_music():
    """API endpoint to get list of music with covers and YouTube links"""
    music_folder = BASE_DIR / 'static' / 'music'
    
    if not music_folder.exists():
        return jsonify({'tracks': []})
    
    def extract_video_id(url):
        """Extract YouTube video ID from various URL formats"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_youtube_thumbnail(video_id):
        """Get YouTube thumbnail URL with fallback"""
        if not video_id:
            return ''
        # Try maxresdefault first, fallback to hqdefault
        return {
            'primary': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
            'fallback': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
        }
    
    tracks = []
    # Look for .youtube files
    for item in sorted(music_folder.iterdir()):
        if item.is_file() and item.suffix.lower() == '.youtube':
            with open(item, 'r', encoding='utf-8') as f:
                youtube_url = f.read().strip()
            
            if youtube_url:
                video_id = extract_video_id(youtube_url)
                thumbnails = get_youtube_thumbnail(video_id)
                
                tracks.append({
                    'cover': thumbnails['primary'],
                    'cover_fallback': thumbnails['fallback'],
                    'youtube_url': youtube_url,
                    'title': item.stem
                })
    
    return jsonify({'tracks': tracks})

@app.route('/api/fav-photo-links')
def get_fav_photo_links():
    """Get mapping of fav_photo images to their destination folders"""
    fav_photo_folder = BASE_DIR / 'static' / 'fav_photo'
    links_file = BASE_DIR / 'static' / 'fav_photo' / 'links.txt'
    
    links = {}
    if links_file.exists():
        with open(links_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    photo_name, dest_folder = line.split(':', 1)
                    links[photo_name.strip()] = dest_folder.strip()
    
    # If no links file, check for folders in photos that match image names
    # First, try to find exact filename matches in subfolders
    photos_folder = BASE_DIR / 'static' / 'photos'
    if photos_folder.exists():
        for fav_img in fav_photo_folder.iterdir():
            if fav_img.is_file() and fav_img.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}:
                # Check if this photo is not already in links
                if fav_img.name not in links:
                    # Look for this exact filename in subfolders
                    for subfolder in photos_folder.iterdir():
                        if subfolder.is_dir():
                            photo_in_subfolder = subfolder / fav_img.name
                            if photo_in_subfolder.exists():
                                links[fav_img.name] = subfolder.name
                                break
                    
                    # If still no match, try name-based matching
                    if fav_img.name not in links:
                        for subfolder in photos_folder.iterdir():
                            if subfolder.is_dir():
                                if fav_img.stem.lower() in subfolder.name.lower() or subfolder.name.lower() in fav_img.stem.lower():
                                    links[fav_img.name] = subfolder.name
                                    break
    
    return jsonify({'links': links})

# Flask automatically serves static files from 'static' folder
# No custom route needed

if __name__ == '__main__':
    # Create necessary folders
    folders = ['static/photos', 'static/videos', 'static/music', 'static/fav_photo']
    for folder in folders:
        os.makedirs(BASE_DIR / folder, exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=8080)

