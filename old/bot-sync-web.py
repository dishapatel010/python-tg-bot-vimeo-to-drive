import time
import telebot
import os
import sys
import drive_api as drive
import vimeo_api as vimeo
import shutil
from slugify import slugify
from flask import Flask, request

server = Flask(__name__)
# Pybot
TOKEN = "1256163582:AAEUbeS_KJ77AXv68zY13beIM03FoG0H7eg"

#  TEST BOT TOKEN
# TOKEN = "1200831446:AAHIkHX6aWLhCzCx_U1s_6reylc7R7xgBok"


bot = telebot.TeleBot(token=TOKEN)
# bot = telebot.AsyncTeleBot(token=TOKEN)

default_dir = '16m8_vJaE--4LludRLZNSVVP86j1XrAkT'
current_set_dir = '16m8_vJaE--4LludRLZNSVVP86j1XrAkT'
heroku_web_url = 'https://py-bot-vimeo.herokuapp.com/'
# heroku_web_url = 'https://127.0.0.1:5000/'

dileep = 760135118
venu = 642649878
kamesh = 599072894
allowed_grp = -1001413818920

allowed_users_grp = [dileep, allowed_grp]


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

download_completed_files = []
download_failed_files = []
upload_failed_files = []
logs = []
allowed_grp = -322400391

bot_downloding_status = False

#removing output and temp files
print("\n\n Removing Output directory and Temp directory")
if os.path.exists(OUTPUT_DIR) and os.path.isdir(OUTPUT_DIR):
    print('removing output directory')
    shutil.rmtree(OUTPUT_DIR)

if os.path.exists(TEMP_DIR) and os.path.isdir(TEMP_DIR):
    print('removing temp directory')
    shutil.rmtree(TEMP_DIR)

print('Bot Started :)')






@bot.message_handler(commands=['add']) 
def add_grp_user_handle(message):
    print("\n\n\nGOT ADD REQUEST >>")
    if isAllowed(message)!=True:
        send_chat_message(message, 'You are not Authorized')
        return
    print(f"ALLOWING USER ID OR GRP ID:: {message.text.split(' ')[1]}")
    allow_this_grp_user(int(message.text.split(' ')[1]), message)


@bot.message_handler(commands=['start']) 
def send_welcome(message):
    print("\n\n\n<<GOT START REQUEST>>")
    if isAllowed(message)!=True:
        send_chat_message(message, 'You are not Authorized')
        return
    global bot_downloding_status
    if bot_downloding_status == False:
        print(f"\n\n Start MEssage :: \n{message}\n\n")
        send_chat_message(message, 'welcome to glad to see you. \n what you will download today \n????')
    else:
        send_chat_message(message, '?????????\n ????????????\n wait, \n Bot is Busy')
    
@bot.message_handler(commands=['help'])
def send_help(message):
    print("\n\n\n<<GOT HELP REQUEST>>")
    if isAllowed(message)!=True:
        send_chat_message(message, 'You are not Authorized')
        return
    global bot_downloding_status
    if bot_downloding_status == False:
        msg = get_help_message()
        send_chat_message(message, msg)
    else:
        send_chat_message(message, '?????????\n ????????????\n wait, \n Bot is Busy')

 

@bot.message_handler(commands=['files'])
def get_files(message):
    print("\n\n\n<< GOT FILES REQUEST >>")
    if isAllowed(message)!=True:
        send_chat_message(message, 'You are not Authorized')
        return
    global bot_downloding_status
    if bot_downloding_status == False:
        send_chat_message(message, get_downloaded_files_list())
    else:
        send_chat_message(message, '?????????\n ????????????\n wait, \n Bot is Busy.')
        bot.delete_message(get_chat_id(message), message.message_id)
        time.sleep(2)
        bot.delete_message(get_chat_id(message), message.message_id+1)

@bot.message_handler(commands=['logs'])
def get_logs_handler(message):
    print("\n\n\n<<GOT LOGS REQUEST>>")
    if isAllowed(message)!=True:
        send_chat_message(message, 'You are not Authorized')
        return    
    global bot_downloding_status
    if bot_downloding_status == False:
        count = message.text[6]
        if count == '':
            count = '10'
        try:
            send_chat_message(message, 'Logs: \n'+get_logs(int(count)))
        except:
            send_chat_message(message, 'Error occured..')
    else:
        send_chat_message(message, '?????????\n ????????????\n wait, \n Bot is Busy.')



@bot.message_handler(commands=['d'])  
def name_download(message):
    print("\n\n\n<< GOT DOWNLOAD VIDEO REQ >>")
    if isAllowed(message)!=True:
        send_chat_message(message, 'You are not Authorized')
        return
    global bot_downloding_status
    if bot_downloding_status == False:
        try:
            bot_downloding_status =True
            fulltext = message.text[3:].split('@')
            if((fulltext[1] is None) or ('json' not in fulltext[1])):
                return bot.reply_to(message, "???????????? vimeo url err")
            if(fulltext[0] is None):
                return bot.reply_to(message, "???????????? filename err")
            fulltext[0] = slugify(fulltext[0])
            download_request(fulltext[0], fulltext[1], message)
        
        except IndexError:
            send_chat_message(message, '????????????\nFILENAME: '+fulltext[0]+'\nPlease check command.')
            print(f"\n\n\n\n\n {fulltext} command error of /d")
        except:
            print(f"\n\n\n\n\n {fulltext} Something err in download_request() function.")
            send_chat_message(message, '????????????\nFILENAME: '+fulltext[0]+'\nSomething went wrong')
        finally:
            bot_downloding_status = False
    else:
        send_chat_message(message, '?????????\n ????????????\n wait, \n Bot is Busy.')


@bot.message_handler(commands=['sync']) 
def sync_items(message):
    print("\n\n\n<<GOT SYNC CMD>>")
    if isAllowed(message)!=True:
        send_chat_message(message, 'You are not Authorized')
        return
    global bot_downloding_status
    if bot_downloding_status == False:
        bot_downloding_status = True
        reqs = message.text.split('\n')
        print(f"Got requests :: \n{reqs[1:]}")
        clear_unwanted_logs()
        try:
            download_sync(reqs[1:], message)
        except:
            bot.reply_to(message, "???????????? \nerror Occured !!\n")
        finally:
            bot_downloding_status = False
    else:
        send_chat_message(message, '?????????\n ????????????\n wait, \n Bot is Busy.')














def download_sync(reqs, message):
    start_all_at = time.time() 
    send_chat_message(message, "Dude, Bot Downloading Started you just chill and come later. \n look for happy face ")
    send_chat_message(message, '????')
    for req in reqs:
        fulltext = req.split('@')
        print(fulltext)
        if((fulltext[1] is None) or ('json' not in fulltext[1])):
            bot.reply_to(message, fulltext[0]+" ???????????? vimeo url err")
            continue
        if(fulltext[0] is None):
            bot.reply_to(message, fulltext[0]+" ???????????? filename err")
            continue
        fulltext[0] = slugify(fulltext[0])

        print("Downloading ... ")
        print(f"Downoading : {fulltext[0]} - URL : {fulltext[1]}")

        download_request(fulltext[0], fulltext[1], message)
    send_chat_message(message, 'All downloads done ????????????????\n????????????????\n???????????????? \n Downloaded files are her :: ')
    send_chat_message(message, get_downloaded_files_list())
    send_chat_message(message, get_download_failed_files_list())
    send_chat_message(message, get_upload_failed_files_list())
    end_all_at = time.time()
    taken_time = (end_all_at - start_all_at)/60
    send_chat_message(message, 'Total Taken Time :: '+taken_time+' minutes')

    


def download_request(file_name, json_url, message):
    global download_completed_files
    global logs
    global download_failed_files
    global upload_failed_files
    start = time.time()
    logs.append('??? FILENAME: '+file_name+' > Download Started')
    print('????????? \nFILENAME: '+file_name+'\nDwonload Started')
    send_chat_message(message, '????????? \nFILENAME: '+file_name+'\nDwonload Started')
    #Downloading Vimeo File
    [download_status, dmsg] = vimeo.vimeo_downloader(json_url, file_name, False, False)


    if(download_status == True):

        print('???????????? \nFILENAME: '+file_name+'\nDownload Done')
        send_chat_message(message, '???????????? \nFILENAME: '+file_name+'\nDownload Done')
        logs.append('???? FILENAME: '+file_name+' > File Downloaded')

        #UPLOAD File TO GDRIVE
        global current_set_dir
        print(f'\n\n{file_name} uploading..  ::to folder :: {current_set_dir}')
        [upload_status, umsg]= drive.upload_video_to_this_folder(current_set_dir,file_name)
        if(upload_status == True):
            end = time.time()
            taken_time = (end - start)/60
            print('???????????? \nFILENAME: '+file_name+'\nUpload Done \nTaken Time :: '+taken_time+' minutes')
            send_chat_message(message, '???????????? \nFILENAME: '+file_name+'\nUpload Done \nTaken Time :: '+taken_time+' minutes')
            download_completed_files.append('??? >>> '+file_name)
            logs.append('??? FILENAME: '+file_name+' > File Downloaded and Uploaded Completely')
            

        else:
            logs.append('???? FILENAME: '+file_name+' > Upload failed Gdrive')
            upload_failed_files.append('???? FILENAME: '+file_name+' > Upload failed Gdrive')
            send_chat_message(message, '????????????\nFILENAME: '+file_name+'\nUpload failed Gdrive')
            print('????????????\nFILENAME: '+file_name+'\nUpload failed Gdrive')
    else:
        logs.append('???? FILENAME: '+file_name+' > Download failed')
        download_failed_files.append('???? FILENAME: '+file_name+' > Download failed')
        send_chat_message(message, '????????????\n'+file_name+'Download failed')
        print('????????????\nFILENAME: '+file_name+'Download failed')
    return


def clear_unwanted_logs():
    global download_completed_files
    global download_failed_files
    global upload_failed_files
    download_completed_files.clear()
    download_failed_files.clear()
    upload_failed_files.clear()



def send_chat_message(message, msg):
    chat_id = get_chat_id(message)
    bot.send_message(chat_id, msg)
    return

def get_downloaded_files_list():
    global download_completed_files
    messgae = 'Downloaded Files are :\n'
    for filename in download_completed_files:
        messgae = messgae+filename+ '\n'
    return messgae

def get_download_failed_files_list():
    global download_failed_files
    messgae = 'Downloaded Failed Files are :\n'
    for filename in download_failed_files:
        messgae = messgae+filename+ '\n'
    return messgae

def get_upload_failed_files_list():
    global upload_failed_files
    messgae = 'Upload Failed Files are :\n'
    for filename in upload_failed_files:
        messgae = messgae+filename+ '\n'
    return messgae

def get_chat_id(message):
    chat =  message.chat
    chat_id = getattr(chat, "id")
    return chat_id


def get_logs(count):
    global logs
    flogs = []
    if(count>=len(logs)):
        flogs = logs
    else:
        flogs = logs[-count:]
    message = ''
    for log in flogs:
        message = message+'\n'+log
    return message    


def isAllowed(message):
    global allowed_grp
    print(f"\n\n\n\n:::Checking Authorization :::")
    chat_id = get_chat_id(message)
    print("Got chat ID:: "+str(chat_id))
    user_id = get_from_user_id(message)
    print(f"GOT USER ID :: {user_id}")
    if(chat_id in allowed_users_grp or user_id in allowed_users_grp):
        print("Access Granted")
        return True
    else:
        print("Access Rejected")
        return False

def get_from_user_id(message):
    from_user = message.from_user
    # print(f"From User :: {from_user}")
    user_id = getattr(from_user, "id")
    return user_id

def allow_this_grp_user(grp_id, message):
    global allowed_users_grp
    allowed_users_grp.append(grp_id)
    send_chat_message(message, str(grp_id)+'\n::Group or user now allowed')
    print(f"Allowed Users or grps : \n{allowed_users_grp}")


def get_help_message():
    msg = 'List of Commands are :\n\n\n'
    msg = msg + '/help - get help from me\n\n\n'
    msg = msg + '/d - cmd to download vimeo file with name and link seperated by @\n\n'
    msg = msg + 'Ex: /d <<you_file_name>>@<<download_url>>\n\n\n'
    msg = msg + '/files - get all downloaded files\n\n'
    msg = msg + '/logs 5- get logs of specified count\n\n'
    msg = msg + '   Ex: /logs <<count_val>>\n\n\n'
    msg = msg + '/sync - download files synchronously \n\n'
    msg = msg + 'EX: \n/sync - \nfile1@url1\nfile2@url2\n\n\n'
    return msg
















@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
   bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
   return "!", 200

@server.route("/")
def webhook():
   bot.remove_webhook()
   bot.set_webhook(url=heroku_web_url + TOKEN)
   return "Sucessfully added webhook to bot:<br>To remove /stop", 200

@server.route("/stop")
def delete_webhook():
    bot.remove_webhook()
    return "Web hook removed !!",200




if __name__ == "__main__":
   server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

