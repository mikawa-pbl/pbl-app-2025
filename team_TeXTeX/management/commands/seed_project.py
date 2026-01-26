from django.core.management.base import BaseCommand
from team_TeXTeX.models import Project, ProjectFile, Users

class Command(BaseCommand):
    help = 'Seeds a dummy project for testing compilation'

    def handle(self, *args, **options):
        # Ensure Alice exists
        user, _ = Users.objects.get_or_create(user_id=1, defaults={'user': 'Alice'})
        
        # Create Project
        project, created = Project.objects.get_or_create(
            name="Hello World Project",
            defaults={'owner': user}
        )
        
        if created:
            self.stdout.write(f"Created project: {project.name}")
            
            # Create Main TeX File
            tex_content = r"""\documentclass{ltjsarticle}
\begin{document}
Hello, World!
\begin{equation}
E = mc^2
\end{equation}
\end{document}
"""
            ProjectFile.objects.create(
                project=project,
                filename="main.tex",
                content=tex_content,
                is_main=True
            )
            self.stdout.write("Created main.tex")


        else:
             self.stdout.write(f"Project '{project.name}' already exists.")
        
        # Ensure .latexmkrc exists regardless
        latexmkrc_content = """$latex = 'lualatex %O -synctex=1 -interaction=nonstopmode %S';
$bibtex = 'upbibtex';
$makeindex = 'mendex -U %O -o %D %S';
$pdf_mode = 4;
"""
        obj, created_rc = ProjectFile.objects.get_or_create(
            project=project,
            filename=".latexmkrc",
            defaults={'content': latexmkrc_content, 'is_main': False}
        )
        if created_rc:
            self.stdout.write("Created .latexmkrc (was missing)")
        else:
            self.stdout.write(".latexmkrc already exists")
            
        # Fix for ALL projects (including id=1)
        self.stdout.write("Checking all projects for .latexmkrc...")
        for p in Project.objects.all():
            obj, created_rc = ProjectFile.objects.get_or_create(
                project=p,
                filename=".latexmkrc",
                defaults={'content': latexmkrc_content, 'is_main': False}
            )
            if created_rc:
                self.stdout.write(f"Created .latexmkrc for project '{p.name}' (id={p.id})")
            else:
                 pass # already exists
