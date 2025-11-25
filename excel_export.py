import pandas as pd

def export_excel(df, distributor, filename):
    """
    Export DataFrame to Excel with numeric formatting (comma, no decimals) 
    and auto column width.
    """
    df = df.copy()

    # Create Excel writer
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=distributor, index=False)
        workbook = writer.book
        worksheet = writer.sheets[distributor]

        # Define format: comma-separated, zero decimals
        number_format = workbook.add_format({'num_format': '#,##0'})

        # Apply formatting only to numeric columns
        for idx, col in enumerate(df.columns):
            if pd.api.types.is_numeric_dtype(df[col]):
                worksheet.set_column(idx, idx, 15, number_format)
            else:
                worksheet.set_column(idx, idx, 18)  # wider for text

        writer.save()
