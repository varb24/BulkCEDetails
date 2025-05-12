TEMPLATE = """
<!doctype html>
<html>
  <head>
    <title>Fix Error Rows</title>
    <style>
      .error {
        border: 2px solid red;
        background-color: #ffe6e6;
      }
      input:disabled {
        background-color: #f5f5f5;
        color: #666;
      }
      fieldset { margin-bottom: 1.5em; padding: 1em; }
      label { display: inline-block; width: 150px; font-weight: bold; }
      input { width: 300px; }
    </style>
  </head>
  <body>
    <h1>Rows with Errors</h1>
    <form method="post">
      {% for idx, row in error_rows.items() %}
        <fieldset>
          <legend>Row {{ idx }}</legend>
          {% for col, val in row.items() %}
            {% set is_error = col in invalid_fields[idx] %}
            <div>
              <label for="{{ idx }}__{{ col }}">{{ col }}</label>
              <input
                type="text"
                id="{{ idx }}__{{ col }}"
                name="{{ idx }}__{{ col }}"
                value="{{ val|e }}"
                class="{% if is_error %}error{% endif %}"
                {% if not is_error %}disabled{% endif %}
              />
            </div>
          {% endfor %}
        </fieldset>
      {% endfor %}
      <button type="submit">Save Changes</button>
    </form>
  </body>
</html>
"""