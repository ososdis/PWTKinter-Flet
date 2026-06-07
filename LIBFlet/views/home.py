import flet as ft
from services import LibraryService


class MainView(ft.Column):
    def __init__(self, service: LibraryService, on_select):
        super().__init__(
            expand=True,
            scroll=ft.ScrollMode.ALWAYS,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        self.service, self.on_select = service, on_select

    def build(self):
        self.search = ft.TextField(
            label="Rechercher...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.load,
            expand=True,
        )
        self.button = ft.Button("Ajouter Librarie", on_click=self.ajouter_lib)
        self.new_lib = ft.TextField("New Library", expand=True)
        self.add_lib = ft.Column(controls=[self.new_lib, self.button], expand=True)
        self.list = ft.Column(expand=True)
        self.controls = [
            ft.Text("Gestionnaire", size=24),
            self.search,
            self.add_lib,
            self.list,
        ]

    def did_mount(self):
        """Appelé automatiquement quand le composant est ajouté à la page"""
        self.load()

    def load(self, e=None):
        libs = self.service.fetch_libraries(self.search.value or "")
        self.list.controls = [
            ft.ListTile(
                title=ft.Text(lib.name),
                on_click=lambda _, lid=lib.id: self.on_select(lid),
            )
            for lib in libs
        ]
        self.update()

    def ajouter_lib(self):
        self.service.add_new_lib(self.new_lib.value)
        self.load()
