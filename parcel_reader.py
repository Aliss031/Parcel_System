from flask import Flask, render_template_string, Response
import cv2
import easyocr

app = Flask(__name__)
reader = easyocr.Reader(['en'], gpu=False)

camera = cv2.VideoCapture("http://10.114.0.213:8080/video")

# HTML page template
HTML_PAGE = """
<!doctype html>
<title>Live OCR Stream</title>
<h2 style="text-align:center;">Live OCR Text Detection</h2>
<div style="display:flex; justify-content:center;">
    <img src="{{ url_for('video_feed') }}">
</div>
"""

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        resized_frame = cv2.resize(frame, (640, 480))
        results = reader.readtext(resized_frame)

        y_offset = 30  # For overlay text
        detected_texts = []

        for (bbox, text, prob) in results:
            (tl, tr, br, bl) = bbox
            tl = tuple(map(int, tl))
            br = tuple(map(int, br))

            # Draw box and put text near box
            cv2.rectangle(resized_frame, tl, br, (0, 255, 0), 2)
            cv2.putText(resized_frame, text, (tl[0], tl[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            detected_texts.append(text)

        # Show all detected text at top left
        for i, text in enumerate(detected_texts[:5]):  # Show up to 5 lines
            cv2.putText(resized_frame, f"> {text}", (10, y_offset + i*25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        ret, buffer = cv2.imencode('.jpg', resized_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
