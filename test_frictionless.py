# from frictionless import validate
#
# # 1. Validate
# report = validate(
#     "./sample_data/sample_testing.csv",
#     schema="bulkCE_schema.json",
# )
#
# # 2. Pull out all the errors
# #    report.tasks is a list of ReportTask objects; each has .errors (List[Error])
# row_issues = {}
# for task in report.tasks:
#     for error in task.errors:
#         # row number (always present for cell/row errors)
#         row = getattr(error, "row_number", None)
#         # some errors have field_name, some don't (PrimaryKeyError, RowError, etc.)
#         field = getattr(error, "field_name", None)
#         # use the .note or .message for human detail
#         note = getattr(error, "note", None) or getattr(error, "message", None)
#         # error type for quick classification
#         etype = error.type
#
#         # collect
#         row_issues.setdefault(row, []).append({
#             "type": etype,
#             "field": field,
#             "note": note,
#         })
#
# # 3. Print a summary
# for row, issues in sorted(row_issues.items()):
#     print(f"Row {row}:")
#     for issue in issues:
#         fld = issue["field"] or "<row-level>"
#         print(f"  • [{issue['type']}] {fld}: {issue['note']}")
import frictionless
from frictionless import validate, describe, extract
import csv
import json
from collections import defaultdict
import pprint

import logging

from google.api_core.client_logging import setup_logging

setup_logging()

def validate_csv(file_location, schema_location: str):
    """Returns a frictionless Report object."""

    # Run validation
    report = validate(
        file_location,
        schema=schema_location,
    )

    if report.valid:
        print("No validation errors found!")
        return report

    print(f"Found {len(report.tasks[0].errors)} errors")

    return report


def extract_row_data(data_source, errors_by_row):
    # Read the original CSV to get the data for rows with errors
    rows_data = {}
    try:
        with open(data_source, 'r', newline='') as f:
            reader = csv.DictReader(f)
            row_idx = 2  # Row 1 is header, data starts at row 2
            for row in reader:
                if row_idx in errors_by_row:
                    rows_data[row_idx] = row
                row_idx += 1
    except Exception as e:
        print(f"Error reading CSV: {e}, from data source: {data_source}")
        return {'error':'Could not read CSV file'}

    return rows_data


def extract_error_rows(report: frictionless.Report) -> dict:
    """Extract error row information from frictionless Report"""
    errors_by_row = defaultdict(list)

    for error in report.tasks[0].errors:
        # Handle errors without row_number attribute (like SchemeError)
        row_num = getattr(error, 'row_number', 0)  # Use 0 for errors not associated with a specific row
        error_type = type(error).__name__

        # Extract field name if available
        field_name = None
        if hasattr(error, 'field_name'):
            field_name = error.field_name
        elif hasattr(error, 'note') and 'field' in str(error.note):
            # Try to extract field name from note
            parts = str(error.note).split("'")
            if len(parts) > 1:
                field_name = parts[1]

        error_info = {
            "type": error_type,
            "message": error.message,
            "field": field_name
        }
        errors_by_row[row_num].append(error_info)

    return errors_by_row


def combine_error_and_data(errors_by_row, rows_data):
    """Takes row error data, and the actual data and returns a datastructure that combines the two"""
    result = {}
    try:
        print(f'Combining errors with row data.')
        for row_num, errors in errors_by_row.items():
            if row_num == 0:
                # Handle file-level or schema-level errors (not associated with specific rows)
                result['file_level'] = {
                    "data": {},
                    "errors": errors
                }
            elif row_num in rows_data:
                result[row_num] = {
                    "data": rows_data[row_num],
                    "errors": errors,
                    "error_columns": [{ f['field'] : rows_data.get(row_num).get(f['field'])} for f in errors if f['field'] is not None] # Turn this into a function dummy.
            }
            print(f'Printing intermediate results form combine error {result}')
    except KeyError as e:
        pprint.pp(f'Bad data access. Data dump\n {rows_data}\n{errors}\n {str(e)}')
        logging.error('wut', exc_info=True)
    except TypeError as e:
        pprint.pp(rows_data)
        pprint.pp(f'aah {[type(elem) for elem in rows_data[3]]} ')
        pprint.pp(f'\n{([type(elem) for elem in rows_data.values()])}')

    return result

def extract_and_save_errors(result, rows_data: dict) -> dict:
    """
    Extract errors from CSV validation and save them to files, returns a data structure that contains error rows
    and all validation information.
    """
    # Group errors by row number

    # Combine the errors with their row data

    # Save to JSON
    with open('validation_errors.json', 'w') as f:
        print(f'Saving validation')
        json.dump(result, f, indent=2)

    # Save to CSV for easier viewing
    try:
        with open('error_rows.csv', 'w', newline='') as f:
            if not result:
                print(f'failed to write error csv, result is empty.')
                return result

            # Get field names from first data row + error columns
            data_rows = {k: v for k, v in result.items() if k != 'file_level' and v["data"]}
            if not data_rows:
                print("No row-specific errors to write to CSV")
                return result

            first_row = next(iter(data_rows.values()))
            fieldnames = list(first_row["data"].keys())
            fieldnames.extend(['Error_Types', 'Error_Messages', 'Error_Fields'])

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for row_num, data in result.items():
                if row_num == 'file_level' or not data['data']:
                    continue  # Skip file-level errors in CSV output

                row_data = data['data'].copy()  # Copy row data

                # Add error information
                error_types = "; ".join([e["type"] for e in data['errors']])
                error_messages = "; ".join([e["message"] for e in data['errors']])
                error_fields = "; ".join([str(e["field"]) for e in data['errors'] if e["field"]])

                row_data['Error_Types'] = error_types
                row_data['Error_Messages'] = error_messages
                row_data['Error_Fields'] = error_fields

                writer.writerow(row_data)
    except Exception as e:
        print(f"Error writing CSV: {e}")

    print(f"Saved error data to validation_errors.json and error_rows.csv")

    # Print summary
    print("\nError Summary:")
    for row_num, data in result.items():
        if row_num == 'file_level':
            print(f"\nFile/Schema Level Errors:")
        else:
            print(f"\nRow {row_num}:")

        for error in data["errors"]:
            field = error["field"] if error["field"] else "<row-level>"
            print(f"  • {field}: {error['type']} - {error['message']}")

    return result


if __name__ == "__main__":
    valid_rows = []
    data_source = "./sample_data/sample_testing.csv"
    filename = data_source[data_source.find("/",2) + 1: -4]
    print(filename)

    schema_location = "bulkCE_schema.json"
    print(f'Starting data extraction')

    validated_report = validate_csv(data_source, schema_location)
    print(f'Validated report {validated_report}')
    invalid_rows = extract_error_rows(validated_report)
    print(f'Invalid rows {invalid_rows}')
    rows_data = extract_row_data(data_source, invalid_rows)
    print(f'Rows data {rows_data}')
    combined_data = combine_error_and_data(invalid_rows, rows_data)
    print(f'Combined data {combined_data}')
    result = extract_and_save_errors(combined_data, rows_data)

    # Provides basic information about csv data.
    #resource = describe(data_source)
    # Returns a dict where each row is dict from the CSV's non label rows.
    # all_rows = extract(data_source)
    # print([x for x in all_rows.keys()])
    # #exit()
    # all_row_data = all_rows[filename]
    # # print(resource)
    # print(all_rows)
    # #print(error_info)
    # print(error_info.keys())
    # # list all rows that do not contain error. Each row is a dictionary.
    # valid_rows = [x for idx, x in enumerate(all_rows[filename]) if idx not in error_info.keys() and idx != 0]
    # print(valid_rows)
