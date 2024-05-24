from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class CreateMember(FlaskForm):
    Name = StringField('Name',
                       id='name', 
                           validators=[DataRequired()])
    family_situation = StringField('Family Situation',
                                   id='family_situation',
                                   validators=[DataRequired()])
    Occupation = StringField('Occupation',
                             id='occupation',
                             validators=[DataRequired()])
    name_of_children = StringField('Name of Children',
                                   id='name_of_children',
                                   validators=[DataRequired()])
    first_name_of_children = StringField('First Name of Children',
                                         id='first_name_of_children',
                                         validators=[DataRequired()])
    name_of_parents = StringField('Name of Parents',
                                  id='name_of_parents',
                                  validators=[DataRequired()])
    first_name_of_parents = StringField('First Name of Parents',
                                        id='first_name_of_parents',
                                        validators=[DataRequired()])
    mobile_number = StringField('Mobile number',
                                id='mobile_number',
                                validators=[DataRequired()])
