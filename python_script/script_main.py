import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Replace these variables with your own values
CREDS_FILE = 'C:/Users/HP/Desktop/chatbot/req_JSON/fleet-gift-399519-c174726df4ba.json'
# CALENDAR_ID = 'your_calendar_id@group.calendar.google.com'  # Your Google Calendar ID
CALENDAR_ID = 'kavitakhanna75@gmail.com'  # Your Calendar ID

TIME_ZONE = 'Asia/Kolkata'  # Your timezone, e.g., 'America/New_York'

# Initialize the Google Calendar API
def initialize_calendar():
    creds = service_account.Credentials.from_service_account_file(
        CREDS_FILE, scopes=['https://www.googleapis.com/auth/calendar']
    )
    service = build('calendar', 'v3', credentials=creds)
    return service

def build_task_event_map(service):
    task_event_map = {}
    try:
        events = service.events().list(calendarId=CALENDAR_ID).execute()
        for event in events.get('items', []):
            task_name = event.get('summary', '')
            event_id = event.get('id', '')
            if task_name and event_id:
                task_event_map[task_name] = event_id
        return task_event_map
    except Exception as e:
        print(f"An error occurred while building the task event map: {str(e)}")
        return {}

# Create a task/event on Google Calendar and update the dictionary
def create_task(service, task_name, task_type, start_time_str, duration_hours):
    try:
        start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
        end_time = start_time + datetime.timedelta(hours=duration_hours)

        event = {
            'summary': f"{task_name}",
            'description': f"Task Type: {task_type}",
            'start': {'dateTime': start_time.strftime('%Y-%m-%dT%H:%M:%S'), 'timeZone': TIME_ZONE},
            'end': {'dateTime': end_time.strftime('%Y-%m-%dT%H:%M:%S'), 'timeZone': TIME_ZONE},
        }

        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        event_id = created_event.get('id')

        # Update the task_event_map with the task name and event ID
        task_event_map[task_name] = event_id

        return created_event.get('htmlLink')

    except Exception as e:
        return str(e)

# Delete a task/event from Google Calendar using its name
def delete_task_by_name(service, task_name):
    try:
        # Retrieve the event ID from the task_event_map
        event_id = task_event_map.get(task_name)

        if event_id:
            # Delete the task/event using its event ID
            service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
            # Remove the task from the task_event_map
            del task_event_map[task_name]
            return True
        else:
            return False

    except HttpError as e:
        print(f"An error occurred while deleting the task: {str(e)}")
        return False
    
# Update an existing task/event in Google Calendar by event name
def update_task_by_name(service, event_name, updated_task_name, updated_start_time_str, updated_duration_hours):
    try:
        # Retrieve the event ID from the task_event_map based on the event name
        event_id = task_event_map.get(event_name)

        if event_id:
            # Fetch the existing event details
            existing_event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

            # Update the event with new details
            start_time = datetime.datetime.strptime(updated_start_time_str, "%Y-%m-%d %H:%M")
            end_time = start_time + datetime.timedelta(hours=updated_duration_hours)

            existing_event['summary'] = f"{updated_task_name}"
            existing_event['start']['dateTime'] = start_time.strftime('%Y-%m-%dT%H:%M:%S')
            existing_event['end']['dateTime'] = end_time.strftime('%Y-%m-%dT%H:%M:%S')

            updated_event = service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=existing_event).execute()
            return updated_event.get('htmlLink')
        else:
            return "Event not found"

    except Exception as e:
        return str(e)


if __name__ == "__main__":
    # Initialize the Google Calendar service
    service = initialize_calendar()
    task_event_map = build_task_event_map(service)

    while True:
        print("1. Create Task")
        print("2. Update Task")
        print("3. Delete Task")
        print("4. lsit of Task")
        print("5. Exit")
        
        choice = input("Enter your choice: ")

        if choice == "1":
            # Prompt the user for task details
            task_name = input("Enter task name: ")
            task_type = input("Enter task type: ")
            start_time_str = input("Enter task start date and time (YYYY-MM-DD HH:MM): ")
            duration_hours = int(input("Enter task duration in hours: "))

            # Create the task/event and get the event link
            event_link = create_task(service, task_name, task_type, start_time_str, duration_hours)

            if event_link:
                print(f"Task created successfully. View it here: {event_link}")
            else:
                print("An error occurred while creating the task.")
        
        elif choice == "2":
            event_name = input("Enter the name of the event/task to update: ")
            updated_task_name = input("Enter updated task name: ")
            # updated_task_type = input("Enter updated task type: ")2
            updated_start_time_str = input("Enter updated start date and time (YYYY-MM-DD HH:MM): ")
            updated_duration_hours = int(input("Enter updated duration in hours: "))

            updated_link = update_task_by_name(service, event_name, updated_task_name, updated_start_time_str, updated_duration_hours)

            if updated_link:
                print(f"Task updated successfully. View it here")
        elif choice == "3":
            print(task_event_map)
            if(len(task_event_map)==0):
                print("no taks found")
                continue
            task_name_to_delete = input("Enter the name of the task to delete: ")
            if delete_task_by_name(service, task_name_to_delete):
                print(f"Task '{task_name_to_delete}' deleted successfully.")
            else:
                print(f"Task '{task_name_to_delete}' not found or deletion failed.")
        elif choice=="4":
            print(task_event_map)
        elif choice == "5":
            break