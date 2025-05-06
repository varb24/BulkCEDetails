import logging
import pandas as pd

"""
Requirements:
1) Validate individual rows; output rows that lack information and what they are missing.
2) Collect the fields that are missing data.
3) Pass through the parts that 
"""
def validate_required_fields(df, required_fields):
    missing = required_fields - set(df.columns)
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
    REQUIRED_FIELDS = {'approval organization', 'ce hours/contact hours', 'offering id', 'date start', 'date stop'}
    OPTIONAL_FIELDS = {'levels', 'ce broker state', 'areas'}


    # 2. Read CSV directly
    df = pd.read_csv('./sample_data/sample_1.csv')
    validate_required_fields(df, REQUIRED_FIELDS)
    # 3. Log the DataFrame content
    #    Prepend a newline so the table prints nicely
    logging.info("\n%s", df.to_string(index=False))

    # You can still use print if you just want to see something simple
    print("Done reading and logging DataFrame.")

    for col in df:
        print(col)
if __name__ == "__main__":
    logging.info(main())
