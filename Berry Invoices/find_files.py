from pathlib import Path


def find_care_notes(folder_path, date, patient_name):
    # Construct expected file name
    expected_file_name = f"Care Notes - {date} - {patient_name}.pdf"

    # Check if the file exists in the folder
    file_path = Path(folder_path) / expected_file_name
    return file_path if file_path.exists() else None


def find_invoices(folder_path, date, patient_name):
    # Construct expected file name
    expected_file_name = f"Invoice - {date} - {patient_name}2.pdf"

    # Check if the file exists in the folder
    file_path = Path(folder_path) / expected_file_name
    return file_path if file_path.exists() else None
