"""Service class for managing projects"""


class ProjectService:
    """Service class for managing projects"""

    def __init__(self):
        # Static dummy data for projects
        self.projects = [
            {
                "id": 1,
                "name": "Project Alpha",
                "description": "A groundbreaking project.",
                "status": "active",
            },
            {
                "id": 2,
                "name": "Project Beta",
                "description": "An innovative solution.",
                "status": "completed",
            },
            {
                "id": 3,
                "name": "Project Gamma",
                "description": "Under development.",
                "status": "active",
            },
        ]
        self.next_id = 4  # Auto-increment ID for new projects

    def get_projects(self, search="", status="all", page=1, per_page=5):
        """Fetch paginated and filtered projects"""
        filtered_projects = self.projects
        if search:
            filtered_projects = [
                p
                for p in filtered_projects
                if search.lower() in p["name"].lower()
                or search.lower() in p["description"].lower()
            ]
        if status != "all":
            filtered_projects = [p for p in filtered_projects if p["status"] == status]

        total_pages = (len(filtered_projects) + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        return filtered_projects[start:end], total_pages

    def get_project_by_id(self, project_id):
        """Fetch a project by its ID"""
        return next((p for p in self.projects if p["id"] == project_id), None)

    def add_project(self, name, description, status):
        """Add a new project"""
        new_project = {
            "id": self.next_id,
            "name": name,
            "description": description,
            "status": status,
        }
        self.projects.append(new_project)
        self.next_id += 1

    def update_project(self, project_id, name, description, status):
        """Update an existing project"""
        project = self.get_project_by_id(project_id)
        if project:
            project["name"] = name
            project["description"] = description
            project["status"] = status

    def delete_project(self, project_id):
        """Delete a project"""
        project = self.get_project_by_id(project_id)
        if project:
            self.projects.remove(project)
            return True
        return False
