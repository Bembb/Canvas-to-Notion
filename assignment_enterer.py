"""
assignment_enterer puts assignments from your canvas courses into your notion to-do list! It might be poorly optimized but it's better than entering hundreds of assignments manually.
"""

import os
import json
import requests

from dotenv import load_dotenv
from canvasapi import Canvas
from notion_client import Client

# load env variables
load_dotenv()
API_URL = "https://osu.instructure.com/"
CANVAS_KEY = os.getenv("CANVAS_API_KEY")
NOTION_KEY = os.getenv("NOTION_API_KEY")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

# Initialize a new Canvas/notion object
canvas = Canvas(API_URL, CANVAS_KEY)
os.environ['NOTION_TOKEN'] = NOTION_KEY
notion = Client(auth=os.environ["NOTION_TOKEN"])


headers = {
    "Authorization": "Bearer " + NOTION_KEY,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


"""
returns list of all titles of every page in the to-do list from a specific course. 
db_id is the id of the notion database to read.
course_id is the id of the course to get assignment titles from
"""
def get_titles(db_id, course_id):
    # filter to only get assignments from the specific course
    query_filter = {
        "filter": {
            "property": "Course",
            "relation": {
                "contains": course_id
            }
        }
    }

    # create empty list to contain titles
    titles = []
    url = f"https://api.notion.com/v1/databases/{db_id}/query"

    response = requests.post(url, json = query_filter, headers=headers)

    # if found
    if response.status_code == 200:
        data = response.json()
        # Loop through the results and extract titles
        for result in data.get("results", []):
            title_property = result["properties"].get("Name", {})  
            if title_property.get("title"):
                title = title_property["title"][0].get("text", {}).get("content", "")
                titles.append(title)
    else: # if not found
        print(f"Error: {response.status_code}, {response.text}")
    

    return titles

def main():
    # open file containing all course/database ids (the structure is odd lines are canvas course ids, even lines are notion course page ids, the corresponding notion-course-page id comes after the canvas course id)
    try:
        with open("course_ids.json", "r") as file:
            obj = json.load(file)
    except FileNotFoundError:
        print("Error: course_ids.json not found")
        return
    
    for entry in obj:
        course_id = entry["canvas_id"]
        course_notion_id = entry["notion_relation_id"]

        # Get all assignments in Canvas course
        course = canvas.get_course(course_id)
        print(f"COURSE: {course.name} ({course_id})")
        assignments = course.get_assignments()

        #  Get all assignment names in Notion course page
        titles = get_titles(NOTION_DB_ID, course_notion_id)

        # For each assignment in this course (on canvas): 
        for assignment in assignments:
            #check if already in database
            if assignment.name in titles:
                print("Assignment already in Notion. Skipping...")
                continue
            # If not in Notion database, add to Notion database.
            print(f"Writing assignment '{assignment.name}' to Notion...")
            new_page = {
                "Name": {
                    "type": "title",
                    "title": [
                    {
                        "type": "text",
                        "text": {"content": assignment.name, "link":{"url":assignment.html_url}},
                    }
                ],
                },
                "Course": {
                    "type": "relation",
                    "relation": [{"id": course_notion_id}]
                },
            }
            # Add due date if exists
            if(assignment.due_at is not None):
                new_page["Due date"] = {
                        "type": "date",
                        "date": {"start": assignment.due_at}
                        }
    
            notion.pages.create(parent={"database_id": NOTION_DB_ID}, properties=new_page)


if __name__ == "__main__":
    main()