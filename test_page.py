import os
import tempfile
from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
from test_frictionless import extract_and_save_errors
from BulkCEDetailsAPI.templates.fix_rows import TEMPLATE

app = Flask(__name__)

ORIGINAL        = "./sample_data/sample_testing.csv"
FIXED_OUTPUT    = "./sample_data/sample_testing_fixed.csv"
SCHEMA_LOCATION = "bulkCE_schema.json"

# Keep your “master” copy in memory
GLOBAL_DF = pd.read_csv(ORIGINAL)

def validate_in_memory(df: pd.DataFrame):
    # dump to a temp CSV so your existing validator just works
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp.write(df.to_csv(index=False).encode())
        tmp.flush()
        temp_path = tmp.name

    try:
        return extract_and_save_errors(temp_path, SCHEMA_LOCATION) or {}
    finally:
        os.remove(temp_path)

@app.route("/", methods=["GET", "POST"])
def edit_errors():
    global GLOBAL_DF

    # 1) re-validate
    error_info = validate_in_memory(GLOBAL_DF)

    # 2) collect only the row-level errors
    invalid_fields = {
        row_num: { e["field"] for e in info["errors"] if e.get("field") }
        for row_num, info in error_info.items()
        if row_num != "file_level"
    }

    # 3) build the actual row data from GLOBAL_DF,
    #    mapping the validator’s row_number → dataframe row
    error_rows = {}
    for row_num in invalid_fields:
        # note: your validator uses row_number starting at 2 for the first data row
        df_idx = row_num - 2
        if 0 <= df_idx < len(GLOBAL_DF):
            error_rows[row_num] = GLOBAL_DF.iloc[df_idx].to_dict()

    if request.method == "POST":
        # 4) apply the edits into GLOBAL_DF
        for field_name, new_val in request.form.items():
            row_str, col = field_name.split("__", 1)
            row_num = int(row_str)
            df_idx  = row_num - 2
            GLOBAL_DF.iat[df_idx, GLOBAL_DF.columns.get_loc(col)] = new_val

        # 5) re-validate and check if any row errors remain
        error_info = validate_in_memory(GLOBAL_DF)
        still_invalid = [
            rn for rn in error_info.keys() if rn != "file_level"
        ]
        if not still_invalid:
            GLOBAL_DF.to_csv(FIXED_OUTPUT, index=False)
            return (
                "<h1>All errors fixed 🎉</h1>"
                f"<p>Saved your clean file to <code>{FIXED_OUTPUT}</code></p>"
            )

        # otherwise, fall through and re-render the form

    # 6) render only those remaining error rows
    return render_template_string(
        TEMPLATE,
        error_rows=error_rows,
        invalid_fields=invalid_fields,
    )

if __name__ == "__main__":
    app.run(debug=True)
