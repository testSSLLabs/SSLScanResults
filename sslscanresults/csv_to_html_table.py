# CSV to HTML Table
import pandas as pd

def csv_to_html_table(csv_file_location, html_file_location):
    a = pd.read_csv(csv_file_location, index_col=False)
    # save as html file
    a.to_html(html_file_location)
 
    html_file = a.to_html()
