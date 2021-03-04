from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    label_id = None
    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            if 'Daily Coding Problems' in label['name']:
                label_id = label['id']

    dir_info = {"Easy": "C:\\Users\\s0095057\\Documents\\Personal\\Projects\\DailyCodingProblems\\Easy",
                "Medium": "C:\\Users\\s0095057\\Documents\\Personal\\Projects\\DailyCodingProblems\\Medium",
                "Hard": "C:\\Users\\s0095057\\Documents\\Personal\\Projects\\DailyCodingProblems\\Hard"}
    if label_id is not None:
        results = service.users().messages().list(userId='me', labelIds=[label_id], maxResults=10000).execute()
        messages = results.get('messages', [])
        if not messages:
            print("No messages found.")
        else:
            print("Message snippets:")
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                subject = [sub['value'] for sub in msg['payload']['headers'] if sub['name']=='Subject'][0]
                if 'Daily Coding Problem: Problem #' in subject:
                    subject = subject.replace('Daily Coding Problem: Problem #', '')
                    sub_info = subject.split(' ')
                    _type = sub_info[-1].replace('[','').replace(']','')
                    _file_path = os.path.join(dir_info[_type], 'problem_%s.txt' %sub_info[0])
                    coded_data = msg['payload']['parts'][0]['body']['data']
                    _data = base64.urlsafe_b64decode(coded_data.encode("ASCII")).decode("utf-8")
                    sents = _data.split('\n')
                    start = "Good morning! Here's your coding interview problem for today."
                    end = "Upgrade to premium"
                    outp = []
                    start_flag = False
                    for sent in sents:
                        if end in sent:
                            break
                        if start_flag and start not in sent:
                            outp.append(sent)
                        if start in sent:
                            start_flag = True

                    print('Problem %s' %sub_info[0])
                    with open(_file_path, 'w', encoding="utf-8") as f:
                        for line in outp:
                            f.write(line)
                    print('---------')

if __name__ == '__main__':
    main()