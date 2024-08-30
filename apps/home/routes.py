# Import necessary modules and models
from datetime import datetime

import httpagentparser
from flask import render_template, request, redirect, url_for, send_file
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from toastify import notify
from datetime import datetime
import io

from apps import db
from apps.authentication.models import Users, Members, Children, Parents, Partners, EmergencyContact, PDFFile
from apps.home import blueprint


@blueprint.route('/index')
@login_required
def index():
    users = Users.query.all()  # Get all users
    user_count = Users.query.count()  # Count all users
    member_count = Members.query.count()  # Count all members
    return render_template('home/index.html', segment='index', users=users, user_count=user_count,
                           member_count=member_count)


@blueprint.route('/<template>')
@login_required
def route_template(template):
    members = Members.query.all()  # Get all members
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, members=members, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html', segment='page-404'), 404

    except:
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
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        member_id = request.form.get('member_id')
        if file.filename == '':
            return redirect(request.url)
        if file:
            new_file = PDFFile(filename=file.filename, data=file.read(), member_id=member_id)
            db.session.add(new_file)
            db.session.commit()
            return 'File uploaded successfully!'
    members = Members.query.all()
    return render_template('home/upload_pdf.html', members=members, segment='upload_pdf')


@blueprint.route('/view_pdf/<int:file_id>')
@login_required
def view_pdf(file_id):
    file_data = PDFFile.query.get(file_id)
    return send_file(io.BytesIO(file_data.data), attachment_filename=file_data.filename, as_attachment=False)


@blueprint.route('/download_pdf/<int:file_id>')
@login_required
def download_pdf(file_id):
    file_data = PDFFile.query.get(file_id)
    return send_file(io.BytesIO(file_data.data), attachment_filename=file_data.filename, as_attachment=True)


@blueprint.route('/members')
@login_required
def show_members():
    members = Members.query.all()  # Get all members
    return render_template('home/members.html', members=members, segment='members')


@blueprint.route('/newUser', methods=['GET', 'POST'])
def new_account():
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
    segment = get_segment(request)
    if request.method == 'POST':
        # Récupérer l'utilisateur actuel
        user = Users.query.get(current_user.id)

        # Mettre à jour les informations de l'utilisateur avec les données du formulaire
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

        # Met à jour le mot de passe si un nouveau mot de passe est fourni
        if request.form.get('password'):
            user.set_password(request.form.get('password'))

        # Enregistrer les modifications dans la base de données
        db.session.commit()

        notify(
            BodyText='Profile updated successfully!',
            AppName='Mutuelle FTSL',
            TitleText='Success',
            ImagePath="/static/assets/img/brand/favicon.jpg"
        )

        return render_template('home/settings.html', segment=segment)

    return render_template('home/settings.html', segment=segment)


@blueprint.route('/newMember', methods=['GET', 'POST'])
def add_member():
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


# Helper - Extract the current page name from the request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None
