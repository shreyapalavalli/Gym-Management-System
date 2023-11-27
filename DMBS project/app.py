from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__, template_folder='templates')

# Replace these values with your MySQL database credentials
server = 'localhost'
database = 'gym_management_system'
username = 'root'
password = 'Shreyanp@2003'

# Create a MySQL connection
conn = pymysql.connect(
    host=server,
    user=username,
    password=password,
    database=database
)

cursor = conn.cursor()

# Placeholder for admin credentials (replace with a secure authentication mechanism)
admin_credentials = {'username': 'admin', 'password': 'admin123'}

# Placeholder for member credentials
member_credentials = {'username': 'member', 'password': 'member123'}

# Placeholder for member credentials
trainer_credentials = {'username': 'trainer', 'password': 'trainer123'}

# Define route for the login page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None  # Variable to store error messages

    if request.method == 'POST':
        # Retrieve form data
        username = request.form['username']
        password = request.form['password']

        # Check if it's the admin
        if username == admin_credentials['username'] and password == admin_credentials['password']:
            # Admin login
            return redirect(url_for('display_tables', role='admin'))
        
        # Check if it's the member
        elif username == member_credentials['username'] and password == member_credentials['password']:
            # Member login
            return redirect(url_for('display_tables', role='member'))
        
        # Check if it's the trainer
        elif username == trainer_credentials['username'] and password == trainer_credentials['password']:
            # Trainer login
            return redirect(url_for('display_tables', role='trainer'))

        else:
            error = "Wrong username or password. Please try again."

    return render_template('login.html', error=error)

# # Define route for member dashboard
# @app.route('/member-dashboard')
# def member_dashboard():
#     return render_template('member_dashboard.html')

# Define route for displaying tables
@app.route('/index/<role>')
def display_tables(role):
    print("Role received:", role)
    if role == 'admin':
        tables = ['Member', 'MembershipPlan', 'GymSession', 'Trainer', 'Equipment', 'Staff', 'Payments']
    elif role == 'member':
        tables = ['MembershipPlan','GymSession', 'Trainer', 'Equipment']
    else :
        tables = ['Member', 'MembershipPlan', 'GymSession', 'Equipment']


    tables_data = {}

    for table in tables:
        query = f'SELECT * FROM {table};'
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        tables_data[table] = {'columns': columns, 'rows': rows}

    return render_template('index.html', tables_data=tables_data, selected_table_name=None, selected_table_data=None, role=role)

# Define route for displaying a specific table
@app.route('/table/<table>')
def display_table(table):
    role = request.args.get('role')  # Get the role from the query parameters
    print("Role received in display_table:", role)
    query = f'SELECT * FROM {table};'
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    # Identify the primary key and its index in the columns
    primary_key = f'{table}_id'
    primary_key_index = columns.index(primary_key) if primary_key in columns else None

    selected_table_data = {'columns': columns, 'rows': rows, 'primary_key': primary_key, 'primary_key_index': primary_key_index}
    tables_data = {table: selected_table_data}  # Place the selected_table_data under the key of the table name
    return render_template('index.html', tables_data=tables_data, selected_table_name=table, selected_table_data=selected_table_data, role=role)

# Route to handle the update form submission
@app.route('/update/<table_name>', methods=['POST'])
def update(table_name):
    if request.method == 'POST':
        update_id = request.form.get('update_id')
        columns_to_update = request.form.getlist('columns_to_update[]')
        update_values = {}

        # Collect updated values from the form for the specified columns
        for column in columns_to_update:
            value = request.form.get(column)
            if value is not None:  # Check if the value is not null
                update_values[column] = value

        if not update_values:
            # No valid values to update, handle this case (e.g., display an error message)
            return redirect(url_for('display_table', table=table_name))

        # Generate the update query for the specified columns
        with conn.cursor() as cursor:
            update_query = f"UPDATE {table_name} SET "
            update_query += ", ".join([f"{column} = '{update_values[column]}'" for column in columns_to_update])
            update_query += f" WHERE {table_name}_id = {update_id}"

            # Execute the update query
            cursor.execute(update_query)

        conn.commit()

        # Redirect to the updated table
        return redirect(url_for('display_table', table=table_name, role='admin'))


# Route for inserting, updating, and deleting data
@app.route('/action/<action>/<table>', methods=['POST'])  # Set method to POST for delete
def handle_data(action, table):
    if request.method == 'POST' and request.form.get('_method') == 'PATCH':
        # Override the request method for updates
        request.environ['REQUEST_METHOD'] = 'PATCH'

    if action == 'insert':
        if request.method == 'POST':
            # Exclude 'role' from the list of columns and values
            columns = [column for column in request.form.keys() if column != '_method' and column != 'role']
            values = [request.form[column] for column in columns]
            
            placeholders = ', '.join(['%s'] * len(values))
            query = f'INSERT INTO {table} ({", ".join(columns)}) VALUES ({placeholders});'
            
            cursor.execute(query, values)
            conn.commit()

            # Get the role from the form data or set a default value
            role = request.form.get('role', 'admin')

            return redirect(url_for('display_tables', role=role))
    
    elif action == 'update':
        # Call the update function with the specified table name
        return update(table)


    elif action == 'delete':
        if request.method == 'POST':
            row_id = int(request.form['row_id'])
            primary_key_column = f'{table}_id'
            query = f'DELETE FROM {table} WHERE {primary_key_column} = %s;'
            cursor.execute(query, (row_id,))
            conn.commit()
            return redirect(url_for('display_tables', role='admin'))

    return redirect(url_for('display_tables'))

if __name__ == '__main__':
    app.run(debug=True)
