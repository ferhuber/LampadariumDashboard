from flask import Flask, request, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm  # Import FlaskForm here
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
import pandas as pd
import sqlite3
import os
import calendar

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
        df = pd.read_csv(file)
        
        # Clean and convert the 'Amount' column
        df['Amount'] = (
            df['Amount']
            .replace('[\$,]', '', regex=True)  # Remove dollar signs and commas
            .replace('[(]', '-', regex=True)   # Replace opening parenthesis with minus
            .replace('[)]', '', regex=True)    # Remove closing parenthesis
            .astype(float)                     # Convert to float
        )
        
        # Assuming the second "Account" column should be named 'related_account'
        df.columns = [
            'date', 'transaction_type', 'number', 'posting', 'name',
            'location', 'description', 'account', 'related_account', 'amount'
        ]
        
        # Drop rows where all elements are NaN (or None)
        df.dropna(how='all', inplace=True)

        # Drop duplicates based on a subset of columns that should be unique
        # Adjust the subset list based on your data and requirements
        df.drop_duplicates(subset=['date', 'transaction_type', 'number', 'name', 'account', 'related_account', 'amount'], inplace=True)

        
        # Connect to the SQLite database and insert data
        with sqlite3.connect('database/quickbooks.db') as conn:
            df.to_sql('quickbooks_transactions', conn, if_exists='append', index=False)

        flash('File uploaded and data inserted successfully!')
        return redirect(url_for('view_transactions'))
    
    return render_template('upload.html', form=form)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


# Route to display transactions
@app.route('/transactions')
def view_transactions():
    conn = sqlite3.connect('database/quickbooks.db')
    conn.row_factory = sqlite3.Row  # This will enable column access by name
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM quickbooks_transactions")
    transactions_data = cursor.fetchall()

   

    conn.close()

    return render_template('transactions.html', transactions=transactions_data)





# Route to add a new transaction (example of a form submission)
@app.route('/add-transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        # Extract data from form submission
        date = request.form['date']
        transaction_type = request.form['transaction_type']
        number = request.form.get('number')  # Optional field
        posting = request.form['posting']
        name = request.form['name']
        location = request.form.get('location')  # Optional field
        description = request.form['description']
        account = request.form['account']
        related_account = request.form.get('related_account')  # Optional field
        amount = request.form['amount'].replace(',', '').replace('$', '').replace('(', '-').replace(')', '')

        # Convert amount to float
        try:
            amount = float(amount)
        except ValueError:
            flash('Invalid amount format.')
            return redirect(url_for('add_transaction'))

        # Connect to the database
        conn = sqlite3.connect('database/quickbooks.db')
        cursor = conn.cursor()

        # Insert the new transaction
        cursor.execute('''
            INSERT INTO quickbooks_transactions (
                date, transaction_type, number, posting, name,
                location, description, account, related_account, amount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, transaction_type, number, posting, name, location, description, account, related_account, amount))

        conn.commit()
        conn.close()

        flash('New transaction added successfully!')
        return redirect(url_for('view_transactions'))

    return render_template('transactions.html')


# Route to dashboard
from datetime import datetime

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    conn = sqlite3.connect('database/quickbooks.db')
    cursor = conn.cursor()

      # Initialize variables
    year_filter = ""

    # Get the current year
    current_year = str(datetime.now().year)

    # Check if year is posted, otherwise use current year
    actual_year = request.form.get('year', current_year)
    if actual_year:
        year_filter = f" AND SUBSTR(date, 7, 4) = '{actual_year}'"

    # Initialize the base queries with the year filter
    base_expense_query = f"SELECT * FROM quickbooks_transactions WHERE transaction_type LIKE '%Expense%' {year_filter}"
    base_income_query = f"SELECT * FROM quickbooks_transactions WHERE transaction_type LIKE '%Deposit%' {year_filter}"


    # Initialize variables
    total_expenses = 0
    total_income = 0
    specific_month_selected = False
    specific_year_selected = False
    selected_month = None
    expense_query = base_expense_query
    income_query = base_income_query
    aggregated_expenses = []  # For aggregated expenses by Name for a selected month
    aggregated_deposits = []  # Initialize for aggregated deposits
    
   
    
    if request.method == 'POST':
        month = request.form.get('month')
        year = request.form.get('year')

        if 'reset' in request.form:
            specific_month_selected = False
            selected_month = None
        elif month and year:
            # A specific month is selected
            specific_month_selected = True
            selected_month = month

            # Apply filters only for the selected month
            month_year_filter = f" AND SUBSTR(date, 4, 2) = '{month}' AND SUBSTR(date, 7, 4) = '{year}'"

            # Query for aggregated expenses
            aggregate_query = f"""
                SELECT Name, SUM(CAST(REPLACE(Amount, ',', '') AS REAL)) as TotalAmount
                FROM quickbooks_transactions
                WHERE transaction_type LIKE '%Expense%' {month_year_filter}
                GROUP BY Name
            """
            cursor.execute(aggregate_query)
            aggregated_expenses = cursor.fetchall()


            # Query for aggregated deposits
            aggregate_deposits_query = f"""
                SELECT Name, SUM(CAST(REPLACE(Amount, ',', '') AS REAL)) as TotalAmount
                FROM quickbooks_transactions
                WHERE transaction_type LIKE 'Deposit%' {month_year_filter}
                GROUP BY Name
            """
            cursor.execute(aggregate_deposits_query)
            aggregated_deposits = cursor.fetchall()
            

            expense_query += month_year_filter
            income_query += month_year_filter

    # Execute the queries for expenses and income
    cursor.execute(expense_query)
    expenses = cursor.fetchall()
    cursor.execute(income_query)
    income = cursor.fetchall()

    # Initialize arrays for chart data
    expenses_by_month = [0] * 12
    income_by_month = [0] * 12

    # Query to fetch monthly expense and income data
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    year = request.form.get('year')
    for i, month_str in enumerate(months, start=1):
       
       
        # Query for expenses dashboard chart
        cursor.execute("""
        SELECT SUM(CAST(REPLACE(amount, ',', '') AS REAL))
        FROM quickbooks_transactions
        WHERE transaction_type LIKE '%Expense%'
        AND SUBSTR(date, 4, 2) = ?
        AND SUBSTR(date, 7, 4) = ?
        """, (month_str, year))

        expenses_by_month[i-1] = cursor.fetchone()[0] or 0

        # Query for income dashboard chart
        cursor.execute("""
        SELECT SUM(CAST(REPLACE(amount, ',', '') AS REAL))
        FROM quickbooks_transactions
        WHERE transaction_type LIKE '%Deposit%'
          AND SUBSTR(date, 4, 2) = ?
          AND SUBSTR(date, 7, 4) = ?
    """, (month_str, year))
        
        income_by_month[i-1] = cursor.fetchone()[0] or 0

    conn.close()

    # Calculate total expenses and income
    total_expenses = sum(expenses_by_month)
    total_income = sum(income_by_month)

    # Summing the totals for expenses and income
    total_expenses = sum(expenses_by_month)
    total_income = sum(income_by_month)
    profit = total_income - total_expenses

    # Dashboard chart data with real values
    # Convert month numbers to names
    month_names = [calendar.month_name[int(month)] for month in months]

    chart_data = {
        'months': month_names,
        'expenses': expenses_by_month,
        'income': income_by_month
    }

    labels = [expense[0] for expense in aggregated_expenses]
    data = [expense[1] for expense in aggregated_expenses]
    DepositLabels = [income[0] for income in aggregated_deposits]
    DepositData = [income[1] for income in aggregated_deposits]

    return render_template('dashboard.html', expenses=expenses, 
                           income=income, 
                           chart_data=chart_data, 
                           specific_month_selected=specific_month_selected, 
                           selected_month=selected_month, 
                           total_expenses=total_expenses, 
                           total_income=total_income, 
                           profit=profit,
                           aggregated_expenses=aggregated_expenses,
                           aggregatedExpensesLabels=labels, 
                           aggregatedExpensesData=data,
                           aggregated_deposits=aggregated_deposits,
                           aggregatedDepositsLabels=DepositLabels, 
                           aggregatedDepositsData=DepositData,
                           year=year,
                           actual_year=actual_year)

if __name__ == '__main__':
    app.run(debug=True)

