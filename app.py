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

# Route to dasboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    conn = sqlite3.connect('database/transactions.db')
    cursor = conn.cursor()

    # Base queries
    expense_query = "SELECT * FROM transactions WHERE \"TRANSACTION\" LIKE '%Expense%'"
    income_query = "SELECT * FROM transactions WHERE \"TRANSACTION\" LIKE '%Income%'"

    if request.method == 'POST':
        month = request.form.get('month')  # Expecting 'Jan', 'Feb', 'Mar', etc.
        year = request.form.get('year')    # Expecting '23' for 2023, for example

        if month and year:
            expense_query += f" AND SUBSTR(DATE, 4, 3) = '{month}' AND SUBSTR(DATE, 8, 2) = '{year}'"
            income_query += f" AND SUBSTR(DATE, 4, 3) = '{month}' AND SUBSTR(DATE, 8, 2) = '{year}'"


            # Print the final SQL queries for debugging
    print("Expense Query:", expense_query)
    print("Income Query:", income_query)

    cursor.execute(expense_query)
    expenses = cursor.fetchall()

    cursor.execute(income_query)
    income = cursor.fetchall()

    conn.close()

    return render_template('dashboard.html', expenses=expenses, income=income)






if __name__ == '__main__':
    app.run(debug=True)
