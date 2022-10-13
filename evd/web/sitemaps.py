from django.contrib.sitemaps import Sitemap
from web.models import UserProfile

class websitemap(Sitemap):
    
    def items(self):
        return UserProfile.objects.all()
    
    def location(self, item):
         return None
    
    def lastmod(self, obj):
        return obj.from_date
    
"""class staticviewSitemap(Sitemap):
    
    def items(self):
        return ['']
    
    def location(self,item):
        return reverse(item)"""