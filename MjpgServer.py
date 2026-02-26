#!/usr/bin/python3
"""
Author: Igor Maculan - n3wtron@gmail.com
A Simple mjpg stream http server
"""

import cv2
import time
import threading
import http
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer

img_show = None
quality = (int(cv2.IMWRITE_JPEG_QUALITY), 70)
_standalone_mode = False
_standalone_camera = None


class MJPG_Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global img_show
        if self.path == "/?action=snapshot":
            _update_frame_from_standalone_camera()
            if img_show is not None:
                try:
                    l_quality = (int(cv2.IMWRITE_JPEG_QUALITY), 100)
                    ret, jpg = cv2.imencode(".jpg", img_show, l_quality)
                    jpg_bytes = jpg.tobytes()
                    self.send_response(200)
                    self.send_header("Content-type", "image/jpeg")
                    self.send_header("Content-length", str(len(jpg_bytes)))
                    self.end_headers()
                    self.wfile.write(jpg_bytes)
                except Exception as e:
                    print("error1", e)
        else:
            img_show = None
            self.send_response(200)
            self.send_header(
                "Content-type",
                "multipart/x-mixed-replace; boundary=--boundarydonotcross",
            )
            self.end_headers()
            while True:
                try:
                    _update_frame_from_standalone_camera()
                    if img_show is not None:
                        ret, jpg = cv2.imencode(".jpg", img_show, quality)
                        jpg_bytes = jpg.tobytes()
                        self.send_header("Content-type", "image/jpeg")
                        self.send_header("Content-length", str(len(jpg_bytes)))
                        # self.send_header('X-Timestamp:', time.time())
                        self.wfile.write("--boundarydonotcross\r\n".encode())
                        self.end_headers()
                        self.wfile.write(jpg_bytes)
                    time.sleep(0.03)
                except Exception as e:
                    print("error2", e)
                    break


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def _update_frame_from_standalone_camera():
    global img_show
    global _standalone_camera
    if not _standalone_mode:
        return

    try:
        if _standalone_camera is None:
            import hiwonder.Camera as Camera

            _standalone_camera = Camera.Camera()
            _standalone_camera.camera_open()
            time.sleep(0.1)
        if _standalone_camera.frame is not None:
            img_show = _standalone_camera.frame
    except Exception as e:
        print("standalone camera error", e)


def startMjpgServer():
    try:
        server = ThreadedHTTPServer(("", 8080), MJPG_Handler)
        print("server started")
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    _standalone_mode = True
    startMjpgServer()
