import os
import io

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

        

class GoogleSharedSheet:
    _scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    _local = '.local/'
    def __init__(self,sheet_id):
        """Initiate instance of GoogleSharedSheet class that can be later use to access
        data in the shared .xlsm spreadsheet 
        """
        

        service = build('sheets', 'v4', credentials=GoogleSharedSheet._auth(GoogleSharedSheet._local+'tokenS.JSON',GoogleSharedSheet._local+'SecretS.JSON'))

        # Create an instance of the Sheets API
        self.sheet = service.spreadsheets()
        self.sheet_id = None
        self.shared_id = sheet_id

        # Create an instance of the Drive API
        self.service = build('drive', 'v2', credentials=GoogleSharedSheet._auth(GoogleSharedSheet._local+'tokenD.JSON',GoogleSharedSheet._local+'SecretD.JSON'))

        # convert public sheet from microsoft excell format
        self.convertSheet() # for testing purposes 

    # def __del__(self):
    #     self.deleteConvertedSheet()
    #     pass

    def _auth(tokenf,secretf):
        """Just dont touch this and everything will be fine
        Returns credential for google api auth, getting and saving token from {tokenf}
        and getting {serctef} in case if {tokenf} doesnt exists 
        """
        creds = None
        if os.path.exists(tokenf):
            creds = Credentials.from_authorized_user_file(tokenf, scopes=GoogleSharedSheet._scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    secretf, scopes=GoogleSharedSheet._scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with io.open(tokenf, encoding="utf-8",mode='w' if os.path.exists() else 'x') as token:
                token.write(creds.to_json())
        return creds
    
    def convertSheet(self):
        """Makes a copy of shared xlsm sheet by spcified sheet_id in __init__
        for later converting it into google sheet to access it via 
        getCellData() or getData() methods
        Note: this method can be used for synchronisig shared sheet with saved on drive
        it'll delete an already existing instance of copied and converted sheet if it 
        was already created earlier
        """
        if self.isConverted():
            self.deleteConvertedSheet()
        result = self.service.files().copy(fileId=self.shared_id,convert=True,body={"title":"schedule_copy"}).execute()
        self.sheet_id = result["id"]

    def isConverted(self) ->bool:
        return self.sheet_id != None

    def deleteConvertedSheet(self):
        """Deletes copy of a shared sheet from users dirve created by
        convertSheet() method, nothing will happen if 
        """
        if self.isConverted():
            self.service.files().delete(fileId=self.sheet_id).execute()
            self.sheet_id = None
        

    def getData(self):
        """Does everything for you: sycnhronising, converting, and getting raw data for
        it to be later converted in whatever you need it to be :)
        """
        self.convertSheet()
        
        # values = result.get('values', [])
        
        self.deleteConvertedSheet()
        
