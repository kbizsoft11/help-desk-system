from flask import render_template, request, redirect, url_for, flash, session, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # Import db from __init__.py
from .models import User, Ticket
import os
import csv
from datetime import timedelta

# Define routes in a function so that they can be added to the app later


def init_app(app):

    # @app.before_request
    # def check_login():
    #     # Define the routes where user needs to be authenticated
    #     if 'user_id' not in session and request.endpoint not in ['login_page', 'register_page',]:
    #         flash("You must be logged in to view this page.", "error")
    #         return redirect(url_for('login_page'))

    @app.route('/')
    def index():
        # Check if the user is already logged in
        if 'user_id' in session:
            flash("You are already logged in", "success")
            return redirect(url_for('tickets'))

        return render_template('auth/login.html')

    @app.route('/register')
    def register_page():
        # Check if the user is already logged in
        if 'user_id' in session:
            flash("You are already logged in", "success")
            return redirect(url_for('tickets'))
        return render_template('auth/register.html')

    @app.route('/login')
    def login_page():
        # Check if the user is already logged in
        if 'user_id' in session:
            flash("You are already logged in", "success")
            return redirect(url_for('tickets'))

        # print("app.template_folder", app.template_folder)
        return render_template('auth/login.html')

    @app.route('/forgot-password')
    def forgot_password_page():
        # Check if the user is already logged in
        if 'user_id' in session:
            flash("You are already logged in", "success")
            return redirect(url_for('tickets'))

        return render_template('auth/forgot-password.html')

    @app.route('/profile')
    def profile_page():
        if 'user_id' not in session:
            flash("You must be logged in to view this page.", "error")
            return redirect(url_for('login_page'))

        # Get the current user's ID from the session
        current_user_id = session['user_id']

        # Fetch the user from the database based on the user_id
        user = User.query.get(current_user_id)

        # Check if the user exists
        if not user:
            flash("User not found.", "error")
            return redirect(url_for('login_page'))

        # Pass the user's details to the template
        return render_template('auth/profile.html', user=user)

    @app.route('/auth/forgot-password', methods=['POST'])
    def forgot_user_password():
        email = request.form.get('email')
        # Get password input from the user
        new_password = request.form.get('new_password')

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:

            # Check if the password length is less than 8 characters
            if len(new_password) < 8:
                flash("Password must be at least 8 characters long.", "error")
                return redirect(url_for('forgot_password_page'))

            # Generate a hashed password before storing it
            hashed_password = generate_password_hash(new_password)

            # Update the user's password in the database
            existing_user.password = hashed_password
            db.session.commit()  # Commit the changes to the database

            flash('Password updated successfully!',
                  'success')  # Success message
            # Redirect to login page after updating the password
            return redirect(url_for('login_page'))
        else:
            flash(
                'Email not found. Please check the email address and try again.', 'error')
            # Redirect back to the forgot password page
            return redirect(url_for('forgot_password_page'))

    @app.route('/auth/register', methods=['POST'])
    def user_register():
        username = request.form.get('username')
        email = request.form.get('email')
        # Get password input from the user
        password = request.form.get('password')
        role = 1  # 0 for admin, 1 for normal user

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please use a different email.',
                  'error')  # Show flash message
            return redirect(url_for('register_page'))

        # Check if the password length is less than 8 characters
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for('register_page'))

        # Hash the password using Werkzeug with the correct method
        hashed_password = generate_password_hash(
            password, method='pbkdf2:sha256')  # Correct hash method

        # Create the new user with the hashed password
        new_user = User(username=username, email=email,
                        password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session.permanent = True

        flash('Your registration was successfull',
              'success')  # Show success message
        return redirect(url_for('tickets'))

    @app.route('/auth/login', methods=['POST'])
    def user_login():
        email = request.form.get('email')
        password = request.form.get('password')

        # Find the user in the database by email
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not found.", "error")
            return redirect(url_for('login_page'))

        # Check if the password length is less than 8 characters
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for('login_page'))

        # Check if the password matches the hashed password in the database
        if not check_password_hash(user.password, password):
            flash("Invalid email or password.", "error")
            return redirect(url_for('login_page'))

        if user.role == 0:
            flash("You have admin rights", "error")
            return redirect(url_for('login_page'))

        # Successful login
        session['user_id'] = user.id
        session['username'] = user.username
        session.permanent = True

        flash(f"Welcome back, {user.username}!", "success")
        return redirect(url_for('tickets'))

    @app.route("/delete_user", methods=['POST'])
    def delete_user():
        user_id = request.form.get('id')

        # Find the user by ID
        user = User.query.get(user_id)

        if user:
            # If user exists, delete it
            db.session.delete(user)
            db.session.commit()
            flash("User deleted successfully", "success")
        else:
            # If user does not exist, show error
            flash("User not found", "error")

        return redirect(url_for('users'))

    @app.route('/tickets')
    def tickets():
        if 'user_id' not in session:
            flash("You must be logged in to view this page.", "error")
            return redirect(url_for('login_page'))

        search_term = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Number of tickets per page

        # Query tickets with optional search term
        if search_term:
            query = Ticket.query.filter(
                Ticket.user_id == session['user_id'],
                (Ticket.title.contains(search_term) |
                 Ticket.description.contains(search_term))
            )
        else:
            query = Ticket.query.filter_by(user_id=session['user_id'])

        # Apply ordering and pagination
        pagination = query.order_by(Ticket.id.desc()).paginate(
            page=page, per_page=per_page)

        ticket_count = query.count()

        # Handle invalid page numbers
        if page > pagination.pages and pagination.pages > 0:
            return redirect(url_for('tickets', page=1, search=search_term))

        # Format the `created_at` field for each ticket on the current page
        for ticket in pagination.items:
            ticket.created_at_formatted = ticket.created_at.strftime(
                '%d %b, %Y')

        # Render the template with paginated tickets
        return render_template(
            'tickets/index.html',
            tickets=pagination.items,       # Tickets for the current page
            tickets_count=ticket_count,     # Tickets count
            pagination=pagination,          # Pagination object for navigation
            search_term=search_term         # Retain the search term in the template
        )

    @app.route('/add-ticket', methods=['GET'])
    def add_ticket_view():
        if 'user_id' not in session:
            flash("You must be logged in to view this page.", "error")
            return redirect(url_for('login_page'))

        return render_template('tickets/add-ticket.html')

    @app.route('/edit-ticket/<int:ticket_id>', methods=['GET'])
    def edit_ticket_view(ticket_id):
        if 'user_id' not in session:
            flash("You must be logged in to view this page.", "error")
            return redirect(url_for('login_page'))

        # Retrieve the ticket by ID
        ticket = Ticket.query.get(ticket_id)

        if not ticket:
            flash("Ticket not found.", "error")
            return redirect(url_for('tickets'))

        return render_template('tickets/edit-ticket.html', ticket=ticket)

    @app.route('/update-ticket/<int:ticket_id>', methods=['POST'])
    def update_ticket(ticket_id):
        # Retrieve the ticket by ID
        ticket = Ticket.query.get(ticket_id)

        if not ticket:
            flash("Ticket not found.", "error")
            return redirect(url_for('tickets'))

        # Check if the current user is the one who created the ticket
        if ticket.user_id != session['user_id']:
            flash("You can only edit your own tickets.", "error")
            return redirect(url_for('tickets'))

        # Get the updated data from the form
        title = request.form.get('title')
        description = request.form.get('description')

        if not title or not description:
            flash("All fields are required.", "error")
            return redirect(url_for('edit_ticket_view', ticket_id=ticket_id))

        # Update ticket fields
        ticket.title = title
        ticket.description = description

        # Commit the changes to the database
        db.session.commit()

        flash("Ticket updated successfully!", "success")
        return redirect(url_for('tickets'))

    @app.route('/add-ticket', methods=['POST'])
    def add_ticket():
        title = request.form.get('title')
        description = request.form.get('description')
        user = User.query.get(session['user_id'])

        if user is None:
            flash("User not found.", "error")
            return redirect(url_for('login_page'))

        # Check for empty fields
        if not title or not description:
            flash("All fields are required.", "error")
            return redirect(url_for('add_ticket'))  # Redirect to the form page

        new_ticket = Ticket(
            title=title, description=description, user_id=user.id, status=1)
        db.session.add(new_ticket)
        db.session.commit()

        flash("Ticket created successfully", "success")
        return redirect(url_for('tickets'))

    @app.route("/delete_ticket", methods=['POST'])
    def delete_ticket():
        ticket_id = request.form.get('id')

        # Find the ticket by ID
        ticket = Ticket.query.get(ticket_id)

        if ticket:
            # If ticket exists, delete it
            db.session.delete(ticket)
            db.session.commit()
            flash("Ticket deleted successfully", "success")
        else:
            # If ticket does not exist, show error
            flash("Ticket not found", "error")

        return redirect(url_for('tickets'))

    @app.route("/delete_all_ticket", methods=['POST'])
    def delete_all_ticket():
        # Ensure the user is logged in by checking session['user_id']
        if 'user_id' not in session:
            flash("You must be logged in to perform this action.", "error")
            return redirect(url_for('login_page'))

        user_id = session['user_id']

        # Get all tickets for the logged-in user
        tickets = Ticket.query.filter_by(user_id=user_id).all()

        if tickets:
            # Delete all tickets associated with the current user
            for ticket in tickets:
                db.session.delete(ticket)
            db.session.commit()
            flash("All tickets deleted successfully", "success")
        else:
            # If no tickets found for the user
            flash("No tickets found for the user.", "error")

        return redirect(url_for('tickets'))

    @app.route('/auth/logout')
    def user_logout():
        session.pop('user_id', None)
        session.pop('user_username', None)

        flash("You have been logged out.", "success")
        return redirect(url_for('login_page'))

    # ADMIN Dashboard

    @app.route("/admin")
    def admin_index():
        if 'admin_id' in session:
            flash("You are already login.", "success")
            return redirect(url_for('admin_tickets'))

        return render_template('admin/auth/login.html')

    @app.route('/admin/auth/login', methods=['POST'])
    def admin_login():
        email = request.form.get('email')
        password = request.form.get('password')

        # Find the user in the database by email
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not found.", "error")
            return redirect(url_for('admin_index'))

        # Check if the password length is less than 8 characters
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for('admin_index'))

        # Check if the password matches the hashed password in the database
        if not check_password_hash(user.password, password):
            flash("Invalid email or password.", "error")
            return redirect(url_for('admin_index'))

        if user.role != 0:
            flash("You don't have admin rights.", "error")
            return redirect(url_for('admin_index'))

        # Successful login
        session['admin_id'] = user.id
        session['admin_username'] = user.username
        session.permanent = True

        flash(f"Welcome back admin!", "success")
        return redirect(url_for('admin_tickets'))

    @app.route('/admin/users')
    def admin_users():
        if 'admin_id' not in session:
            flash("You must be logged in to view this page.", "error")
            return redirect(url_for('admin_index'))

        # Fetch the current user based on user_id stored in session
        current_user = User.query.get(session['admin_id'])

        # Check if the user is an admin (role == 0)
        if current_user.role != 0:
            flash("You do not have permission to view this page.", "error")
            return redirect(url_for('admin_index'))  # Redirect to login page

        search_term = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        per_page = 5

        query = User.query

        # Apply search filter if a search term is provided
        if search_term:
            query = query.filter(
                (User.username.contains(search_term) |
                 User.email.contains(search_term))
            )

        # Apply ordering and pagination
        pagination = query.order_by(User.id.desc()).paginate(
            page=page, per_page=per_page)

        all_users = pagination.items

        users_count = query.count()

        for user in all_users:
            user.created_at_formatted = user.created_at.strftime('%d %b, %Y')
            user.ticket_count = Ticket.query.filter_by(user_id=user.id).count()

        users_count = User.query.count()

        return render_template(
            'admin/users.html',
            users=all_users,
            search_term=search_term,
            pagination=pagination,
            users_count=users_count
        )

    @app.route('/admin/tickets')
    def admin_tickets():

        if 'admin_id' not in session:
            flash("You must be logged in to view this page.", "error")
            return redirect(url_for('admin_index'))

        # Fetch the current user based on user_id stored in session
        current_user = User.query.get(session['admin_id'])

        # Check if the user is an admin (role == 0)
        if current_user.role != 0:
            flash("You do not have permission to view this page.", "error")
            return redirect(url_for('admin_index'))  # Redirect to login page

        search_term = request.args.get('search', '')
        status_term = request.args.get('status', '')

        page = request.args.get('page', 1, type=int)
        per_page = 5

        query = Ticket.query

        # Apply search filter if a search term is provided
        if search_term:
            query = query.filter(
                (Ticket.title.contains(search_term) |
                 Ticket.description.contains(search_term))
            )

        # if status_term and status_term != 'all':  # 'all' means no status filter
        #     query = query.filter(Ticket.status == int(status_term))

        # Apply ordering and pagination
        pagination = query.order_by(Ticket.id.desc()).paginate(
            page=page, per_page=per_page)

        # Get the tickets for the current page
        all_tickets = pagination.items

        ticket_counts = query.count()

        # Process tickets to format created_at (optional)
        for ticket in all_tickets:
            ticket.created_at_formatted = ticket.created_at.strftime(
                '%d %b, %Y')
            ticket.username = ticket.user.username
            ticket.email = ticket.user.email

        return render_template(
            'admin/tickets.html',
            tickets=all_tickets,
            pagination=pagination,
            ticket_counts=ticket_counts,
            search_term=search_term
        )

    @app.route('/update_ticket_status/<int:ticket_id>', methods=['POST'])
    def update_ticket_status(ticket_id):
        if 'admin_id' not in session:
            return jsonify({"error": "Unauthorized access"}), 401

        data = request.get_json()
        new_status = data.get('status')

        ticket = Ticket.query.get(ticket_id)
        if ticket:
            ticket.status = int(new_status)
            db.session.commit()
            return jsonify({"message": "Status updated successfully"}), 200
        else:
            return jsonify({"error": "Ticket not found"}), 404

    @app.route("/admin_delete_ticket", methods=['POST'])
    def admin_delete_ticket():
        ticket_id = request.form.get('id')

        # Find the ticket by ID
        ticket = Ticket.query.get(ticket_id)

        if ticket:
            # If ticket exists, delete it
            db.session.delete(ticket)
            db.session.commit()
            flash("Ticket deleted successfully", "success")
        else:
            # If ticket does not exist, show error
            flash("Ticket not found", "error")

        return redirect(url_for('admin_tickets'))

    @app.route("/admin_delete_user", methods=['POST'])
    def admin_delete_user():
        user_id = request.form.get('id')

        # Find the user by ID
        user = User.query.get(user_id)

        if user:
            # Delete all tickets related to this user
            Ticket.query.filter_by(user_id=user_id).delete()

            # Delete the user
            db.session.delete(user)
            db.session.commit()

            flash("User deleted successfully", "success")
        else:
            # If user does not exist, show error
            flash("User not found", "error")

        return redirect(url_for('admin_users'))

    @app.route('/admin/auth/logout')
    def admin_logout():
        session.pop('admin_id', None)
        session.pop('admin_username', None)

        flash("You have been logged out.", "success")
        return redirect(url_for('admin_index'))
