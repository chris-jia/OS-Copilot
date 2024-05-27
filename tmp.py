from openpyxl import load_workbook
from openpyxl.chart import BarChart, Reference

# Load the workbook
file_path = '/home/user/WeeklySales.xlsx'
wb = load_workbook(file_path)

# Select the new sheet
new_sheet = wb["Sheet2"]

# Create a reference for the data
data = Reference(new_sheet, min_col=2, min_row=1, max_col=3, max_row=5)
categories = Reference(new_sheet, min_col=1, min_row=2, max_row=5)

# Create the bar chart
chart = BarChart()
chart.add_data(data, titles_from_data=True)
chart.set_categories(categories)
chart.title = "Sales & COGS"
chart.style = 10
chart.x_axis.title = "Week"
chart.y_axis.title = "Amount"

# Add the chart to the sheet
new_sheet.add_chart(chart, "E5")

# Save the workbook to ensure the chart is added
wb.save(file_path)

print("Clustered column chart added to 'Sheet2' successfully.")
