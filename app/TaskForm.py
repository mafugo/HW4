from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    status = SelectField('Status', choices=[('todo', 'To-Do'), ('done', 'Done')], validators=[DataRequired()])
    deadline = DateField('Deadline', format='%Y-%m-%d', validators=[DataRequired()])
    task_type = SelectField('Task Type', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save')
