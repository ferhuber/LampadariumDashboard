from flask import Flask, request, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm  # Import FlaskForm here
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
import pandas as pd
import sqlite3
import os

class UploadForm(FlaskForm):
    file = FileField('File', validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!')])
    submit = SubmitField('Upload')

class MonthYearForm(FlaskForm):
    month = SelectField('Month', choices=[('1', 'January'), ('2', 'February'), ...], validators=[DataRequired()])
    year = SelectField('Year', choices=[('2021', '2021'), ('2022', '2022'), ...], validators=[DataRequired()])
    submit = SubmitField('Submit')


app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = os.environ.get('FLASK_APP_SECRET_KEY', '15mWeYc76LTo0cUk')



# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for the about page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for the contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route to upload CSV file
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        df = pd.read_csv(file, usecols=['DATE', 'ID', 'TRANSACTION', 'CATEGORY', 'AMOUNT'])
        
        # Drop rows with any missing values
        df = df.dropna(how='any')

        # Connect to the SQLite database
        conn = sqlite3.connect('database/transactions.db')

        # Check for existing IDs in the database and remove them from the DataFrame
        existing_ids = pd.read_sql_query('SELECT ID FROM transactions', conn)
        df = df[~df['ID'].isin(existing_ids['ID'])]

        # Write the remaining new data to the 'transactions' table
        df.to_sql('transactions', conn, if_exists='append', index=False)

        conn.close()
        flash('File successfully uploaded and data added to the database.', 'success')
        return redirect(url_for('show_transactions'))
    return render_template('upload.html', form=form)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


# Route to display transactions
@app.route('/transactions')
def show_transactions():
    conn = sqlite3.connect('database/transactions.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions ")
    transactions = cursor.fetchall()

    conn.close()
    return render_template('transactions.html', transactions=transactions)

# Route to add a new transaction (example of a form submission)
@app.route('/add-transaction', methods=['POST'])
def add_transaction():
    if request.method == 'POST':
        date = request.form['date']
        transaction = request.form['transaction']
        category = request.form['category']
        amount = request.form['amount']
        # ... get other fields similarly

        conn = sqlite3.connect('database/transactions.db')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO transactions (date, transaction, category, amount, ...)
            VALUES (?, ?, ?, ?, ...)
        """, (date, transaction, category, amount, ...))

        conn.commit()
        conn.close()

        return redirect(url_for('show_transactions'))

# Route to dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    conn = sqlite3.connect('database/transactions.db')
    cursor = conn.cursor()

    # Initialize the base queries for expenses and income
    base_expense_query = "SELECT * FROM transactions WHERE \"TRANSACTION\" LIKE '%Expense%'"
    base_income_query = "SELECT * FROM transactions WHERE \"TRANSACTION\" LIKE '%Income%'"

    specific_month_selected = False
    selected_month = None

    if request.method == 'POST':
        month = request.form.get('month')
        year = request.form.get('year')
        
        if 'reset' in request.form:
            # Reset button was pressed; show data for all months
            specific_month_selected = False
            expense_query = base_expense_query
            income_query = base_income_query
            selected_month = None

            print(selected_month)
        elif month and year:
            # A specific month is selected
            specific_month_selected = True
            selected_month = month

            # Apply filters only for the selected month
            month_year_filter = f" AND SUBSTR(DATE, 4, 3) = '{month}' AND SUBSTR(DATE, 8, 2) = '{year}'"
            expense_query = base_expense_query + month_year_filter
            income_query = base_income_query + month_year_filter
        else:
            # No specific month selected, use base queries
            expense_query = base_expense_query
            income_query = base_income_query
    else:
        # Default case when the page is first loaded
        expense_query = base_expense_query
        income_query = base_income_query

    # Execute the queries for expenses and income
    cursor.execute(expense_query)
    expenses = cursor.fetchall()
    cursor.execute(income_query)
    income = cursor.fetchall()

    # Initialize arrays for chart data
    expenses_by_month = [0] * 12
    income_by_month = [0] * 12

    # Query to fetch monthly expense and income data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for i, month_str in enumerate(months, start=1):
        # Query for expenses
        cursor.execute("SELECT SUM(CAST(REPLACE(amount, ',', '') AS REAL)) FROM transactions WHERE \"TRANSACTION\" LIKE '%Expense%' AND SUBSTR(date, 4, 3) = ?", (month_str,))
        expenses_by_month[i-1] = cursor.fetchone()[0] or 0

        # Query for income
        cursor.execute("SELECT SUM(CAST(REPLACE(amount, ',', '') AS REAL)) FROM transactions WHERE \"TRANSACTION\" LIKE '%Income%' AND SUBSTR(date, 4, 3) = ?", (month_str,))
        income_by_month[i-1] = cursor.fetchone()[0] or 0

    conn.close()

    # Preparing chart data with real values
    chart_data = {
        'months': months,
        'expenses': expenses_by_month,
        'income': income_by_month
    }

    return render_template('dashboard.html', expenses=expenses, income=income, chart_data=chart_data, specific_month_selected=specific_month_selected, selected_month=selected_month)

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)