# -*- coding: utf-8 -*-
import json
import os.path
import urllib.request
import urllib.error
import time
import cv2
from tqdm import tqdm,trange
http_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
key = "-Eg-zFh1teip83A1gCdYjCO28WhBpK-7"
secret = "zDZnldNJdh67azyidk_luUQUGee9uAb2"
filepath = r"F:\Data\137\LuCheng\Projects\test\2.png"

def get_ret(img):
    data = []
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
    data.append(key)
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
    data.append(secret)
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
    data.append('Content-Type: %s\r\n' % 'application/octet-stream')
    data.append(img)
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_landmark')
    data.append('0')
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_attributes')
    data.append("age,gender,emotion,beauty")
    data.append('--%s--\r\n' % boundary)
    for i, d in enumerate(data):
        if isinstance(d, str):
            data[i] = d.encode('utf-8')

    http_body = b'\r\n'.join(data)

    # build http request
    req = urllib.request.Request(url=http_url, data=http_body)

    # header
    req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)

    try:
        # post data to server
        resp = urllib.request.urlopen(req, timeout=5)
        # get response
        qrcont = resp.read()
        # if you want to load as json, you should decode first,
        # for example: json.loads(qrount.decode('utf-8'))
        ret = json.loads(qrcont.decode('utf-8'))

        # img = cv2.
        # draw_on_picture()
    except urllib.error.HTTPError as e:
        print(e.read().decode('utf-8'))
    return ret


def draw_on_picture(img, ret):
    for face in ret['faces']:
        texts = []
        rectangle = face['face_rectangle']
        start = (rectangle['left'], rectangle['top'])
        end = (rectangle['left'] + rectangle['width'], rectangle['top'] + rectangle['height'])
        cv2.rectangle(img, start, end, (255, 0, 0), 2)
        gender = face['attributes']['gender']['value']
        age = str(face['attributes']['age']['value'])
        emotion = max(face['attributes']['emotion'], key=face['attributes']['emotion'].get)
        if gender == 'Male':
            score = str(face['attributes']['beauty']['male_score'])
        else:
            score = str(face['attributes']['beauty']['female_score'])
        texts.append("gender:" + gender)
        texts.append("age:" + age)
        texts.append("emotion:" + emotion)
        texts.append("beauty:" + score)

        cnt = 0
        for text in texts:
            pos = (start[0], start[1] + cnt)
            cnt += 30
            cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)


def detect_picture_withpath(imgpath):
    img = cv2.imread(imgpath)
    _, buffer = cv2.imencode('.jpg', img)
    imgbin = buffer.tobytes()
    ret = get_ret(imgbin)
    draw_on_picture(img, ret)
    return img
    # cv2.imshow('img', img)
    # cv2.waitKey(0)

def detect_picture(img):
    _, buffer = cv2.imencode('.jpg', img)
    imgbin = buffer.tobytes()
    ret = get_ret(imgbin)
    draw_on_picture(img, ret)
    return img


def detect_video(video_path,  save_path):
    cap = cv2.VideoCapture(video_path)
    cnt = '0'
    frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    with tqdm(total=total_frames) as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = detect_picture(frame)
            frames.append(frame)
            pbar.update(1)
    save_video(frames, save_path)


def save_video(frames, save_path):
    height, width, _ = frames[0].shape

    # 设置要保存的视频文件名、编解码器、帧率和视频尺寸
    output_filename = os.path.join('output', save_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 使用 MP4 编解码器
    fps = 30.0  # 帧率
    video_size = (width, height)  # 视频尺寸与第一帧相同
    # 创建视频编写器对象
    video_writer = cv2.VideoWriter(output_filename, fourcc, fps, video_size)

    # 按顺序读取每一帧并写入视频
    for i in trange(len(frames)):
        frame = frames[i]

        # 将当前帧写入视频
        video_writer.write(frame)

    # 释放资源
    video_writer.release()


if __name__ == '__main__':
    imgpath = r"F:\Data\137\LuCheng\Projects\test\lijun.jpg"
    video_path = r"gaoyinge.mp4"
    save_path = r"gaoyinge.mp4"
    detect_video(video_path, save_path)
    # detect_picture_withpath(imgpath)
