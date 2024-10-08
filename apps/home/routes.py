# Import necessary modules and models
from datetime import datetime

import httpagentparser
import pandas as pd
from flask import render_template, request, redirect, url_for, send_file, abort, session
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from toastify import notify
from datetime import datetime
import io

from werkzeug.security import check_password_hash, generate_password_hash

from apps import db
from apps.authentication.models import Users, Members, Children, Parents, Partners, EmergencyContact, PDFFile, \
    Declaration, DeclarationFile
from apps.authentication.util import verify_pass, hash_pass
from apps.home import blueprint


@blueprint.route('/index')
@login_required
def index():
    """
    This function is a route handler for the '/index' endpoint. It requires the user to be logged in.
    It retrieves all users and members from the database and renders the 'home/index.html' template.

    Returns:
        The rendered 'home/index.html' template with the following variables:
        - segment: 'index'
        - users: All users from the database
        - user_count: The count of all users from the database
        - member_count: The count of all members from the database
    """
    # Retrieve all users from the database
    users = Users.query.all()

    # Count all users in the database
    user_count = Users.query.count()

    # Count all members in the database
    member_count = Members.query.count()

    # Count all events in the database
    event_count = Declaration.query.count()

    # Paginate the users
    page = request.args.get('page', 1, type=int)
    per_page = 6
    paginated_users = Users.query.order_by(Users.username).paginate(page=page, per_page=per_page)

    # Render the 'home/index.html' template with the above variables
    return render_template('home/index.html', segment='index', users=users, user_count=user_count,
                           member_count=member_count, event_count=event_count, paginated_users=paginated_users)


@blueprint.route('/<template>')
@login_required
def route_template(template):
    """
    Route for serving HTML templates.

    This function serves HTML templates from the 'home' directory in the templates folder.
    It first retrieves all members from the database. Then, it tries to render the template
    specified by the 'template' parameter. If the template does not end with '.html', it
    appends '.html' to the template name. Finally, it renders the template with the members
    and the current page segment.

    If the template is not found, it renders the 'page-404.html' template. If any other
    exception occurs, it renders the 'page-500.html' template.

    Parameters:
        template (str): The name of the template to render.

    Returns:
        If the template is found and rendered successfully, it returns the rendered template.
        If the template is not found, it returns the rendered 'page-404.html' template.
        If any other exception occurs, it returns the rendered 'page-500.html' template.
    """
    members = Members.query.all()  # Get all members
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, members=members, segment=segment)

    except TemplateNotFound:
        # Render the 'page-404.html' template if the template is not found
        return render_template('home/page-404.html', segment='page-404'), 404

    except:
        # Render the 'page-500.html' template if any other exception occurs
        return render_template('home/page-500.html', segment='page-500'), 500


# @blueprint.route('/settings')
# def settings():
#     # Detect the current page
#     segment = get_segment(request)
#
#     user_agent = request.headers.get('User-Agent')
#     device_info = httpagentparser.simple_detect(user_agent)
#     return render_template('home/settings.html', device_info=device_info, segment=segment)

@blueprint.route('/upload_pdf', methods=['GET', 'POST'])
@login_required
def upload_pdf():
    """
    Route for handling file uploads.

    If the request method is POST, checks if a file is present in the request.
    If a file is present, creates a new PDFFile object with the file data and member ID.
    Adds the new PDFFile object to the database and returns a success message.

    If the request method is GET, retrieves all members from the database and renders the 'home/upload_pdf.html' template.

    Returns:
        If the request method is POST and a file is present:
            - If the file has no name, redirects to the current URL.
            - If the file has a name, creates a new PDFFile object with the file data and member ID.
            - Adds the new PDFFile object to the database and commits the changes.
            - Returns the success message 'File uploaded successfully!'.
        If the request method is GET:
            - Retrieves all members from the database.
            - Renders the 'home/upload_pdf.html' template with the members and segment 'upload_pdf'.
    """
    if request.method == 'POST':
        # Check if a file is present in the request
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        member_id = request.form.get('member_id')
        # Check if the file has a name
        if file.filename == '':
            return redirect(request.url)
        # If the file has a name, create a new PDFFile object with the file data and member ID
        if file:
            new_file = PDFFile(filename=file.filename, data=file.read(), member_id=member_id)
            db.session.add(new_file)
            db.session.commit()
            notify_success('File uploaded successfully!')
            return redirect(url_for('home_blueprint.show_members'))
    # If the request method is GET, retrieve all members from the database and render the 'home/upload_pdf.html'
    # template
    members = Members.query.all()
    return render_template('home/upload_pdf.html', members=members, segment='upload_pdf')


@blueprint.route('/view_pdf/<string:file_id>')
@login_required
def view_pdf(file_id):
    """
    View a PDF file by its ID.

    Args:
        file_id (int): The ID of the PDF file to view.

    Returns:
        Response: The PDF file as a response, with the filename as the attachment name.
    """
    # Retrieve the PDF file data from the database
    file_data = PDFFile.query.get(file_id)

    # Create a BytesIO object with the file data
    file_bytes = io.BytesIO(file_data.data)

    # Return the file as a response with the specified filename
    return send_file(
        file_bytes,
        attachment_filename=file_data.filename,
        as_attachment=False  # Set as_attachment to False to display the file in the browser
    )


@blueprint.route('/download_pdf/<string:file_id>')
@login_required
def download_pdf(file_id):
    """
    Download a PDF file by its ID.

    Args:
        file_id (int): The ID of the PDF file to download.

    Returns:
        Response: The downloaded PDF file as an attachment.

    Raises:
        NotFound: If the PDF file with the given ID is not found.
    """
    # Retrieve the PDF file data from the database
    file_data = PDFFile.query.get(file_id)

    # If the file is not found, raise a 404 error
    if file_data is None:
        abort(404)

    # Create a BytesIO object with the file data
    file_bytes = io.BytesIO(file_data.data)

    # Return the file as an attachment with the specified filename
    return send_file(
        file_bytes,
        attachment_filename=file_data.filename,
        as_attachment=True
    )


@blueprint.route('/export_user_excel')
@login_required
def export_user_excel():
    """
    This route generates an Excel file containing user data
    and sends it for download.

    Returns:
        A downloadable Excel file containing user data.
    """
    # Retrieve user data from the database
    users = Users.query.all()

    # Create DataFrames from the user data
    user_data = [{
        "Username": user.username,
        "Email": user.email,
        "Role": user.role
    } for user in users]

    df_users = pd.DataFrame(user_data)

    # Create a Pandas Excel writer using an in-memory buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write the user data to the Excel file
        df_users.to_excel(writer, sheet_name='Users', index=False)

    # Reset the buffer position to the beginning
    output.seek(0)

    # Send the Excel file as a downloadable attachment
    return send_file(output, as_attachment=True, download_name="usersList.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@blueprint.route('/export_member_excel')
@login_required
def export_member_excel():
    """
    This route generates an Excel file containing member data along with their related entities
    (children, parents, partners, and emergency contacts) and sends it for download.

    Returns:
        A downloadable Excel file containing member data, children, parents, partners, and emergency contacts.
    """
    # Retrieve data from the database
    members = Members.query.all()

    # Create a dictionary to map member IDs to their full names
    member_name_map = {member.idMember: f"{member.name} {member.firstName}" for member in members}

    # Create DataFrames for each entity
    member_data = [{
        "Member Name": member.name,
        "Member First Name": member.firstName,
        "Member Birthday": member.dateBirth.strftime("%Y-%m-%d"),
        "Member Local": member.local,
        "Member Occupation": member.occupation,
        "Member Family Situation": member.familySituation
    } for member in members]

    # Retrieve children, parents, partners, and emergency contacts for each member
    children_data = [{
        "Member Name": member_name_map.get(child.member_id),
        "Child Name": child.name,
        "Child First Name": child.firstName,
        "Child Birthday": child.dateBirth.strftime("%Y-%m-%d")
    } for child in Children.query.all()]

    parents_data = [{
        "Member Name": member_name_map.get(parent.member_id),
        "Parent Name": parent.name,
        "Parent First Name": parent.firstName,
        "Parent Mobile Number": parent.mobileNumber
    } for parent in Parents.query.all()]

    partners_data = [{
        "Member Name": member_name_map.get(partner.member_id),
        "Partner Name": partner.name,
        "Partner First Name": partner.firstName,
        "Partner Birthday": partner.dateBirth.strftime("%Y-%m-%d")
    } for partner in Partners.query.all()]

    emergency_contacts_data = [{
        "Member Name": member_name_map.get(contact.member_id),
        "Emergency Contact Name": contact.name,
        "Emergency Contact First Name": contact.firstName,
        "Emergency Contact Address": contact.address,
        "Emergency Contact Mobile Number": contact.mobileNumber,
        "Emergency Contact Quality": contact.quality,
        "Emergency Contact Others": contact.others
    } for contact in EmergencyContact.query.all()]

    # Create DataFrames using pandas
    df_members = pd.DataFrame(member_data)
    df_children = pd.DataFrame(children_data)
    df_parents = pd.DataFrame(parents_data)
    df_partners = pd.DataFrame(partners_data)
    df_emergency_contacts = pd.DataFrame(emergency_contacts_data)

    # Create an in-memory buffer for the Excel file
    output = io.BytesIO()

    # Write each DataFrame to a separate sheet in the Excel file
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_members.to_excel(writer, sheet_name='Members', index=False)
        df_children.to_excel(writer, sheet_name='Children', index=False)
        df_parents.to_excel(writer, sheet_name='Parents', index=False)
        df_partners.to_excel(writer, sheet_name='Partners', index=False)
        df_emergency_contacts.to_excel(writer, sheet_name='Emergency Contacts', index=False)

    # Move the pointer back to the beginning of the stream
    output.seek(0)

    # Send the Excel file as a downloadable attachment
    return send_file(output, as_attachment=True, download_name="members_and_related_data.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@blueprint.route('/members')
@login_required
def show_members():
    members = Members.query.all()  # Get all members
    return render_template('home/members.html', members=members, segment='members')


@blueprint.route('/settings')
@login_required
def settings():
    segment = get_segment(request)
    return render_template('home/settings.html', segment=segment)


@blueprint.route('/newUser', methods=['GET', 'POST'])
def new_account():
    """
    Route for creating a new user account.

    If the request method is POST and the form contains the 'register' field,
    it validates the form data and creates a new user in the database.
    If the email already exists, it displays an error message.
    If any of the required fields are missing, it displays an error message.
    If the role is not specified, it displays an error message.
    Otherwise, it creates a new user and displays a success message.

    If the request method is GET, it renders the 'newUser.html' template.
    """
    segment = get_segment(request)  # Detect the current page

    if 'register' in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Check if the email already exists
        email_exists = Users.query.filter_by(email=email).first()
        if email_exists:
            notify_error('Email already exists')
            return render_template('home/newUser.html',
                                   success=False, segment=segment)

        if not email:
            notify_error('Please fill in the blank field', )
            return render_template('home/newUser.html',
                                   success=False, segment=segment)

        if not username:
            notify_error('Please fill in the blank field', )
            return render_template('home/newUser.html',
                                   success=False, segment=segment)

        if not password:
            notify_error('Please fill in the blank field', )
            return render_template('home/newUser.html',
                                   success=False, segment=segment)

        if not role:
            notify_error('Role is required', )
            return render_template('home/newUser.html',
                                   success=False, segment=segment)

        # Otherwise, we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        notify_success('User created successfully, you can now login', )

        return render_template('home/newUser.html',
                               success=True, segment=segment)
    else:
        return render_template('home/newUser.html', segment=segment)


@blueprint.route('/edit_user/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    """
    Edit user details based on the user ID.

    Args:
        id (str): The ID of the user to edit.

    Returns:
        If the request method is GET, renders the 'home/edit_user.html' template with the user object.
        If the request method is POST, updates the user details and redirects to the home page.

    Raises:
        NotFound: If the user with the given ID does not exist.
    """
    # Get the user object based on the ID
    user = Users.query.get_or_404(id)

    # Get the current segment
    segment = get_segment(request)

    if request.method == 'POST':
        # Update the user's username and email
        user.username = request.form['username']
        user.email = request.form['email']

        # Optionally update the password if provided
        password = request.form.get('password')
        if password:
            user.password = generate_password_hash(password)

        # Update the user's role if provided
        user.role = request.form.get('role', user.role)

        try:
            # Commit the changes to the database
            db.session.commit()
            notify_success('User updated successfully!')
            return redirect(url_for('home_blueprint.index'))
        except Exception as e:
            # Rollback the changes if an error occurs
            db.session.rollback()
            notify_error(f'Error updating user: {str(e)}')
            return redirect(url_for('home_blueprint.edit_user', id=id))

    # Render the 'home/edit_user.html' template with the user object
    return render_template('home/edit_user.html', user=user, segment=segment)


@blueprint.route('/delete_user/<string:id>', methods=['POST'])
@login_required
def delete_user(id):
    """
    This route is used to delete a user based on the user ID.

    Args:
        id (str): The ID of the user to be deleted.

    Returns:
        redirect: Redirects to the home page after successful deletion.

    Raises:
        Exception: If there is an error during the deletion process.
    """
    # Get the user object based on the provided ID
    user = Users.query.get_or_404(id)

    try:
        # Delete the user from the database
        db.session.delete(user)
        # Commit the changes to the database
        db.session.commit()
        # Notify the user that the deletion was successful
        notify_success('User deleted successfully!')
    except Exception as e:
        # If there is an error during the deletion process, rollback the changes
        db.session.rollback()
        # Notify the user about the error
        notify_error(f'Error deleting user: {str(e)}')

    # Redirect the user to the home page
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/change-password', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in
def change_password():
    """
    Route for changing the password of the logged-in user.

    The user must provide their old password, a new password, and confirm it.
    If all fields are filled and the old password is correct, the new password is hashed
    and stored in the database. If the new password is not at least 8 characters long,
    an error message is displayed. If the new password and confirmation do not match,
    an error message is displayed. If there is an error updating the password, an error
    message is displayed.
    Args:
        None
    Returns:
        If the request method is POST, it renders the 'home/settings.html' template with
        a success message if the password was changed successfully, or an error message
        if there was an error. If the request method is GET, it renders the
        'home/settings.html' template.
    """
    segment = get_segment(request)  # Get the current page segment

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check if all fields are filled
        if not old_password or not new_password or not confirm_password:
            notify_error('Please fill in all fields.')
            return redirect(url_for('home_blueprint.settings'))

        # Verify that the old password is correct
        if not verify_pass(old_password, current_user.password):
            notify_error('The old password is incorrect.')
            return redirect(url_for('home_blueprint.settings'))

        # Check if the new password and confirmation match
        if new_password != confirm_password:
            notify_error('The new password and confirmation do not match.')
            return redirect(url_for('home_blueprint.settings'))

        # Check that the new password is long enough
        # if len(new_password) < 8:
        #     notify_error('The new password must be at least 8 characters long.')
        #     return render_template('home/settings.html', success=False, segment=segment)

        # Hash the new password and update the user
        hashed_password = hash_pass(new_password)  # This returns bytes
        current_user.password = hashed_password.decode('ascii')  # Store it as a string

        # Save changes to the database
        try:
            db.session.commit()
            notify_success('Password changed successfully.')
            return redirect(url_for('home_blueprint.settings'))
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            notify_error('Error updating the password.')
            return redirect(url_for('home_blueprint.settings'))
    else:
        # Display the form if the method is GET
        return redirect(url_for('home_blueprint.settings'))


@blueprint.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    """
    Update the user profile with the data from the form.

    If the request method is POST, update the user's information with the form data.
    If a new password is provided, update the user's password.
    Save the changes to the database.

    Returns:
        The rendered 'home/settings.html' template with the updated segment.

    """
    segment = get_segment(request)

    if request.method == 'POST':
        # Get the current user
        user = Users.query.get(current_user.id)

        # Update the user's information with the form data
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.firstName = request.form.get('first_name')
        user.lastName = request.form.get('last_name')
        user.address = request.form.get('address')
        user.city = request.form.get('city')
        user.country = request.form.get('country')
        user.postalCode = request.form.get('postal_code')
        user.position = request.form.get('occupation')
        user.about = request.form.get('about_me')

        # Update the user's password if a new password is provided
        if request.form.get('password'):
            user.set_password(request.form.get('password'))

        # Save the changes to the database
        db.session.commit()

        # Notify the user that the profile was updated successfully
        notify_success('Profile updated successfully')

    return redirect(url_for('home_blueprint.settings'))


@blueprint.route('/newMember', methods=['GET', 'POST'])
def add_member():
    """
    Route for creating a new member.

    If the request method is POST and the form contains the necessary fields,
    a new member, children, parents, partners, and emergency contacts are created
    and added to the database.

    Returns:
        If the request method is GET, renders the 'home/newMember.html' template.
        If the request method is POST, redirects to the 'home/newMember.html' template.
    """
    segment = get_segment(request)  # Detect the current page

    if request.method == 'POST':
        # Retrieve form data
        member_name = request.form.get('name_members')
        member_first_name = request.form.get('first_name_members')
        member_date_birth = request.form.get('birthday_members')
        member_local = request.form.get('local_members')
        member_family_situation = request.form.get('family_situation_members')
        member_occupation = request.form.get('occupation_members')

        children_name = request.form.get('name_children')
        children_first_name = request.form.get('first_name_children')
        children_date_birth = request.form.get('birthday_children')

        parent_name = request.form.get('name_parents')
        parent_first_name = request.form.get('first_name_parents')
        parent_mobile_number = request.form.get('mobile_parents')

        partner_name = request.form.get('name_partners')
        partner_first_name = request.form.get('first_name_partners')
        partner_date_birth = request.form.get('birthday_partners')

        emergency_name = request.form.get('name_emergency')
        emergency_first_name = request.form.get('first_name_emergency')
        emergency_address = request.form.get('address_emergency')
        emergency_mobile_number = request.form.get('mobile_emergency')
        emergency_quality = request.form.get('quality_emergency')
        emergency_others = request.form.get('others_emergency')

        # Create a new Member object
        new_member = Members(
            name=member_name,
            firstName=member_first_name,
            local=member_local,
            familySituation=member_family_situation,
            occupation=member_occupation,
            dateBirth=datetime.strptime(member_date_birth, '%Y-%m-%d')
        )

        db.session.add(new_member)
        db.session.commit()  # Commit to get the member's ID

        # Add children
        new_child = Children(
            name=children_name,
            firstName=children_first_name,
            dateBirth=datetime.strptime(children_date_birth, '%Y-%m-%d'),
            member_id=new_member.idMember
        )
        db.session.add(new_child)

        # Add parents
        new_parent = Parents(
            name=parent_name,
            firstName=parent_first_name,
            mobileNumber=parent_mobile_number,
            member_id=new_member.idMember
        )
        db.session.add(new_parent)

        # Add partners
        new_partner = Partners(
            name=partner_name,
            firstName=partner_first_name,
            dateBirth=datetime.strptime(partner_date_birth, '%Y-%m-%d'),
            member_id=new_member.idMember
        )
        db.session.add(new_partner)

        # Add emergency contacts
        new_emergency_contact = EmergencyContact(
            name=emergency_name,
            firstName=emergency_first_name,
            address=emergency_address,
            mobileNumber=emergency_mobile_number,
            quality=emergency_quality,
            others=emergency_others,
            member_id=new_member.idMember
        )
        db.session.add(new_emergency_contact)

        # Commit all changes
        db.session.commit()
        notify_success('Member added successfully!')
        return render_template('home/newMember.html',
                               segment=segment)  # Redirect to another page after adding the member

    return redirect(url_for('home_blueprint.show_members'))  # Replace with your template


@blueprint.route('/newDeclaration', methods=['GET', 'POST'])
@login_required
def add_declaration():
    """
    Handles the creation of a new declaration, including uploading and storing multiple files.

    This function receives a POST request with a recipient name, declaration type, and multiple files.
    It searches for the user and member based on the recipient name, creates a new declaration,
    and associates it with the user and member. It then processes each file and stores it in the database.
    Finally, it notifies the user of the successful addition of the declaration and renders the events page.

    Returns:
        The rendered events page if the request method is GET, otherwise the rendered new-delcl.html page.
    """
    segment = get_segment(request)

    if request.method == 'POST':
        # Extract recipient name, declaration type, and files from the request
        recipient_name = request.form.get('recipient-name')
        declaration_type = request.form.get('type-name')
        files = request.files.getlist('join-name')

        # Split recipient name into first and last name
        if recipient_name is not None:
            names = recipient_name.split()
            user_first_name = names[0]
            member_first_name = names[0]
            user_last_name = names[1]
            member_name = names[1]
        else:
            raise ValueError("recipient_name is None")

        # Find user and member based on names
        user = Users.query.filter_by(firstName=user_first_name, lastName=user_last_name).first()
        member = Members.query.filter_by(name=member_name, firstName=member_first_name).first()

        # If user or member not found, notify and return
        if not user:
            notify_error('Utilisateur non trouvé')
            return render_template('home/guest/modals/new-delcl.html')
        if not member:
            notify_error('Membre non trouvé')
            return render_template('home/guest/modals/new-delcl.html')

        # Create a new declaration and associate it with the user and member
        declaration = Declaration(
            user_id=user.id,
            member_id=member.idMember,
            declaration_type=declaration_type
        )
        db.session.add(declaration)
        db.session.commit()

        # Process each file and store it in the database
        for file in files:
            if file and file.filename.endswith('.pdf'):
                declaration_file = DeclarationFile(
                    declaration_id=declaration.id,
                    file_name=file.filename,
                    file_data=file.read()
                )
                db.session.add(declaration_file)

        db.session.commit()

        # Notify user of successful addition
        notify_success('Déclaration ajoutée avec succès !')

        return redirect(url_for('home_blueprint.events'))

    return redirect(url_for('home_blueprint.events'))


@blueprint.route('/reject/<string:id>', methods=['GET', 'POST'])
@login_required
def reject_declaration(id):
    """
    Reject a declaration with the given ID.

    Args:
        id (str): The ID of the declaration to reject.

    Returns:
        The rendered events page if the request method is POST,
        otherwise the rendered reject_form.html page.
    """
    if request.method == 'POST':
        # Fetch the declaration by its ID
        declaration = Declaration.query.get(id)

        if not declaration:
            notify_error("Déclaration non trouvée.")
            return redirect(url_for('blueprint.events'))

        # Get the reason for rejection from the form
        reason = request.form.get('reason')

        if not reason:
            notify_error("Veuillez fournir une raison pour le rejet.")
            return redirect(url_for('home_blueprint.events'))

        # Update the status of the declaration and save the reason
        declaration.statut = 'rejected'
        declaration.declaration_text = reason  # You can store the reason in declaration_text

        # Commit the changes to the database
        db.session.commit()

        notify_success('Déclaration rejetée avec succès.')
        return redirect(url_for('home_blueprint.events'))

    # In case of GET request, render the form page or redirect
    return redirect(url_for('home_blueprint.events'))


@blueprint.route('/schedule/<string:id>', methods=['POST'])
@login_required
def schedule_declaration(id):
    """
    Schedule a declaration by updating its status to 'scheduled'.

    Args:
        id (str): The ID of the declaration to schedule.

    Returns:
        Redirects to the events page after scheduling the declaration.
    """
    # Fetch the declaration by its ID
    declaration = Declaration.query.get(id)

    if not declaration:
        notify_error("Déclaration non trouvée.")
        return redirect(url_for('home_blueprint.events'))

    # Update the status of the declaration to 'scheduled'
    declaration.statut = 'scheduled'

    # Commit the changes to the database
    db.session.commit()

    notify_success('Déclaration programmée avec succès.')
    return redirect(url_for('home_blueprint.events'))


def notify_error(message):
    """
    Notifies the user of an error with a given message.

    Args:
        message (str): The error message to display.
    """
    notify(
        BodyText=message,
        AppName='Mutuelle FTSL',
        TitleText='Error !',
        ImagePath="/static/assets/img/brand/favicon.jpg"
    )


def notify_success(message):
    """
    Notifies the user of a successful action with a given message.

    Args:
        message (str): The success message to display.
    """
    notify(
        BodyText=message,
        AppName='Mutuelle FTSL',
        TitleText='Congratulation !',
        ImagePath="/static/assets/img/brand/favicon.jpg"
    )


@blueprint.route('/events')
@login_required
def events():
    """
    Retrieve and display all declarations with their associated members.

    This function retrieves all declarations from the database and renders the events page with the list of declarations.
    It also counts the number of events 'pending', 'canceled', and 'scheduled'.

    Returns:
        The rendered events page with the list of declarations.
    """
    segment = get_segment(request)
    declarations = Declaration.query.all()
    # count the number of events 'pending'
    pending_count = Declaration.query.filter_by(statut='pending').count()

    # count the number of events 'canceled'
    canceled_count = Declaration.query.filter_by(statut='rejected').count()

    # count the number of events 'scheduled'
    scheduled_count = Declaration.query.filter_by(statut='scheduled').count()
    return render_template('home/events.html', declarations=declarations, segment=segment, pending_count=pending_count,
                           canceled_count=canceled_count, scheduled_count=scheduled_count)


@blueprint.route('/search_autocomplete', methods=['GET'])
def search_autocomplete():
    """
    Route for searching users, members, and declarations based on input query.

    When a user types in the search box, this route is called with a GET request
    to retrieve matching results for users, members, or declarations.
    The query is passed as a parameter 'q'. It renders the 'search_results.html'
    template with the matched results.

    The results are displayed in a dropdown menu on the frontend.
    """
    segment = get_segment(request)  # Detect the current page

    query = request.args.get('q', '')

    # If no query is provided, render the search results page with no results
    if not query:
        return render_template('home/search_results.html', results=[], segment=segment)

    # Search in Users, Members, and Declarations tables
    user_results = Users.query.filter(Users.username.ilike(f'%{query}%')).all()
    member_results = Members.query.filter(Members.name.ilike(f'%{query}%')).all()
    declaration_results = Declaration.query.filter(Declaration.declaration_type.ilike(f'%{query}%')).all()

    # Combine results into a single list
    results = []

    # Append user results
    if user_results:
        for user in user_results:
            results.append({'name': user.username, 'type': 'User', 'url': f'/user/{user.id}'})

    # Append member results
    if member_results:
        for member in member_results:
            results.append({'name': member.name, 'type': 'Member', 'url': f'/member/{member.id}'})

    # Append declaration results
    if declaration_results:
        for declaration in declaration_results:
            results.append({'name': declaration.title, 'type': 'Declaration', 'url': f'/declaration/{declaration.id}'})

    # If no results found, return an empty list
    if not results:
        notify_error('No results found for your query.')
        return render_template('home/search_results.html', results=[], segment=segment)

    # Render the results in the search_results.html template
    return render_template('home/search_results.html', results=results, segment=segment)


def search_users(query):
    # Replace with actual search logic
    return Users.query.filter(Users.username.ilike(f'%{query}%')).all()


def search_members(query):
    # Replace with actual search logic
    return Members.query.filter(Members.name.ilike(f'%{query}%')).all()


def search_declarations(query):
    # Replace with actual search logic
    return Declaration.query.filter(Declaration.declaration_type.ilike(f'%{query}%')).all()


# Helper - Extract the current page name from the request
def get_segment(request):
    """
    Extracts the last segment of the request path and returns it.
    If the segment is empty, returns 'index'.
    If any exception occurs, returns None.

    Args:
        request (flask.Request): The Flask request object.

    Returns:
        str: The last segment of the request path or 'index'.
        None: If any exception occurs.
    """
    try:
        # Extract the last segment of the request path
        segment = request.path.split('/')[-1]

        # If the segment is empty, return 'index'
        if segment == '':
            segment = 'index'

        return segment
    except:
        # If any exception occurs, return None
        return None
