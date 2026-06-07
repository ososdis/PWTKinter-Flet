from typing import Callable, cast

import flet as ft
from models import LibraryDTO
from services import LibraryService

#
# 5. UI (Adaptateur sortie)
#


class BookDetailView(ft.Container):
    def __init__(
        self, book_id: int, title: str, service: LibraryService, refresher: Callable
    ) -> None:
        super().__init__(expand=True)
        self.service = service
        self.book_id = book_id
        self.title = title
        self.refresher = refresher
        self.display_text = ft.Text(
            self.title, on_tap=self.set_edit_mode, selectable=True
        )
        self.edit_book = ft.TextField(title)

    def did_mount(self):
        self.content = self.display_text
        self.update()

    def save_edit(self, e):
        # Update display text with new input value
        self.title = self.edit_book.value
        self.update_book()
        self.content = self.display_text
        self.refresher()

    def set_edit_mode(self, e):
        # Toggle text field
        self.content = ft.Row(
            [
                self.edit_book,
                ft.IconButton(icon=ft.Icons.CHECK, on_click=self.save_edit),
            ]
        )
        self.update()

    def update_book(self):
        try:
            self.service.edit_book(self.title, self.book_id)
        except ValueError as err:
            self.page.show_dialog(ft.SnackBar(ft.Text(str(err))))
            self.update


class BookListScreen(ft.Column):
    def __init__(self, service: LibraryService, lib_id: int, on_back):
        super().__init__(expand=True)
        self.service, self.lib_id, self.on_back = service, lib_id, on_back
        self.tf = ft.TextField(label="Nouveau Livre", expand=True)

    def did_mount(self):
        """Appelé automatiquement quand le composant est ajouté à la page"""
        self.refresh()

    def refresh(self) -> None:
        lib: LibraryDTO | None = self.service.get_details(self.lib_id)

        if lib:
            new_controls = cast(
                list[ft.Control],
                [
                    ft.TextButton("← Retour", on_click=lambda _: self.on_back()),
                    ft.Text(
                        f"Collection : {lib.name if lib else ''}",
                        size=25,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row([self.tf, ft.IconButton(ft.Icons.ADD, on_click=self.add)]),
                    ft.Column(
                        [
                            ft.ListTile(
                                title=BookDetailView(
                                    book_id=b.id,
                                    title=b.title,
                                    service=self.service,
                                    refresher=self.refresh,
                                )
                            )
                            for b in lib.books
                        ],
                        scroll=ft.ScrollMode.ALWAYS,
                        expand=True,
                    )
                    if lib.books
                    else ft.Text("No books yet"),
                ],
            )

            self.controls = new_controls
            self.update()

    def add(self, e):
        try:
            self.service.create_book(self.tf.value, self.lib_id)
            self.tf.value = ""
            self.refresh()
        except ValueError as err:
            self.page.show_dialog(ft.SnackBar(ft.Text(str(err))))
            self.refresh()
