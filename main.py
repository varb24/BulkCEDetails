import logging
import pandas as pd
from pydantic import BaseModel

"""
Requirements:
1) Validate individual rows; output rows that lack information and what they are missing.
2) Collect the fields that are missing data.
3) Pass through the parts that are complete.
4) Return the parts that are missing information, and the details on what fields are missing.
"""
class CEDetail(BaseModel):
    approval_org : str


def validate_required_columns(df, all_fields):
    """Ensures all columns are present in the document"""
    sheet_titles = set()
    for col in df.columns:
        sheet_titles.add(col)
    missing = set(all_fields) - sheet_titles
    if missing:
        raise KeyError(f'Missing required column(s): {", ".join(missing)}')



def main():
    # 1. Configure logging to show INFO+ messages
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    #
    REQUIRED_FIELDS = ['Approval Organization', 'CE Hours/Contact Hours', 'Offering ID', 'Date Start', 'Date Stop']
    OPTIONAL_FIELDS = ['Levels', 'CE Broker State', 'Areas']

    # Holds invalid data
    report = {}

    # 2. Read CSV directly
    df = pd.read_csv('./sample_data/sample_testing.csv')

    # allows numbered indexes for each row
    df = df.reset_index().rename(columns={'index': 'row_id'})
    validate_required_columns(df, REQUIRED_FIELDS + OPTIONAL_FIELDS)
    # 3. Log the DataFrame content
    #    Prepend a newline so the table prints nicely
    logging.info("\n%s", df.to_string(index=False))

    malformed_rows = {}
    # Extract rows whose data is missing important information.
    # 1) Tests for missing fields, each row in missing_import_rows has at least one blank (NaN) required field.
    mask = df[REQUIRED_FIELDS].isna().any(axis=1)
    missing_import_rows = df[mask]
    logging.info(f'Malformed rows {missing_import_rows}')
    # 2) Tests for missing invalid information
    # This implementation is good for small datasets(thousands of rows.)
    for idx, row in df.iterrows():
        # `row` is a Series
        # find fields with bad information.
        logging.info(f'Verifying information for id: {row['row_id']}')
    print("Done reading and logging DataFrame.")


if __name__ == "__main__":
    logging.info(main())
