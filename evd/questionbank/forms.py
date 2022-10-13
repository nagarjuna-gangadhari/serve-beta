from django import forms
from web.models import Topic, SubTopics


class QuestionForm(forms.Form):
    board = forms.ChoiceField(label='Board', choices=(), required=False, widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    subject = forms.ChoiceField(label='Subject', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    grade = forms.ChoiceField(label='Grade', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    topic = forms.ChoiceField(choices=(), label="Select Topic",widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    subtopic = forms.ChoiceField(choices=(),label="Select Sub Topic", required=False, widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;'}))
    exercise_number = forms.CharField(label='Exercise Number',max_length=16, required=False,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;','required':'required','autocomplete':'off'}))
    question_instruction = forms.CharField(label='Question Instruction',max_length=2048, required=False, widget=forms.Textarea(attrs={'class':'form-control','style':'display:inline !important;margin-bottom:unset;','rows':3}))
    question = forms.CharField(label='Question',max_length=2048, widget=forms.Textarea(attrs={'class':'form-control','style':'display:inline !important;margin-bottom:unset;','rows':3,'required':'required'}))
    question_image = forms.ImageField(label='Image', required=False, widget=forms.ClearableFileInput(attrs={'class':'form-control','style':'display:inline !important;margin-bottom:unset;'}))
    question_type = forms.ChoiceField(label='Question Type',choices=(("DirectAnswer","Direct Answer"),("MCQs","Multiple Choice"),("True/False","True/False"),("Others","Others")),widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    question_type_science = forms.ChoiceField(label='Question Type',choices=(("Fill in the blanks","Fill in the blanks"),("MCQs","Choose the correct answer"),("True/False","True/False"),("Correct the following statements","Correct the following statements"),("Clue based question","Clue based question"),("Name the picture","Name the picture"),("Give one word for","Give one word for"),("Analogy","Analogy"),
    ("One line answer","One line answer"),("Picture based questions","Picture based questions"),("Give reasons ","Give reasons "),("Draw a diagram","Draw a diagram"),("Define","Define"),("Answer in brief","Answer in brief")),
    widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    question_type_maths = forms.ChoiceField(label='Question Type',choices=(("Simplify","Simplify"),("MCQs","Choose the correct answer"),("MCQs","Multiple Choice"),("Fill in the blanks","Fill in the blanks"),("Find the value of","Find the value of"),("Solve the following","Solve the following"),("Measure the angle","Measure the angle"),
    ("Draw the following","Draw the following"),("Compare the following","Compare the following"),("Do as directed","Do as directed"),("Match the following","Match the following"),("True/False","State true/false"),("Define the following","Define the following"),("Prove the theorem","Prove the theorem"),("Write the formula","Write the formula"),
    ("Calculate","Calculate"),(" Graph work- representation of data"," Graph work- representation of data"),("Geometric constructions","Geometric constructions"),("Statement problem","Statement problem")
    ),widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    difficulty_level = forms.ChoiceField(label='Difficulty Level',choices=(("Hard","Hard"),("Medium","Medium"),("Easy","Easy")), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    answer_question = forms.CharField(label='Choices',max_length=2048, required=False, widget=forms.Textarea(attrs={'class':'form-control','style':'display:inline !important;margin-bottom:unset;','rows':3}))
    correct_answer = forms.CharField(label='Answer',max_length=512, widget=forms.Textarea(attrs={'class':'form-control','style':'display:inline !important;margin-bottom:unset;','rows':3,'required':'required'}))
    solution = forms.CharField(label='Solution',max_length=2048, required=False, widget=forms.Textarea(attrs={'class':'form-control','style':'display:inline !important;margin-bottom:unset;','rows':3}))
    is_deleted = forms.ChoiceField(label='Is Deleted', choices=(('False', 'False'),('True', 'True')), required=False,widget=forms.Select(attrs={'class': 'form-control','style': 'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;'}))


def get_question_data(question):
    question_dict = {}
    question_dict['board'] = question.board
    question_dict['subject'] = question.subject
    question_dict['grade'] = question.grade
    question_dict['topic'] = question.topic_id
    question_dict['subtopic'] = question.subtopic_id
    question_dict['exercise_number'] = question.exercise_number
    question_dict['question_instruction'] = question.question_instruction
    question_dict['question'] = question.question
    question_dict['question_image'] = question.question_image
    if question.subject == "Maths":
        question_dict['question_type_maths'] = question.question_type
    elif question.subject == "Science":
        question_dict['question_type_science'] = question.question_type
    else:
        question_dict['question_type'] = question.question_type
    question_dict['difficulty_level'] = question.difficulty_level
    question_dict['answer_question'] = question.answer_question
    question_dict['correct_answer'] = question.correct_answer
    question_dict['solution'] = question.solution
    return question_dict

class HolidaysForm(forms.Form):
    board = forms.ChoiceField(label='Board', choices=(), required=False, widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    academic = forms.ChoiceField(label='Academic Year', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    calender = forms.ChoiceField(label='Calender', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    district = forms.ChoiceField(label='District', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;'}))
    center = forms.ChoiceField(label='Center', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;'}))


class Add_HolidaysForm(forms.Form):
    board = forms.ChoiceField(label='Boards', choices=(), required=False, widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    district = forms.ChoiceField(label='District', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    center = forms.ChoiceField(label='Center', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;margin-left:13px','required':'required'}))
    launch_date = forms.DateField(label='Date',required=False,widget=forms.DateInput(format=('%Y-%m-%d'),attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;margin-left: 66px;','type':'Date'}))
    description = forms.CharField(label="Description",max_length=2048,widget=forms.Textarea(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:-32px;margin-left:37px;','rows':2}))
   
    academic = forms.ChoiceField(label='Academic Year', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    calender = forms.ChoiceField(label='Calender', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))


class Apply_HolidaysForm(forms.Form):
    board = forms.ChoiceField(label='Board', choices=(), required=False, widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    academic = forms.ChoiceField(label='Academic Year', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    calender = forms.ChoiceField(label='Calender', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    district = forms.ChoiceField(label='District', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    center = forms.ChoiceField(label='Center', choices=(), widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
    offering = forms.ChoiceField(label='Offering', choices=(), required=False, widget=forms.Select(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;','required':'required'}))
