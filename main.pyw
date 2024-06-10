#KivyMD (GUI)
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemTrailingSupportingText

#Paho-MQTT (Networking)
import paho.mqtt.client as mqtt

#Other (Libraries)
import os
import uuid
from threading import Thread, Event
from time import sleep
from queue import Queue, Empty

#Local Files
from settings import client_info, GUI

client = mqtt.Client(client_id=client_info.id)

class SpacerWidget(MDWidget): # Used to skip a cell in GridLayout (in .kv file)
    pass

class MainApp(MDApp): #KivyMD GUI Class
    
    def on_message(self, client, userdata, msg):
        rawcontent = msg.payload.decode("utf-8")
        content = rawcontent.split()
        self.data_queue.put(content)

        return

    def on_remote_ping(self, content):
        to_ping_id = content[0]
        to_ping_name = self.screen.ids[to_ping_id].text

        return
    
    def on_local_ping(self, to_ping_id):
        flags = self.screen.ids[to_ping_id]._accessory_action.text
        customer = self.screen.ids[to_ping_id].text
        payload = [to_ping_id, 'fdbar', 'ping', flags, customer]
        client.publish(client_info.topic, payload)

        return
        
    def on_remote_removal(self, content):
        to_remove_id = content[0]
        self.screen.ids['lst_activeorders'].remove_widget(id=to_remove_id)

        return
            
    def on_local_removal(self, to_remove_id):
        customer_name = self.screen.ids[to_remove_id].text
        self.screen.ids['lst_activeorders'].remove_widget(id=to_remove_id)
        payload = [to_remove_id, 'fdbar', 'rm', customer_name]
        client.publish(client_info.topic, payload)

        return
        
    def on_remote_add(self, content):
        self.screen.ids['lst_activeorders'].add_widget(MDListItem(MDListItemHeadlineText(text=content[4])), (MDListItemTrailingSupportingText(text=content[3])), id=content[0])

        return
    
    def on_local_add(self, customer_name, has_desert):
        to_add_id = str(uuid.uuid4()) # Creates unique ID for later reference to orders
        
        self.screen.ids['lst_activeorders'].add_widget(
            MDListItem(MDListItemHeadlineText(text=customer_name)),
            (MDListItemTrailingSupportingText(text=has_desert)),id=to_add_id) # Adds List Item to MDList in Active Orders
        
        payload = [to_add_id, 'fdbar', 'mk', has_desert, customer_name] # Generates payload to notify other clients of new order
        client.publish(client_info.topic, payload) # Sends order to all clients subscribed to topic defined in settings.py

        return
    
    def check_mqtt_queue(self, dt): # Checks Queue for new data and routes based on contents of received message
        content = None
        try:
            content = self.data_queue.get(timeout=0.1)
        except:
            pass # Ignoring empty queue
        
        if content:
            if content[2] == 'mk': # mk = Make (Add Order)
                self.on_remote_add(content)

            if content[2] == 'rm': # rm = Remove (Delete Order)
                self.on_remote_removal(content)
                
            if content[2] == 'ping': # ping = Notify (Customer On-Site for Order Pickup)
                self.on_remote_ping(content)
        
        return
    
    def mqtt_thread(self): # Establishes connection and creates sub_thread that monitors incoming messages
        client.username_pw_set(client_info.user, '')
        try:
            client.connect(client_info.ip, client_info.port, client_info.qos)
        except:
            pass

        client.subscribe(client_info.topic)
        client.on_message = self.on_message
        client.loop_start()

        return

    def build(self): # Builds GUI using settings.py parameters
        #GUI Customizations
        Window.borderless = GUI.borderless
        Window.size = GUI.size
        self.theme_cls.primary_palette = GUI.primary_palette
        self.theme_cls.accent_palette = GUI.accent_palette
        self.theme_cls.theme_style = GUI.theme_style
        self.screen = Builder.load_file(GUI.full_kv_file)
        
        return self.screen

    def on_start(self): # Run after GUI built
        self.data_queue = Queue() #Used to transfer data to main thread
        self.mqtt_thread = Thread(target=self.mqtt_thread) #Creating sub_thread to handle connections
        self.mqtt_thread.start() #Starting sub_thread
        
        Clock.schedule_interval(self.check_mqtt_queue, client_info.refresh) #Checks Queue for recieved data, pulls data into main thread

        return
    		
if __name__ == "__main__":
    MainApp().run()