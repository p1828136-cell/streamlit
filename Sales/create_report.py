from io import BytesIO
import json
from pdf_funcs import (cm, A4, A5, landscape,
                       stringWidth, canvas,
                       fit_text_to_column, text_to_ar,
                       font)


# -- paths
headers = ["اسم الصنف", "كمية", "سعر", "اجمالي", "خصم", "صافي"]


result_file_name = "تقرير مبيعات.pdf"

new_columns = [headers]

with open(r'Sales/report_data.json', 'r', encoding='utf-8') as f:
    report_data = json.load(f)

paper_size = {"A4": {"s": A4, "h": 29.7*cm}, "A5": {"s": landscape(A5), "h": 14.85*cm}}
page_s = report_data["paper_size"]
page_h = paper_size[page_s]["h"]
page_s = paper_size[page_s]["s"]

report_inf: dict = report_data["report_inf"]
indexes: dict = {k: v * cm for k, v in report_data["indexes"].items()}

num_cells_per_page: int = report_inf["num_rows_page"]
cell_height: float = report_inf["cell_height"] * cm
columns_width: list = [c * cm for c in report_data["columns_sizes"]]
left_margin: float = (21 * cm - sum(columns_width)) / 2

columns_indexes: list = [left_margin]
s: float = left_margin
for c in columns_width:
    s += c
    columns_indexes.append(s)

# - - - - - - - - - - - - - - - - - - - -
def create_default_report(c: canvas.Canvas, page_inf: str, rows_num: int, from_date: str, to_date: str):
    rows_num = rows_num if rows_num > 0 else 13 - rows_num * -1
    inf_line_y = page_h - 2 * cm - rows_num * .7 * cm - 2.5 * cm

    # address
    c.setFont(font, report_inf["address_FS"])
    address_text = text_to_ar(f"تقرير مبيعات خلال فترة من {to_date} الى {from_date}")

    c.drawString(indexes["address_x"] - stringWidth(address_text, font, report_inf["address_FS"]) / 2,
                 indexes["address_y"]+page_h, address_text)

    # page_inf
    c.setFont(font, report_inf["page_inf_FS"])
    page_inf = text_to_ar(page_inf)
    c.drawString(indexes["page_inf_x"] - stringWidth(page_inf, font, report_inf["page_inf_FS"]) / 2,
                 inf_line_y, page_inf)

# - - - - - - - - - - - - - - - - - - - - execute - - - - - - - - - - - - - - - - - - - - #
def make_sales_form(from_date: str, to_date: str, rows: list[list]) -> BytesIO|None:
    rows_num: int = len(rows)

    # -- create pdf
    report_file = BytesIO()
    report_file.name = result_file_name
    c = canvas.Canvas(report_file, pagesize=page_s)  # create a pdf
    def create_row(row: int, cell_num: int):
        def create(cell, column: int):
            text = text_to_ar(str(cell) if cell is not None else " ")

            current_font_size = fit_text_to_column(text, font, columns_width[column], 11)

            c.setFont(font, current_font_size)
            x = columns_indexes[column]
            y = page_h - 2 * cm - cell_num * cell_height

            text_size = stringWidth(text, font, current_font_size)
            c.drawString((columns_indexes[column + 1] - x - text_size) / 2 + x, y, text)

            c.setFont(font, report_inf["table_FS"])
            c.rect(x, y - .3 * cm, columns_width[column], cell_height, stroke=1, fill=0)

        for column in range(6):
            create(rows[row][-(column+1)], column)
        create(row+1 if row != -1 else "م", 6)

    original_rows = rows
    last_index: int = -1
    page_num: int = 0
    max_report_rows: int = rows_num

    report_pages_num: int = max_report_rows // num_cells_per_page + (
        0 if max_report_rows % num_cells_per_page == 0 else 1)

    for page in range(1, report_pages_num + 1):
        if page < report_pages_num:
            page_rows_num: int = num_cells_per_page
        elif max_report_rows % num_cells_per_page == 0:
            page_rows_num: int = num_cells_per_page
        else:
            page_rows_num: int = max_report_rows % num_cells_per_page

        rows = new_columns
        create_row(-1, 1)
        rows = original_rows
        for cell_num in range(1, page_rows_num+1):
            create_row(last_index + cell_num + (page - 1) * num_cells_per_page, cell_num+1)

        create_default_report(c, "صفحة رقم" + f" {page} " + "من" + f" {report_pages_num}", page_rows_num, from_date, to_date)

        c.showPage()  # create new paper
        page_num += 1
    c.save()
    report_file.seek(0)
    return report_file
    # with open(save_path + result_file_name, "wb") as file:
    #     file.write(report_file.getvalue())
    # os.startfile(save_path + result_file_name)
