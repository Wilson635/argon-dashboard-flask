# Import necessary modules and models
from datetime import datetime

import httpagentparser
from flask import render_template, request, redirect, url_for, send_file, abort
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from toastify import notify
from datetime import datetime
import io

from apps import db
from apps.authentication.models import Users, Members, Children, Parents, Partners, EmergencyContact, PDFFile, \
    Declaration
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

    # Render the 'home/index.html' template with the above variables
    return render_template('home/index.html', segment='index', users=users, user_count=user_count,
                           member_count=member_count)


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
            return 'File uploaded successfully!'
    # If the request method is GET, retrieve all members from the database and render the 'home/upload_pdf.html' template
    members = Members.query.all()
    return render_template('home/upload_pdf.html', members=members, segment='upload_pdf')


@blueprint.route('/view_pdf/<int:file_id>')
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


@blueprint.route('/download_pdf/<int:file_id>')
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


@blueprint.route('/members')
@login_required
def show_members():
    members = Members.query.all()  # Get all members
    return render_template('home/members.html', members=members, segment='members')


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
            notify(
                BodyText='Email already registered',
                AppName='Mutuelle FTSL',
                TitleText='Error !!!',
                ImagePath="/static/assets/img/brand/favicon.jpg"
            )
            return render_template('home/newUser.html',
                                   success=False, segment=segment)

        if not email:
            notify(
                BodyText='Please fill in the blank field',
                AppName='Mutuelle FTSL',
                TitleText='Error !!!',
                ImagePath="/static/assets/img/brand/favicon.jpg"
            )
            return render_template('home/newUser.html',
                                   success=False, segment=segment)

        if not username:
            notify(
                BodyText='Please fill in the blank field',
                AppName='Mutuelle FTSL',
                TitleText='Error !!!',
                ImagePath="/static/assets/img/brand/favicon.jpg"
            )
            return render_template('home/newUser.html',
                                   success=False, segment=segment)

        if not password:
            notify(
                BodyText='Please fill in the blank field',
                AppName='Mutuelle FTSL',
                TitleText='Error !!!',
                ImagePath="/static/assets/img/brand/favicon.jpg"
            )
            return render_template('home/newUser.html',
                                   success=False, segment=segment)

        if not role:
            notify(
                BodyText='Role not registered',
                AppName='Mutuelle FTSL',
                TitleText='Error !!!',
                ImagePath="/static/assets/img/brand/favicon.jpg"
            )
            return render_template('home/newUser.html',
                                   success=False, segment=segment)

        # Otherwise, we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        notify(
            BodyText='User created, please login',
            AppName='Mutuelle FTSL',
            TitleText='Congratulation !!!',
            ImagePath="/static/assets/img/brand/favicon.jpg"
        )

        return render_template('home/newUser.html',
                               success=True, segment=segment)
    else:
        return render_template('home/newUser.html', segment=segment)


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
        notify(
            BodyText='Profile updated successfully!',
            AppName='Mutuelle FTSL',
            TitleText='Success',
            ImagePath="/static/assets/img/brand/favicon.jpg"
        )

    return render_template('home/settings.html', segment=segment)


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

        return render_template('home/newMember.html',
                               segment=segment)  # Redirect to another page after adding the member

    return render_template('home/newMember.html', segment=segment)  # Replace with your template


@blueprint.route('/newDeclaration', methods=['GET', 'POST'])
@login_required
def add_declaration():
    """
    This function handles the POST request for creating a new declaration.
    It retrieves the necessary data from the request form and files,
    finds the user and member based on the provided name and first name,
    creates a new declaration, and notifies the user of the result.

    Returns:
        If the request method is POST, it redirects to the 'events' page.
        Otherwise, it renders the 'new-delcl.html' template.
    """
    if request.method == 'POST':
        # Retrieve the recipient name from the request form
        recipient_name = request.form.get('recipient-name')
        # user_first_name, user_last_name = recipient_name.split()[:2]
        # member_first_name, member_name = recipient_name.split()[-2:]
        # user_first_name, _, user_last_name = recipient_name.partition(' ')
        # member_name, _, member_first_name = recipient_name.rpartition(' ')
        if recipient_name is not None:
            user_first_name, _, user_last_name = recipient_name.partition(' ')
            member_name, _, member_first_name = recipient_name.rpartition(' ')
        else:
            # Handle the case when recipient_name is None
            # You can raise an exception or handle it in some other way
            raise ValueError("recipient_name is None")

        # Retrieve the declaration type and file name from the request form and files
        declaration_type = request.form.get('type-name')
        file_name = request.files['join-name'].filename if 'join-name' in request.files else None

        # Find the user based on the first name and last name
        user = Users.query.filter_by(firstName=user_first_name, lastName=user_last_name).first()
        if not user:
            # Notify the user if the user is not found
            notify(
                BodyText='Utilisateur non trouvé',
                AppName='Mutuelle FTSL',
                TitleText='Erreur',
                ImagePath="/static/assets/img/brand/favicon.jpg"
            )
            return render_template('home/guest/modals/new-delcl.html')

        # Find the member based on the name and first name
        member = Members.query.filter_by(name=member_name, firstName=member_first_name).first()
        if not member:
            # Notify the user if the member is not found
            notify(
                BodyText='Membre non trouvé',
                AppName='Mutuelle FTSL',
                TitleText='Erreur',
                ImagePath="/static/assets/img/brand/favicon.jpg"
            )
            return render_template('home/guest/modals/new-delcl.html')

        # Create a new declaration
        declaration = Declaration(
            user_id=user.id,
            member_id=member.idMember,
            declaration_type=declaration_type,
            file_name=file_name
        )
        db.session.add(declaration)
        db.session.commit()

        # Notify the user of the successful declaration
        notify(
            BodyText='Déclaration ajoutée avec succès !',
            AppName='Mutuelle FTSL',
            TitleText='Succès',
            ImagePath="/static/assets/img/brand/favicon.jpg"
        )

        return render_template('home/guest/modals/new-delcl.html')

    return render_template('home/guest/modals/new-delcl.html')


# Helper - Extract the current page name from the request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None
