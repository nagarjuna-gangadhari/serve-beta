class AllFieldsModelAdminMixin(object):

    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        super(AllFieldsModelAdminMixin, self).__init__(model, admin_site)