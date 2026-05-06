import hashlib
import os
import re
import ssl
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

MIME_TO_EXT = {
        'image/jpeg': 'jpg',
        'image/jpg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'image/webp': 'webp',
        'image/svg+xml': 'svg',
        'image/bmp': 'bmp',
        }

HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }

ssl._create_default_https_context = ssl._create_unverified_context


def sanitize_filename(filename):
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    return filename[:255]


def extract_image_sources(html):
    img_tags = re.findall(r'<img\s+[^>]*>', html, re.IGNORECASE)
    sources = []

    for tag in img_tags:
        for attr in ['data-src', 'src', 'data-original']:
            match = re.search(rf'{attr}=["\'](.*?)["\']', tag, re.IGNORECASE)
            if match and not match.group(1).startswith('data:'):
                sources.append(match.group(1))
                break
    return sources


def extract_page_title(html):
    match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    if match:
        title = match.group(1).strip()
        title = re.sub(r'\s+', ' ', title)
        return title[:100]
    return None


def normalize_url(url):
    url = url.strip()
    if re.match(r'^https?://', url, re.IGNORECASE):
        return url
    if url.startswith('//'):
        return 'https:' + url
    return 'https://' + url


class ImageDownloader:
    def __init__(self):
        self.base_dir = os.path.join(os.path.expanduser("~"), "Desktop", "0000图片下载")
        os.makedirs(self.base_dir, exist_ok=True)

    def get_download_dir(self):
        return self.base_dir

    def download_images(self, url, progress_callback=None):
        url = normalize_url(url)
        image_urls = []
        page_title = None

        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=10) as response:
                content_type = response.info().get('Content-Type', '').split(';')[0].lower()
                base_url = response.url

                if 'text/html' in content_type:
                    html = response.read().decode('utf-8', errors='ignore')
                    page_title = extract_page_title(html)

                    for src in extract_image_sources(html):
                        if src.startswith('//'):
                            src = f'https:{src}'
                        elif src.startswith('/'):
                            parsed = urlparse(base_url)
                            src = f"{parsed.scheme}://{parsed.netloc}{src}"
                        elif 'mmbiz.' in src and not src.startswith(('http:', 'https:')):
                            src = f'https:{src}' if src.startswith('//') else f'https://{src}'

                        absolute_url = urljoin(base_url, src)
                        image_urls.append(absolute_url)

                elif content_type.startswith('image/'):
                    image_urls.append(base_url)
                else:
                    return {
                            'success': False,
                            'message': f"跳过非媒体内容：{url}"
                            }

        except Exception as e:
            return {
                    'success': False,
                    'message': f"处理链接失败: {str(e)}"
                    }

        total = len(image_urls)
        if total == 0:
            return {
                    'success': False,
                    'message': "未找到任何图片"
                    }

        if page_title:
            folder_name = sanitize_filename(page_title)
        else:
            folder_name = urlparse(url).netloc or f"page_{hashlib.md5(url.encode()).hexdigest()[:8]}"

        download_dir = os.path.join(self.base_dir, folder_name)
        os.makedirs(download_dir, exist_ok=True)

        success_count = 0
        errors = []

        for i, img_url in enumerate(image_urls, 1):
            try:
                headers = HEADERS.copy()
                headers['Referer'] = urlparse(img_url).scheme + '://' + urlparse(img_url).netloc

                req = Request(img_url, headers=headers)
                with urlopen(req, timeout=15) as response:
                    content_type = response.info().get('Content-Type', '').split(';')[0].lower()
                    ext = MIME_TO_EXT.get(content_type)

                    if not ext:
                        parsed = urlparse(img_url)
                        file_ext = os.path.splitext(parsed.path)[1][1:].lower()
                        ext = file_ext if file_ext in MIME_TO_EXT.values() else 'bin'

                    url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
                    filename = sanitize_filename(os.path.basename(urlparse(img_url).path)) or f'img_{url_hash}'
                    root = os.path.splitext(filename)[0]
                    base_name = f"{root}.{ext}"

                    save_path = os.path.join(download_dir, base_name)
                    counter = 1
                    while os.path.exists(save_path):
                        base_name = f"{root}_{counter}.{ext}"
                        save_path = os.path.join(download_dir, base_name)
                        counter += 1

                    with open(save_path, 'wb') as f:
                        while True:
                            chunk = response.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)

                    success_count += 1
                    if progress_callback:
                        progress_callback(i, total, success_count)

            except Exception as e:
                errors.append(f"下载失败 [{i}/{total}]: {str(e)[:50]}")
                if progress_callback:
                    progress_callback(i, total, success_count)

        result = {
                'success': True,
                'total': total,
                'success_count': success_count,
                'download_dir': download_dir,
                'url': url,
                'errors': errors
                }
        return result
