import logging
import azure.functions as func
from datetime import date
from ftplib import FTP
import os, sys
import shutil
from pyunpack import Archive
from azure.storage.blob import BlobServiceClient

MY_CONTAINER = "entpackt"
LOCAL_PATH = f"/tmp/ifapdaten"
FILES_TO_UPLOAD = ["Artikel.xml", "Anbieter.xml", "Glossar.xml", "XML_Patiententexte.xml", "Rechtsinfos_Zusatz.xml", "Wirkstoffe.xml", "Zusammensetzungen.xml"]

 
class AzureBlobFileUploader:
  def __init__(self):
    print("Intializing AzureBlobFileUploader")
 
    MY_CONNECTION_STRING = os.environ["MY_CONNECTION_STRING"]

    # Initialize the connection to Azure storage account
    self.blob_service_client =  BlobServiceClient.from_connection_string(MY_CONNECTION_STRING)
 
  def upload_all_images_in_folder(self):

    all_files = [os.path.join(path, name) for path, subdirs, files in os.walk(LOCAL_PATH) for name in files]

    selected_files = [file_path for file_path in all_files for item in FILES_TO_UPLOAD if item in file_path]

    
    print(selected_files)

    logging.info("Schritt 1")
    #logging.info(all_file_names)
    # Upload each file
    for file_name in selected_files:
      self.upload(file_name)
 
  def upload(self,file_name):
    # Create blob with same name as local file name
    blob_client = self.blob_service_client.get_blob_client(container=MY_CONTAINER,
                                                          blob='ifap_daten/'+ file_name.split('\\')[-1])
    logging.info("Schritt 2")

    # Get full path to the file
    upload_file_path = os.path.join(file_name)
 
    # Create blob on storage
    # Overwrite if it already exists!
    logging.info(f"uploading file - {file_name}")
    with open(upload_file_path, "rb") as data:
      blob_client.upload_blob(data,overwrite=True)
 
  

def downloadFromFTP(FTP_HOST,FTP_USER,FTP_PASS,FTP_PORT):

    try:
        logging.info(FTP_HOST)
        with FTP(host=FTP_HOST,user=FTP_USER,passwd=FTP_PASS) as ftps:
            ftps.dir()
            ftps.cwd('pub')
            ftps.nlst()[0]

            with open(os.path.join('/tmp/ifap.7z'), 'wb' ) as file :
                ftps.retrbinary('RETR %s' % ftps.nlst()[0], file.write)

                #file.close()
            ftps.quit()
        os.makedirs(LOCAL_PATH)

        #and unzip
        logging.info('Extract 7z')
        Archive('/tmp/ifap.7z').extractall(LOCAL_PATH)


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #return(exc_type, fname, exc_tb.tb_lineno)
        raise 



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    FTP_HOST = os.getenv('FTP_HOST')
    FTP_USER = os.getenv('FTP_USER')
    FTP_PASS = os.getenv('FTP_PASS')
    FTP_PORT = os.getenv('FTP_PORT')


    try:

        if os.path.exists(LOCAL_PATH):
          shutil.rmtree(LOCAL_PATH)

        downloadFromFTP(FTP_HOST,FTP_USER,FTP_PASS,FTP_PORT)

        azure_blob_file_uploader = AzureBlobFileUploader()
        azure_blob_file_uploader.upload_all_images_in_folder()


        return func.HttpResponse(f"Done.")

    except Exception as e:

        return func.HttpResponse(f"Done. But with erros"+str(e),status_code=400)


