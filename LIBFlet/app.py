import flet as ft
from models import SQLiteLibraryDAO
from services import LibraryService
from views import BookListScreen, GenUIChatApp, MainView

# ==========================================
# 6. APP RUNNER
# ==========================================


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    # service = LibraryService(SQLiteDAO(), SimpleLogger())
    db: str = "database.db"
    service = LibraryService(SQLiteLibraryDAO(db_path=db))

    def router(lib_id=None):
        page.controls.clear()
        if lib_id:
            page.add(BookListScreen(service, lib_id, on_back=router))
        else:
            page.add(MainView(service, on_select=router))
            page.add(GenUIChatApp())

        page.update()

    router()


ft.run(main)
