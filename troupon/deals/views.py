from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, View
from django.http import HttpResponse, Http404
from django.template import Engine, RequestContext
from django.core.paginator import Paginator
from django.core.context_processors import csrf

from deals.models import Deal, STATE_CHOICES

import cloudinary


# Create your views here.
class HomePage(View):
    """class that handles display of the homepage"""

    def get(self, request, *args, **kwargs):

        featured_deals = []

        latest_deals = []

        deals_page = Paginator(latest_deals, 10, orphans=2).page(1)
        
        description = "Check out the newest and hottest deals from all your favourite brands:"
        if not deals_page.paginator.count:
            description = "Sorry, no deals found!"

        deals_listing =  {
            'deals_page': deals_page,
            'date_filter': { 
                'choices': [
                    (7, "Last 7 Days"),
                    (14, "2 Weeks"),
                    (30, "1 Month"),
                    (0, "Show All"),
                ],
                'default': 0
            },
            'title': "latest deals",
            'description': description,
            'base_url': reverse('homepage'),
        }

        context = {
            # 'show_subscribe': True,
            'states': { 'choices': STATE_CHOICES,  'default': 25 },
            'popular_categories': [
                'Get Aways',
                'Fashion & Lifestyle',
                'Electronics',
                'Food',
                'Travel & Get Aways',
                'Fashion',
                'Electronics',
                'Food',
                'Travel',
                'Fashion',
                'Electronics',
                'Food',
            ],
            'featured_deals': featured_deals,
            'deals_listing': deals_listing,
        }

        context.update(csrf(request))
        return render(request, 'deals/index.html', context)


class DealView(View):
    """This handles request for each deal by id.
    """

    def get(self, *args, **kwargs):
        deal_id = self.kwargs.get('deal_id')  # get deal_id from request
        if not deal_id:
            deals = Deal.objects.all()
            engine = Engine.get_default()
            template = engine.get_template('deals/list.html')
            context = RequestContext(self.request, {'deals': deals})
            return HttpResponse(template.render(context))
        try:
            deal = Deal.objects.get(id=deal_id)
            deal = {'deal': deal}
        except Deal.DoesNotExist:
            raise Http404('Deal does not exist')

        # Replace template object compiled from template code
        # with an application template.
        # Use Engine.get_template(template_name)
        engine = Engine.get_default()
        template = engine.get_template('deals/detail.html')

        # set result in RequestContext
        context = RequestContext(self.request, deal)
        return HttpResponse(template.render(context))

    def post(self, request):
        """This handles creation of deals
        """
        try:
            deal = Deal(request.POST)
            response = self.upload(request.FILES, request.POST.get('title'))
            deal.photo_url = response.get('public_url')
            deal.save()
            return redirect('/deals/{0}/'.format(deal.id))
        except:
            return redirect('/deals/')

    def upload(self, file, title):
        return cloudinary.uploader.upload(
                file,
                public_id=title
            )
