import requests
import base64
import json
import urllib

from GUI.data_structure.Text import Text

# ! Add your API Key here
API_KEY = 
SECRET_KEY = 

def baidu_ocr_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials", 
        "client_id": API_KEY, 
        "client_secret": SECRET_KEY
    }
    return str(requests.post(url, params=params).json().get("access_token"))

def get_file_content_as_base64(path, urlencoded=False):
    """
    Get image file as base64 format
    :param path: the path of the image file
    :param urlencoded: whether urlencoded 
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content

def ocr_detection(img_path, language = 'ENG'): # CHN_ENG or ENG
    #start = time.perf_counter()
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general?access_token=" + baidu_ocr_access_token()
    
    img_base64 = get_file_content_as_base64(img_path, urlencoded=True)
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
    payload = 'image='+img_base64
    payload += '&detect_direction=false'
    payload += '&language_type=' + language
    payload += '&vertexes_location=false'
    payload += '&paragraph=false'
    payload += '&probability=false'
    response = requests.request("POST", url, headers=headers, data=payload)
    # print('*** Text Detection Time Taken:%.3fs ***' % (time.perf_counter() - start))
    if 'words_result' not in response.json():
        raise Exception(response.json())
    ocr_result = response.json()['words_result']

    # convert ocr result to unified format
    texts = []
    if ocr_result is not None:
        for r in ocr_result:
            loc = r['location']
            location = {'left': loc['left'], 'top': loc['top'],
                        'right': loc['left']+loc['width'], 'bottom': loc['top']+loc['height']}
            texts.append(Text(words=r['words'], location=location))
            #print(r['words'], location)
    return texts