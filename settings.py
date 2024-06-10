class client_info():
        topic = 'AepSFr$U^B^DTPe6dB7JoZ@nKdwBXwkS3gQAKpEqj6^EF@NmNN@&79hF2FzJdVMC'
        user = "ZcVzpJjJhfb2kA4s" # Username
        id = "Debugging" #User-Friendly Name
        ip = "24.237.61.146" #Broker Address
        port = 1883
        qos = 60
        refresh = 5 #Message Polling Rate in Seconds

class GUI():
    borderless = True
    size = (1024, 600)
    primary_palette = 'Royalblue'
    accent_palette = 'Skyblue'
    theme_style = 'Dark'
    full_kv_file = 'fullui.kv'
    lite_kv_file = 'liteui.kv'


#DEV NOTES
#Message Structure
#msg_id, audience, action, flags, customer