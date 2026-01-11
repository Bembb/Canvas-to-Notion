# Canvas Assignments to Notion Database Script

This is a script to automate importing Canvas assignments to a Notion database. It reads a list of courses, fetches assignments (including names, links and due dates), and adds them to your Notion database. If the assignment name already exists in Notion for that course, it gets skipped.



## Setup

### Notion
You will need a Notion database to store your assignments in. Each item needs at least these properties:
| Property Name | Type     | Description                          |
|---------------|----------|--------------------------------------|
| Name          | Title    | Default title column.                |
| Due date      | Date     | Assignment deadline.                 |
| Course        | Relation | Linked to separate Courses database. |

### API Keys
This script requires a Canvas and Notion API key. You will need to create a .env file in the root directory:

```
CANVAS_API_KEY=your canvas key here
NOTION_API_KEY=your notion key here
NOTION_DB_ID=your db id here
```

### course_ids.json
For each course you want to grab the assignments of, you'll need its Canvas ID and corresponding Course page ID in Notion. Create a `course_ids.json` file. This maps your Canvas courses to the specific page ID in your Notion "Courses" database. It is formatted like so:

```
[
    {
    "canvas_id": 123456,
    "notion_relation_id": "your_notion_course_page_id_here"
    }
]
```

### How to run
1. Install dependencies:

```
pip install -r requirements.txt
```

2. Run the script:

```
python3 assignment_enterer.py
```
