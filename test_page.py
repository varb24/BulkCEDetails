import os
import tempfile
from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
from test_frictionless import (
    validate_csv,
    extract_error_rows,
    extract_row_data,
    combine_error_and_data,
)

from BulkCEDetailsAPI.templates.fix_rows import TEMPLATE

app = Flask(__name__)

ORIGINAL        = "./sample_data/sample_testing.csv"
FIXED_OUTPUT    = "./sample_data/sample_testing_fixed.csv"
SCHEMA_LOCATION = "bulkCE_schema.json"

# Keep your “master” copy in memory
GLOBAL_DF = (
    pd.read_csv(ORIGINAL, dtype=str)  # force everything to string
      .fillna("")                     # turn any leftover NaN → ""
)


def validate_in_memory(df: pd.DataFrame):
    """Validate the dataframe via a temp CSV and return combined error+data info."""
    # dump to a temp CSV so your existing validator just works
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp.write(df.to_csv(index=False).encode())
        tmp.flush()
        temp_path = tmp.name

    try:
        # 1) run validation → Report
        report = validate_csv(temp_path, SCHEMA_LOCATION)
        # 2) pull out errors by row number
        errors_by_row = extract_error_rows(report)
        # 3) read original CSV rows for those row numbers
        rows_data    = extract_row_data(temp_path, errors_by_row)
        # 4) combine into your uniform structure
        return combine_error_and_data(errors_by_row, rows_data)
    finally:
        os.remove(temp_path)


@app.route("/", methods=["GET", "POST"])
def edit_errors():
    global GLOBAL_DF

    # 1) If this is a POST, apply the user’s edits immediately:
    if request.method == "POST":
        for field_name, new_val in request.form.items():
            # field_name is like "5__CE Hours/Contact Hours"
            row_str, col = field_name.split("__", 1)
            row_num = int(row_str)
            df_idx  = row_num - 2
            GLOBAL_DF.iat[df_idx, GLOBAL_DF.columns.get_loc(col)] = new_val

    # 2) Now validate *this* version of GLOBAL_DF:
    error_info = validate_in_memory(GLOBAL_DF)

    # 3) Build invalid_fields & error_rows from *this* report:
    # This data is used to generate the webpage.
    raw_invalid = {
        row_num: [e for e in info["errors"]]
        for row_num, info in error_info.items()
        if row_num != "file_level"
    }
    invalid_fields = {}
    for row_num, errors in raw_invalid.items():
        # collect any explicit field‐level errors
        fields = {e["field"] for e in errors if e.get("field")}

        if not fields:
            # no explicit fields → generic row error (BlankRow, PK, etc)
            # make every column (or just your required ones) editable:
            fields = {"Approval Organization", "CE Broker State",
                      "CE Hours/Contact Hours", "Offering ID",
                      "Date Start", "Date Stop"}
            # or, if you have a schema list: fields = set(REQUIRED_FIELDS)

        invalid_fields[row_num] = fields
    error_rows = {}
    for row_num in invalid_fields:
        df_idx = row_num - 2
        error_rows[row_num] = GLOBAL_DF.iloc[df_idx].to_dict()


    # 4) If it was a POST and *now* there are no errors, save & show success:
    if request.method == "POST" and not invalid_fields:
        GLOBAL_DF.to_csv(FIXED_OUTPUT, index=False)
        return (
            "<h1>All errors fixed 🎉</h1>"
            f"<p>Saved your clean file to <code>{FIXED_OUTPUT}</code></p>"
        )

    # 5) Otherwise (GET or still errors) render the form with the *current* data:
    return render_template_string(
        TEMPLATE,
        error_rows=error_rows,
        invalid_fields=invalid_fields,
    )


if __name__ == "__main__":
    app.run(debug=True)