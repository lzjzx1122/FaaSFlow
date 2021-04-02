import requests,json

def main(event):
    evt = json.loads(event)
    error_status = evt.status
    if error_status == '500':
        return {"message":"The error occurs when the video is transcoding."}
        #Save logs into database


    if error_status == '404':
        return {"message":"The video is too large to be simply transcoded."}
        #inform the frontend
 