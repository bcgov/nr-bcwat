get_licence_import_dates_query = f"""
    SELECT
        dataset,
        import_date
    FROM
        bcwat_lic.bc_data_import_date
"""
