from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class MemberForm(FlaskForm):
    Name = StringField('Name', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    Location = StringField('Location', validators=[DataRequired()])
    family_situation = StringField('Family Situation', validators=[DataRequired()])
    Occupation = StringField('Occupation', validators=[DataRequired()])
    name_of_children = StringField('Name of Children', validators=[DataRequired()])
    first_name_of_children = StringField('First Name of Children', validators=[DataRequired()])
    