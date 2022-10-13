from django.db import models
from web.models import Topic, SubTopics, ContentDetail
from django.contrib.auth.models import User


class QuestionType(models.Model):
    name = models.CharField(max_length=64, null=True)
    instructions = models.CharField(max_length=128)
    code =  models.CharField(max_length=255,null=False)


class Question_Type(models.Model):
    name = models.CharField(max_length=64, null=True)
    instructions = models.CharField(max_length=512,null=True)
    code =  models.CharField(max_length=50,null=False,default="mcq")
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, null=True, related_name='qtype_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='qtype_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = ('Question Type')


class Question_Set(models.Model):
    name = models.CharField(max_length=128, null=True)
    topic = models.ForeignKey(Topic, null=True, related_name="qset_topic")
    subtopic = models.ForeignKey(SubTopics, null=True, related_name='qset_subtopic_id')
    status = models.IntegerField(choices=((1, 'Active'), (2, 'Inactive'),(3, 'Pending'),(4, 'Inactive')), default=1)
    type = models.IntegerField(choices=((1, 'Practice Set'), (2, 'Quiz')), default=1)
    created_by = models.ForeignKey(User, null=True, related_name='qset_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='qset_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    content_detail = models.ForeignKey(ContentDetail, null=True, related_name="qset_content_detail_id")
    duration = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = ('Question Set')


class Question(models.Model):
    title = models.CharField(max_length=512,null=True,blank=True)
    text = models.CharField(max_length=2048,null=True, blank=True)
    status = models.CharField(max_length=32,choices=(("1", 'Active'), ("2", 'Inactive')),default="1")
    questionset = models.ForeignKey(Question_Set,null=False,related_name='qts_question_set')
    topic = models.ForeignKey(Topic, null=True, related_name="qts_topic")
    subtopic = models.ForeignKey(SubTopics, null=True,related_name='qts_subtopic_id')
    type = models.ForeignKey(Question_Type, null=False, related_name="qts_question_type")
    type_code = models.CharField(max_length=50)
    hint = models.CharField(max_length=512)
    complexity = models.IntegerField(choices=((1, 'Easy'), (2, 'Medium'),(3, 'Advanced')), default=1)
    points = models.IntegerField(default=0, null=True)
    created_by = models.ForeignKey(User, null=True, related_name='qts_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='qts_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    sequence = models.IntegerField(default=1)
    actual_sequence_string = models.CharField(max_length=256,null=True)
    learning_outcome = models.CharField(max_length=1024, null=True)
    def __unicode__(self):
        return self.text

    class Meta:
        verbose_name = ('Question')

class Question_Component(models.Model):
    text = models.CharField(max_length=1024)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    status = models.IntegerField(choices=((1, 'Active'), (2, 'Inactive')),default=1)
    question = models.ForeignKey(Question, null=False, related_name="qcmp_parent_question")
    subtype = models.CharField(max_length=50, choices=(('1', 'MCQ option'), ('2', 'Left Column Item'), ('3', 'Right Column Item'),('4', 'Category'),('5', 'Category Item'),('6', 'Order option')),default="1")
    is_answer = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, related_name='qcmp_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='qcmp_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    style_attributes_json = models.CharField(max_length=1024)
    sequence = models.IntegerField(default=1)
    matching_component = models.ForeignKey('self', null=True, related_name="qcmp_parent_component", blank=True)

    def __unicode__(self):
        return self.text

    class Meta:
        verbose_name = ('Question Component')


