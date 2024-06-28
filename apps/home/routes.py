# Import necessary modules and models
from datetime import datetime

import httpagentparser
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from toastify import notify

from apps import db
from apps.authentication.models import Users, Members, Children, Parents, Partners, EmergencyContact
from apps.home import blueprint


@blueprint.route('/index')
@login_required
def index():
    users = Users.query.all()  # Get all users
    user_count = Users.query.count()
    member_count = Members.query.count()
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
