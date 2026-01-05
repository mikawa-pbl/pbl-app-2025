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
            tex_content = r"""\documentclass{article}
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

            # Create .latexmkrc
            latexmkrc_content = """$latex = 'uplatex';
$bibtex = 'upbibtex';
$dvipdf = 'dvipdfmx %O -o %D %S';
$makeindex = 'mendex -U %O -o %D %S';
$pdf_mode = 3;
"""
            ProjectFile.objects.create(
                project=project,
                filename=".latexmkrc",
                content=latexmkrc_content,
                is_main=False
            )
            self.stdout.write("Created .latexmkrc")
        else:
             self.stdout.write(f"Project '{project.name}' already exists.")
