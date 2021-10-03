import os
import io

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials



class GoogleSharedSheet:
    class Range:
        def __init__(self, sheet_name:str,beg_col_idx:int,end_col_idx:int,beg_row_idx:int,end_row_idx:int):
            self.string = f"{sheet_name}!{GoogleSharedSheet.Range.getColStr(beg_col_idx)}{beg_row_idx}:{GoogleSharedSheet.Range.getColIdx(end_col_idx)}{end_row_idx}"

        def getColIdx(string: str) ->int:
            index = 0
            for i in range(len(string)):
                index += ord(string[i])-ord('A')
                if i != len(string)-1:
                    index = (index+1)*26
            return index

        def getColStr(index: int) ->str:
            result = ''
            while True:
                result = chr(ord('A')+index%26) + result
                index //= 26
                if index <= 0:
                    break
                index-=1
            return result

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

    def _auth(tokenf,secretf):
        """
        Returns credential for google api auth
        {tokenf} - path to file in which token will be saved/loaded from if there is one already
        {secretf} - path to file in which secret is stored
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
            with io.open(tokenf, encoding="utf-8",mode='w' if os.path.exists(tokenf) else 'x') as token:
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
        

    def getData(self,rg):
        """ Converting, and getting raw data for
        it to be later converted in whatever you need it to be 
        In :    rh -GoogleSharedSheet.Range object - range of the data that will be copied
        """
        self.convertSheet()
        result = self.sheet.get(spreadsheetId=self.sheet_id, includeGridData = True,ranges = [rg.string] ).execute()
        print(rg.string)
        themeColors = result["properties"]["spreadsheetTheme"]["themeColors"]
        sheet_id = result["sheets"][0]["properties"]["sheetId"]
        rowData = result["sheets"][0]["data"][0]["rowData"]
        merges = result["sheets"][0]["merges"]
        self.deleteConvertedSheet()
        return sheet_id, rowData, merges, themeColors
