from src.excel_generator import ExcelTasksGenerator, ExcelTestGenerator


class ExcelMainGenerator(ExcelTestGenerator, ExcelTasksGenerator):
    """Главный генератор excel отчётов."""

    ...


excel_generator = ExcelMainGenerator()
