import re
import os

from TelegramBot import access_token
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request



class GdriveHelperException(Exception):
    """Raise when something wrong related with Google Drive functions."""


class GoogleDriveHelper:
    def __init__(self):
        self.GDRIVE_TOKEN_FILE = "token.json"
        self.OAUTH_SCOPE = ['https://www.googleapis.com/auth/drive']

    @staticmethod
    def is_gdrive_link(gdrive_url: str) -> bool:
        """
	    Check if the given link is valid Google Drive link or not.
	    """

        pattern = 'https?://(drive\.google\.com\/)\S+'
        return bool(re.search(pattern, gdrive_url))

    @staticmethod
    def is_gdrive_folder(gdrive_url: str) -> bool:
        """
	    Check if the given Google Drive url is folder or not.
	    """

        return "folders" in gdrive_url

    @staticmethod
    def get_id(gdrive_url: str) -> str:
        """
	    Extract Google Drive ID from the the Google Drive URL.
	    """

        try:
            return re.search(r'([-\w]{25,})', gdrive_url)[0]
        except Exception as error:
            raise GdriveHelperException("Drive ID not found") from error

    def get_credentials(self):
        """
	    Generate credentials from token.json
	    """

        credentials = None

        if not os.path.exists(self.GDRIVE_TOKEN_FILE):
            raise GdriveHelperException("token.json not found")

        try:
            credentials = Credentials.from_authorized_user_info(access_token, self.OAUTH_SCOPE)
        except:
            raise GdriveHelperException("Something wrong with the given token.json file.")

        if (
            (credentials is None or not credentials.valid)
            and credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())

        return credentials

    def get_metadata(self, gdrive_url):
        """
	    Return the  metadata of the given Google Drive File url.
	    """

        credentials = self.get_credentials()
        file_id = self.get_id(gdrive_url)

        try:
            service = build('drive', 'v3', cache_discovery=False, credentials=credentials)
            metadata = service.files().get(fileId=file_id, fields='name, size, mimeType',
                                           supportsAllDrives=True).execute()

        except HttpError as error:
            raise GdriveHelperException(error.reason) from error
        return metadata

    def get_bearer_token(self):
        """
	    Return Authentication Bearer token to pass down as header for downloading Gdrive Links.
	    """

        credentials = self.get_credentials()
        return credentials.token

    def get_ddl_link(self, gdrive_link):

        file_id = self.get_id(gdrive_link)
        return f"https://www.googleapis.com/drive/v3/files/{file_id}\?supportsAllDrives\=true\&alt\=media"
