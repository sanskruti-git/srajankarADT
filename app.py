from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key="NOOOB"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/final_project'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(80), nullable=False)

#     def __repr__(self):
#         return '<User %r>' % self.email

db_config = {
    'host': 'sansadtproject.c3eo642a4kqa.us-east-2.rds.amazonaws.com',
    'user': 'admin',
    'password': 'root1234',
    'database': 'final_project',
    'port':'3306'
}

conn = mysql.connector.connect(**db_config)
USER_CREDENTIALS = {
    'email': 'user@example.com',
    'password': 'password123'
}

@app.route('/')
def login_page():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # SQL query to find the user with the given email and password
        query = "SELECT * FROM Users WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return redirect(url_for('display'))
        else:
           flash('Login Unsuccessful. Please check username and password', 'error')
        return redirect(url_for('login_page'))

    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print(request.form)
        full_name = request.form['fullName']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        if password != confirm_password:
            print("Password mismatch")
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('register_form'))

        # # Hash the password
        # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO Users (full_name, email, password) 
                VALUES (%s, %s, %s)
            """
            print("performing insert")
            cursor.execute(insert_query, (full_name, email,password))
            conn.commit()
            print("Insert successfull")
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('display'))
        except Error as e:
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('register_form'))
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('register.html')

@app.route('/stock-form')
def stock_form():
    return render_template('stock-form.html')

@app.route('/register_form')
def register_form():
    return render_template('register.html')


@app.route('/display')
def display():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM nifty_500")
    data_rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('display.html', data_rows=data_rows)



# Define the route that handles the form submission
@app.route('/submit-stock', methods=['POST'])
def submit_stock():
    print("Inside")
    # Get data from form
    companyName = request.form['companyName']
    symbol = request.form['symbol']
    industry = request.form['industry']
    series = request.form['series']
    open_price = float(request.form['open'])
    high = float(request.form['high'])
    low = float(request.form['low'])
    previousClose = float(request.form['previousClose'])
    lastTradedPrice = float(request.form['lastTradedPrice'])
    change = float(request.form['change'])
    percentageChange = float(request.form['percentageChange'])
    shareVolume = int(request.form['shareVolume'])
    valueInRupees = float(request.form['valueInRupees'])
    fiftyTwoWeekHigh = float(request.form['fiftyTwoWeekHigh'])
    fiftyTwoWeekLow = float(request.form['fiftyTwoWeekLow'])
    threeSixFiveDayPercentageChange = float(request.form['threeSixFiveDayPercentageChange'])
    thirtyDayPercentageChange = float(request.form['thirtyDayPercentageChange'])


  

    # Connect to the database
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # SQL INSERT statement
        sql_insert_query = """
        INSERT INTO nifty_500 (companyName, symbol, industry, series, open, high, low, previousClose, 
                               lastTradedPrice, changeInPrice, percentageChange, shareVolume, valueInRupees, 
                               fiftyTwoWeekHigh, fiftyTwoWeekLow, threeSixFiveDayPercentageChange, 
                               thirtyDayPercentageChange) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data_tuple = (companyName, symbol, industry, series, open_price, high, low, previousClose,
                      lastTradedPrice, change, percentageChange, shareVolume, valueInRupees,
                      fiftyTwoWeekHigh, fiftyTwoWeekLow, threeSixFiveDayPercentageChange,
                      thirtyDayPercentageChange)
        print(sql_insert_query)
        # Execute the query
        cursor.execute(sql_insert_query, data_tuple)
        print("success")
        conn.commit()

        # Redirect or respond after successful insertion
        return redirect(url_for('display'))  # Redirect to a success page, if you have one

    except Error as e:
        print("Error while connecting to MySQL", e)
        return str(e)  # Return error message

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/edit-stock/<int:stock_id>', methods=['GET'])
def edit_stock(stock_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM nifty_500 WHERE stock_id = %s", (stock_id,))
    data = cursor.fetchone()

    cursor.close()
    conn.close()

    if data is None:
        return "Record not found", 404

    return render_template('edit_stock.html', data=data)

@app.route('/update-stock/<int:stock_id>', methods=['POST'])
def update_stock(stock_id):
    # Extract data from form
    companyName = request.form['companyName']
    symbol = request.form['symbol']
    industry = request.form['industry']
    series = request.form['series']
    open_price = request.form['open']
    high = request.form['high']
    low = request.form['low']
    previousClose = request.form['previousClose']
    lastTradedPrice = request.form['lastTradedPrice']
    changeInPrice = request.form['changeInPrice']
    percentageChange = request.form['percentageChange']
    shareVolume = request.form['shareVolume']
    valueInRupees = request.form['valueInRupees']
    fiftyTwoWeekHigh = request.form['fiftyTwoWeekHigh']
    fiftyTwoWeekLow = request.form['fiftyTwoWeekLow']
    threeSixFiveDayPercentageChange = request.form['threeSixFiveDayPercentageChange']
    thirtyDayPercentageChange = request.form['thirtyDayPercentageChange']
   
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    update_query = """
    UPDATE nifty_500
    SET companyName = %s, symbol = %s, industry = %s, series = %s, open = %s, high = %s, low = %s, previousClose = %s,
                      lastTradedPrice = %s, changeInPrice = %s, percentageChange = %s, shareVolume = %s, valueInRupees = %s,
                      fiftyTwoWeekHigh = %s, fiftyTwoWeekLow = %s, threeSixFiveDayPercentageChange = %s,
                      thirtyDayPercentageChange= %s
    WHERE stock_id = %s
    """
    cursor.execute(update_query, (companyName, symbol,  industry, series, open_price, high, low, previousClose,
                      lastTradedPrice, changeInPrice, percentageChange, shareVolume, valueInRupees,
                      fiftyTwoWeekHigh, fiftyTwoWeekLow, threeSixFiveDayPercentageChange,
                      thirtyDayPercentageChange, stock_id))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('display'))  # Assuming you have a route to display all records

@app.route('/delete-stock/<int:stock_id>', methods=['POST'])
def delete_stock(stock_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # SQL DELETE statement
        sql_delete_query = "DELETE FROM nifty_500 WHERE stock_id = %s"
        cursor.execute(sql_delete_query, (stock_id,))

        conn.commit()
        flash('Record has been deleted successfully!', 'success')
    except Error as e:
        print("Error while connecting to MySQL", e)
        flash('Error during deletion: ' + str(e), 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('display'))  # Redirect to the display page



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True)

