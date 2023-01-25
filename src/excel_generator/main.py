from src.excel_generator import ExcelTasksGenerator


class ExcelMainGenerator(ExcelTasksGenerator):
    """Главный генератор excel отчётов."""

    ...


excel_generator = ExcelMainGenerator()
