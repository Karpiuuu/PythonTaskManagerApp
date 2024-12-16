import unittest
import os
import json
from tkinter import Tk
from main import TaskManagerApp


class TestTaskManagerApp(unittest.TestCase):
    def setUp(self):
        """Create an instance of the application and a test JSON file."""
        self.test_file = "test_tasks.json"
        self.root = Tk()  # Create a Tkinter root window
        self.root.withdraw()  # Hide the Tkinter window during tests
        self.app = TaskManagerApp(self.root)  # Pass the root to the app instance
        self.app.tasks_file = self.test_file

        # Ensure the test environment is clean
        self.app.task_data = []
        if os.path.exists(self.test_file):
            with open(self.test_file, "w") as file:
                json.dump([], file)

    def tearDown(self):
        """Remove the test file after completing the tests."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.root.destroy()  # Destroy the Tkinter root window

    def test_add_task(self):
        """Test adding a task."""
        task_name = "Test Task"
        task_status = "To Do"
        task_description = "This is a test task description."

        # Add a task
        self.app.add_task_to_tree(task_name, task_status, task_description)
        self.app.task_data.append({"name": task_name, "status": task_status, "description": task_description})

        # Check if the task was added correctly
        self.assertEqual(len(self.app.task_data), 1)
        self.assertEqual(self.app.task_data[0]["name"], task_name)
        self.assertEqual(self.app.task_data[0]["status"], task_status)
        self.assertEqual(self.app.task_data[0]["description"], task_description)

    def test_edit_task(self):
        """Test editing a task."""
        # Add a task
        task_name = "Test Task"
        task_status = "To Do"
        task_description = "This is a test task description."
        self.app.task_data.append({"name": task_name, "status": task_status, "description": task_description})

        # Edit the task
        new_status = "In Progress"
        new_description = "Updated description."
        self.app.task_data[0]["status"] = new_status
        self.app.task_data[0]["description"] = new_description

        # Check if the changes were applied
        self.assertEqual(self.app.task_data[0]["status"], new_status)
        self.assertEqual(self.app.task_data[0]["description"], new_description)

    def test_delete_task(self):
        """Test deleting a task."""
        task_name = "Test Task"
        task_status = "To Do"
        task_description = "This is a test task description."
        self.app.task_data.append({"name": task_name, "status": task_status, "description": task_description})

        # Delete the task
        self.app.task_data = [task for task in self.app.task_data if task["name"] != task_name]

        # Check if the list is empty
        self.assertEqual(len(self.app.task_data), 0)

    def test_save_tasks(self):
        """Test saving tasks to a JSON file."""
        task_name = "Test Task"
        task_status = "To Do"
        task_description = "This is a test task description."
        self.app.task_data.append({"name": task_name, "status": task_status, "description": task_description})

        # Save tasks
        self.app.save_tasks()

        # Check if the file was created and the data is correct
        with open(self.test_file, "r") as file:
            data = json.load(file)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], task_name)
        self.assertEqual(data[0]["status"], task_status)
        self.assertEqual(data[0]["description"], task_description)

    def test_load_tasks(self):
        """Test loading tasks from a JSON file."""
        # Prepare test data
        data = [
            {"name": "Task 1", "status": "To Do", "description": "Description of task 1"},
            {"name": "Task 2", "status": "In Progress", "description": "Description of task 2"}
        ]
        with open(self.test_file, "w") as file:
            json.dump(data, file)

        # Load data
        self.app.load_tasks()

        # Check if the data was loaded correctly
        self.assertEqual(len(self.app.task_data), 2)
        self.assertEqual(self.app.task_data[0]["name"], "Task 1")
        self.assertEqual(self.app.task_data[1]["status"], "In Progress")
        self.assertEqual(self.app.task_data[1]["description"], "Description of task 2")


if __name__ == "__main__":
    unittest.main()
